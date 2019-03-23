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


CLEF = "treble" #determine what clef
if CLEF == "treble":
    clef_img = "treble_clef.jpg"
else:
    clef_img = "bass_clef.jpg"

c = canvas.Canvas("Music.pdf", pagesize=letter)



title(c)

count = 0

#first page
draw_clefs(c, 50, 641, 10)

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

