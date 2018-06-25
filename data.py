import itertools
from midi_to_statematrix import upperBound, lowerBound

def startSentinel():
    def noteSentinel(note):
        # input number for note in range of lowerBound to upperBound 
        position = note
        part_position = [position]
        
        pitchclass = (note + lowerBound) % 12 # 12 notes in an octave including naturals and sharps/flats
        part_pitchclass = [int(i == pitchclass) for i in range(12)] # only keeps track of whether a pitch has been played or not
        
        return part_position + part_pitchclass + [0]*66 + [1] # length will be 80, figure out why
    return [noteSentinel(note) for note in range(upperBound-lowerBound)] 

# l is state, i is a value to move up or down from current note, d is note that gets returned if there is no index i in l
def getOrDefault(l, i, d):
    try:
        return l[i]
    except IndexError:
        return d

# buildContext notes:
# context counts how many of each pitch class in the file
# state is a list of 1x2 lists, list of notestates, stores "memory" of previous note 
# notestate is a 1x2 list that indicates whether the previous note was played or articulated

def buildContext(state):
    context = [0]*12 # initialize octave values with all 0
    for note, notestate in enumerate(state):
        if notestate[0] == 1:
            pitchclass = (note + lowerBound) % 12
            context[pitchclass] += 1
    return context

# determines value for each type of note (half notes, quarter notes, etc) based on time (tempo)
def buildBeat(time):
    return [2*x-1 for x in [time%2, (time//2)%2, (time//4)%2, (time//8)%2]]

# beat is output of buildBeat
# returns input for final model
def noteInputForm(note, state, context, beat):
    position = note
    part_position = [position]

    pitchclass = (note + lowerBound) % 12
    part_pitchclass = [int(i == pitchclass) for i in range(12)]
    # Concatenate the note states for the previous vicinity
    part_prev_vicinity = list(itertools.chain.from_iterable((getOrDefault(state, note+i, [0,0]) for i in range(-12, 13))))

    part_context = context[pitchclass:] + context[:pitchclass]

    return part_position + part_pitchclass + part_prev_vicinity + part_context + beat + [0]

def noteStateSingleToInputForm(state,time):
    beat = buildBeat(time)
    context = buildContext(state)
    return [noteInputForm(note, state, context, beat) for note in range(len(state))]

def noteStateMatrixToInputForm(statematrix):
    # NOTE: May have to transpose this or transform it in some way to make Theano like it
    #[startSentinel()] + 
    inputform = [ noteStateSingleToInputForm(state,time) for time,state in enumerate(statematrix) ]
    return inputform
