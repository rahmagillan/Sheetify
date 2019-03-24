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
    elif length == 0.5:
        if flipped(pitch) == True:
            c.drawImage("eigth_up.jpg", x, y, width=EIGHT_NOTE_UP_W, height=EIGHT_NOTE_UP_L)
        else:
            c.drawImage("eigth.jpg", x, y, width=EIGHT_NOTE_W, height=EIGHT_NOTE_L)
    elif length == 1:
        if flipped(pitch) == True:
            c.drawImage("quarter_up.jpg", x, y, width=QUARTER_NOTE_UP_W, height=QUARTER_NOTE_UP_L)
        else:
            c.drawImage("quarter.jpg", x, y, width=QUARTER_NOTE_W, height=QUARTER_NOTE_L)
    elif length == 2:
        if flipped(pitch) == True:
            c.drawImage("half_up.jpg", x, y, width=HALF_NOTE_UP_W, height=HALF_NOTE_UP_L)
        else:
            c.drawImage("half.jpg", x, y, width=HALF_NOTE_W, height=HALF_NOTE_L)
    elif length == 4:
        c.drawImage("whole.jpg",x,y, width=WHOLE_NOTE_W, height=WHOLE_NOTE_L)


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
    elif length == 2:
        if flipped(pitch) == True:
            return HALF_NOTE_UP_W
        else:
            return HALF_NOTE_W
    elif length == 4:
        return WHOLE_NOTE_W

#def relative_note_location(pitch):



CLEF = "treble" #determine what clef
if CLEF == "treble":
    clef_img = "treble_clef.jpg"
else:
    clef_img = "bass_clef.jpg"

c = canvas.Canvas("Music.pdf", pagesize=letter)
title(c)

###


pitches = [0,65,74,0,65,74,0,65,74,0,65,74,]
lengths = [0.5,0.5,0.5,1,1,1,2,2,2,4,4,4]

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
HALF_NOTE_L = 28
HALF_NOTE_W = 10
HALF_NOTE_UP_L = 28
HALF_NOTE_UP_W = 10
WHOLE_NOTE_L = 7
WHOLE_NOTE_W = 12



###

#first page
count = 0
draw_clefs(c, 50, 641, 10)
c.drawImage("time_signatures.jpg", 85, 654,width=11.2,height=28) #time signature @ 85

#draw notes
running_width = 0
for i in range(len(pitches)):
    running_width += note_width(pitches[i],lengths[i])
    draw_note(c, pitches[i],lengths[i],100+running_width+i*10,654)

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

