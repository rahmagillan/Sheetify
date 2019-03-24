from aubio import source, tempo, pitch, notes
from numpy import median, diff

################################################################################################ tempo

print("Welcome to Sheetify!")
print(
    '''
|___|)________________________________________________________
|___/____________________________|___________________________||
|__/|_______/|____/|_____/|______|___________________________||
|_/(|,\____/_|___/_|____/_|______|___________________________||
|_\_|_/___|__|__|__|___|__|___|__|___________________________||
|   |     | ()  | ()   | ()   |  |                           ||
| (_|   -()-  -()-   -()-   -()- | -()-  -()-  -()-   -()-   ||
|________________________________|__|__()_|__()_|__()__|_____||
|__/___\_._______________________|__|__|__|__|__|__|___|_____||
|__\___|.________________________|___\_|___\_|___\_|___|_____||
|_____/__________________________|____\|____\|____\|_________||
|____/___________________________|___________________________|| 
'''
)
file = input("Enter path of .wav file: ")

file.replace("\\","\\\\")

def get_file_bpm(path, params=None):
    """ Calculate the beats per minute (bpm) of a given file.
        path: path to the file
        param: dictionary of parameters
    """
    if params is None:
        params = {}
    try:
        win_s = params['win_s']
        samplerate = params['samplerate']
        hop_s = params['hop_s']
    except KeyError:
        """
        # super fast
        samplerate, win_s, hop_s = 4000, 128, 64 
        # fast
        samplerate, win_s, hop_s = 8000, 512, 128
        """
        # default:
        samplerate, win_s, hop_s = 44100, 1024, 512

    s = source(path, samplerate, hop_s)
    samplerate = s.samplerate
    o = tempo("specdiff", win_s, hop_s, samplerate)
    # List of beats, in samples
    beats = []
    # Total number of frames read
    total_frames = 0

    while True:
        samples, read = s()
        is_beat = o(samples)
        if is_beat:
            this_beat = o.get_last_s()
            beats.append(this_beat)
            # if o.get_confidence() > .2 and len(beats) > 2.:
            #    break
        total_frames += read
        if read < hop_s:
            break

    # Convert to periods and to bpm
    if len(beats) > 1:
        #if len(beats) < 4:
            #print("few beats found in {:s}".format(path))
        bpms = 60. / diff(beats)
        b = median(bpms)
    else:
        b = 0
        #print("not enough beats found in {:s}".format(path))
    return b

bpm = get_file_bpm(file) /2
#print(bpm)

#################################################################################### pitch

downsample = 1
samplerate = 44100 // downsample
#if len( sys.argv ) > 2: samplerate = int(sys.argv[2])

win_s = 4096 // downsample # fft size
hop_s = 64 // downsample # hop size

s = source(file, samplerate, hop_s)
samplerate = s.samplerate

tolerance = 0.8

pitch_o = pitch("yin", win_s, hop_s, samplerate)
pitch_o.set_unit("midi")
pitch_o.set_tolerance(tolerance)

pitches = []
confidences = []

# total number of frames read
total_frames = 0


eighthNoteLen = 1/(bpm/60*2)
#print(eighthNoteLen)

midiNotes = []
noteLengths = []
startTime = 1.0
while True:
    samples, read = s()
    pitch = pitch_o(samples)[0]
    #pitch = int(round(pitch))
    confidence = pitch_o.get_confidence()
    #if confidence < 0.8: pitch = 0.
    #print("%f %f %f" % (total_frames / float(samplerate), pitch, confidence))

    pitches += [pitch]
    confidences += [confidence]
    total_frames += read

    wholePitch = int(round(pitch))  # pitch rounded to whole number

    #print("%d %f" %(wholePitch,total_frames / float(samplerate)))


    # if list is empty
    if len(midiNotes) == 0:
        midiNotes.append(wholePitch)
        startTime = total_frames / float(samplerate)
    # if list is not empty and changes note
    elif midiNotes[-1] != wholePitch:
        noteLengths.append(total_frames / float(samplerate)-startTime)
        midiNotes.append(wholePitch)
        startTime = total_frames / float(samplerate)

    if read < hop_s:
        noteLengths.append(total_frames / float(samplerate) - startTime)
        break


#print(midiNotes)
#print(noteLengths)

pitches = []
lengths = []
for i in range (len(midiNotes)):
    if noteLengths[i]>eighthNoteLen:
        pitches.append(midiNotes[i])
        lengths.append(int(round(noteLengths[i]/eighthNoteLen))*.5)

#print(pitches)
#print(lengths)

if 0: sys.exit(0)

##########################################################################################################################################################
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image

#canvas size: pagesize=(595.27,841.89)
#canvas size: pagesize=(612,792)
#50 pixel margin


def title(c):
    c.setFont("Helvetica", 16)
    c.drawCentredString(612/2,742,"Sheet Music")


def staff_lines(c, n):
    for i in range(5):
        c.line(50, n-i*7, 562, n-i*7)


def new_page(c, n):
    for i in range(5):
        c.line(50, n-i*7, 562, n-i*7)


def draw_clefs(c,x,y,num):
    for i in range(num):
        if (CLEF == "treble"):
            c.drawImage(clef_img, x, y-i*65,width=31,height=53)
        elif (CLEF == "bass"):
            c.drawImage(clef_img, x+5, (y+17) - i * 65, width=23, height=24)

def draw_note(c, pitch, length, x, y):
    if pitch == 0: #if rest
        if length == 0.5:
            c.drawImage("eigth_rest.jpg",x,y,width=EIGHTH_REST_W,height=EIGHTH_REST_L)
        elif length == 1:
            c.drawImage("quarter_rest.jpg", x, y, width=QUARTER_REST_W, height=QUARTER_REST_L)
        elif length == 2:
            c.drawImage("half_rest.jpg", x, y, width=HALF_REST_W, height=HALF_REST_L)
        elif length == 4:
            c.drawImage("whole_rest.jpg", x, y, width=WHOLE_REST_W, height=WHOLE_REST_L)
    #notes
    elif length == 0.5:
        if flipped(pitch) == True:
            c.drawImage("eigth_up.jpg", x, y, width=EIGHT_NOTE_UP_W, height=EIGHT_NOTE_UP_L)
        else:
            c.drawImage("eigth.jpg", x, y, width=EIGHT_NOTE_W, height=EIGHT_NOTE_L)

        if ledger_line(pitch) == True:
            for i in range (num_ledger(pitch)):
                if ledger_above(pitch) == True:
                    c.line(x - 3, y + 7 / 2+i*7, x + EIGHT_NOTE_W + 3, y + 7 / 2+i*7)
                else:
                    c.line(x - 3, y + 7 / 2+i*7, x + EIGHT_NOTE_W + 3, y + 7 / 2+i*7)

    elif length == 1:
        if flipped(pitch) == True:
            c.drawImage("quarter_up.jpg", x, y, width=QUARTER_NOTE_UP_W, height=QUARTER_NOTE_UP_L)
        else:
            c.drawImage("quarter.jpg", x, y, width=QUARTER_NOTE_W, height=QUARTER_NOTE_L)

        if ledger_line(pitch) == True:
            for i in range (num_ledger(pitch)):
                if ledger_above(pitch) == True:
                    c.line(x - 3, y + 7 / 2+i*7, x + QUARTER_NOTE_W + 3, y + 7 / 2+i*7)
                else:
                    c.line(x - 3, y + 7 / 2+i*7, x + QUARTER_NOTE_W + 3, y + 7 / 2+i*7)

    elif length == 1.5:
        if flipped(pitch) == True:
            c.drawImage("quarter_up.jpg", x, y, width=QUARTER_NOTE_UP_W, height=QUARTER_NOTE_UP_L)
            c.circle(x + QUARTER_NOTE_W + 3, y + 7 / 2, 1, stroke=1, fill=1)
        else:
            c.drawImage("quarter.jpg", x, y, width=QUARTER_NOTE_W, height=QUARTER_NOTE_L)
            c.circle(x + QUARTER_NOTE_W + 3, y + 7 / 2, 1, stroke=1, fill=1)

        if ledger_line(pitch) == True:
            for i in range (num_ledger(pitch)):
                if ledger_above(pitch) == True:
                    c.line(x - 3, y + 7 / 2+i*7, x + QUARTER_NOTE_W + 3, y + 7 / 2+i*7)
                else:
                    c.line(x - 3, y + 7 / 2+i*7, x + QUARTER_NOTE_W + 3, y + 7 / 2+i*7)

    elif length == 2:
        if flipped(pitch) == True:
            c.drawImage("half_up.jpg", x, y, width=HALF_NOTE_UP_W, height=HALF_NOTE_UP_L)
        else:
            c.drawImage("half.jpg", x, y, width=HALF_NOTE_W, height=HALF_NOTE_L)

        if ledger_line(pitch) == True:
            for i in range (num_ledger(pitch)):
                if ledger_above(pitch) == True:
                    c.line(x - 3, y + 7 / 2+i*7, x + HALF_NOTE_W + 3 , y + 7 / 2+i*7)
                else:
                    c.line(x - 3, y + 7 / 2+i*7, x + HALF_NOTE_W + 3, y + 7 / 2+i*7)

    elif length == 3:
        if flipped(pitch) == True:
            c.drawImage("quarter_up.jpg", x, y, width=HALF_NOTE_W, height=HALF_NOTE_L)
            c.circle(x + HALF_NOTE_W + 3, y + 7 / 2, 1, stroke=1, fill=1)
        else:
            c.drawImage("quarter.jpg", x, y, width=HALF_NOTE_W, height=HALF_NOTE_L)
            c.circle(x + HALF_NOTE_W + 3, y + 7 / 2, 1, stroke=1, fill=1)

        if ledger_line(pitch) == True:
            for i in range (num_ledger(pitch)):
                if ledger_above(pitch) == True:
                    c.line(x - 3, y + 7 / 2+i*7, x + HALF_NOTE_W + 3, y + 7 / 2+i*7)
                else:
                    c.line(x - 3, y + 7 / 2+i*7, x + HALF_NOTE_W + 3, y + 7 / 2+i*7)

    elif length == 4:
        c.drawImage("whole.jpg",x,y, width=WHOLE_NOTE_W, height=WHOLE_NOTE_L)

        if ledger_line(pitch) == True:
            for i in range (num_ledger(pitch)):
                if ledger_above(pitch) == True:
                    c.line(x - 3, y + 7 / 2+i*7, x + WHOLE_NOTE_W + 3, y + 7 / 2+i*7)
                else:
                    c.line(x - 3, y + 7 / 2+i*7, x + WHOLE_NOTE_W + 3, y + 7 / 2+i*7)

def flipped(pitch):
    #treble
    if(21 <= pitch <= 50):
        return False
    elif(51 <= pitch <= 59):
        return True
    elif (60 <= pitch <= 71): #C (60) flips based on if its treble or bass clef
        return False
    elif(71 <= pitch <= 108):
        return True


def note_width(pitch,length):
    if pitch == 0: #if rest
        if length == 0.5:
            return EIGHTH_REST_W
        elif length == 1:
            return QUARTER_REST_W
        elif length == 2:
            return HALF_REST_W
        elif length == 4:
            return WHOLE_REST_W
    elif length == 0.5:
        if flipped(pitch) == True:
            return EIGHT_NOTE_UP_W
        else:
            return EIGHT_NOTE_W
    elif length == 1:
        if flipped(pitch) == True:
            return QUARTER_NOTE_UP_W
        else:
            return QUARTER_NOTE_W
    elif length == 1.5:
        return DOTQUARTER_NOTE_W
    elif length == 2:
        if flipped(pitch) == True:
            return HALF_NOTE_UP_W
        else:
            return HALF_NOTE_W
    elif length == 3:
        return DOTHALF_NOTE_W
    elif length == 4:
        return WHOLE_NOTE_W
    else:
        return 0


def relative_note_location(pitch, length):
    if pitch == 0:
        if length == 0.5:
            return 7
        elif length == 1:
            return 7/2
        elif length == 2:
            return 21/2 + 3.5
        elif length == 4:
            return 14 + 3.5
    #lines
    elif pitch == 64 or pitch == 43:
        return -7/2
    elif pitch == 67 or pitch == 47:
        return 7/2
    elif pitch == 71 or pitch == 50:
        return 9/2
    elif pitch == 74 or pitch == 53:
        return 11/2
    elif pitch == 77 or pitch == 57:
        return 13/2
    elif pitch == 60:
        return -7/2 - 7
    #spaces
    elif pitch == 65 or pitch == 45:
        return 0
    elif pitch == 69 or pitch == 48:
        return 7
    elif pitch == 72 or pitch == 52:
        return 14
    elif pitch == 76 or pitch == 55:
        return 21
    elif pitch == 62 or pitch == 59:
        return -7
    else:
        return 0


def ledger_line(pitch):
    if 21 <= pitch <= 40 or 81 <= pitch <= 108 or pitch == 60:
        return True
    else:
        return False


def ledger_above(pitch):
    if CLEF == "treble":
        if 81 <= pitch <= 108:
            return True
        else:
            return False
    else:
        if pitch == 60:
            return True
        else:
            return False


def num_ledger(pitch):
    if 81 <= pitch <= 83 or pitch == 60 or 38 <= pitch <= 40:
        return 1
    elif 84 <= pitch <= 86 or 34 <= pitch <= 37:
        return 2
    elif 87 <= pitch <= 90 or 31 <= pitch <= 33:
        return 3
    elif 91 <= pitch <= 93 or 27 <= pitch <= 30:
        return 4
    elif 94 <= pitch <= 97 or 24 <= pitch <= 26:
        return 5

CLEF = "treble" #determine what clef
if CLEF == "treble":
    clef_img = "treble_clef.jpg"
else:
    clef_img = "bass_clef.jpg"

c = canvas.Canvas("Music.pdf", pagesize=letter)
title(c)

###



EIGHTH_REST_L = 14
EIGHTH_REST_W = 14
QUARTER_REST_L = 21
QUARTER_REST_W = 7
HALF_REST_L = 7/2
HALF_REST_W = 21
WHOLE_REST_L = 7/2
WHOLE_REST_W = 21

EIGHT_NOTE_L = 28
EIGHT_NOTE_W = 15
EIGHT_NOTE_UP_L =28
EIGHT_NOTE_UP_W = 10
QUARTER_NOTE_L = 28
QUARTER_NOTE_W = 10
QUARTER_NOTE_UP_L = 28
QUARTER_NOTE_UP_W = 10
DOTQUARTER_NOTE_L = 28
DOTQUARTER_NOTE_W = 15
HALF_NOTE_L = 28
HALF_NOTE_W = 10
HALF_NOTE_UP_L = 28
HALF_NOTE_UP_W = 10
DOTHALF_NOTE_L = 28
DOTHALF_NOTE_W = 15
WHOLE_NOTE_L = 8
WHOLE_NOTE_W = 12



###

#first page
count = 0
draw_clefs(c, 50, 641, 10)
c.drawImage("time_signatures.jpg", 85, 654,width=11.2,height=28) #time signature @ 85

#draw notes

limit = 592
running_width = 0
counter = 0
i_counter = 0
for i in range(len(pitches)):
    running_width += note_width(pitches[i], lengths[i])
    if running_width + 100+running_width+i_counter*50*0.75 <= limit:
        draw_note(c, pitches[i],lengths[i],100+running_width+i_counter*50*0.75,653+relative_note_location(pitches[i],lengths[i])- counter*65)
        i_counter += 1
    else:
        draw_note(c, pitches[i], lengths[i], 100+running_width +i_counter*50*0.75, 653 + relative_note_location(pitches[i], lengths[i]) - counter*65)
        running_width = 0
        i_counter = 0
        counter += 1

#draw staff
while True:
    loc = 672

    if loc - count*65 > 80:
        staff_lines(c, 682 - count*65)
    else:
        count = 0
        break

    count += 1

#every other page
c.showPage()

numPages = 3
for i in range(numPages):
    draw_clefs(c, 50, 701, 11)
    count = 0
    while True:
        loc = 672

        if loc - count * 65 > 0:
            new_page(c, 742 - count * 65)
        else:
            count = 0
            break

        count += 1

    c.showPage()


c.save()

'''
def hello(c):
    c.drawString(100,100,"Hello World")


c = canvas.Canvas("hello.pdf")
hello(c)
c.showPage()
c.save()
'''
