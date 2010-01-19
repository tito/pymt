from pymt import *

c = '''label {
    draw-background: 1;
    bg-color: rgb(0,0,255,120);
}'''
css_add_sheet(c)

m = MTWidget()

l = MTLabel(label='Label1: PLOP Woooooooooooooooot !', font_size=24, autowidth=True, autoheight=True, pos=(200, 400))
m.add_widget(l)

l2 = MTLabel(label='Label2: Mwhahahaha\nLabel2: :)', pos=(200, 300), autowidth=True, autoheight=True)
print l2.size
m.add_widget(l2)

@m.event
def on_draw():
    w, h = drawLabel(label='Plop', pos=(100, 200), center=False)
    set_color(1,0,0,.2)
    drawRectangle(pos=(100, 200), size=(w,h))

class MTLabelBoundingBox(MTLabel):
    def draw(self):
        set_color(1, 0, 0, 0.5)
        drawRectangle(self.pos, self.size)
        MTLabel.draw(self)

l = MTLabelBoundingBox(label='This is a rather long foobar')
l.pos = (20, 40)
m.add_widget(l)


runTouchApp(m)
