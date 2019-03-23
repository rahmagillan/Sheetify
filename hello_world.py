from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

#canvas size: pagesize=(595.27,841.89)
#canvas size: pagesize=(612,792)
#50 pixel margin


def title(c):
    c.setFont("Helvetica", 16)
    c.drawCentredString(612/2,742,"Sheet Music")


def staff_lines(c, n):
    for i in range(5):
        c.line(50, n-i*7, 562, n-i*7)


#def new_page(c):


c = canvas.Canvas("Music.pdf", pagesize=letter)

title(c)
count = 0

#first page
while True:
    loc = 672

    if loc - count*65 > 80:
        staff_lines(c, 682 - count*65)
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

