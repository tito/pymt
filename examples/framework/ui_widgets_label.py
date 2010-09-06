from pymt import *

# for our example, force drawing of background for all label
c = '''label {
    draw-background: 1;
    bg-color: rgb(0,0,255,120);
}'''
css_add_sheet(c)

# add all the label to the window
m = getWindow()

# testing autowidth/autoheight
l = MTLabel(label='Label1: PLOP Woooooooooooooooot !', font_size=24, autowidth=True, autoheight=True, pos=(200, 400))
m.add_widget(l)

# testing multiline with autowidth/autoheight
l2 = MTLabel(label='Label2: Mwhahahaha\nLabel2: :)', pos=(200, 300), autowidth=True, autoheight=True)
m.add_widget(l2)

# testing multiline + padding + align
l3 = MTLabel(label='Plop\nworld', pos=(200, 200), autosize=True, padding=10)
l4 = MTLabel(label='Plop\nworld', pos=(300, 200), autosize=True, padding=10, halign='center')
l5 = MTLabel(label='Plop\nworld', pos=(400, 200), autosize=True, padding=10, halign='right')
m.add_widget(l3)
m.add_widget(l4)
m.add_widget(l5)

runTouchApp()
