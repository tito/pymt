import random
from pymt import *

if __name__ == '__main__':

    #create a box layout with 5 buttons, and put it into a Anchor layout so its layed out in center
    box = MTBoxLayout(animation_type='ease_in_out_elastic')
    for i in range(6):
        box.add_widget( MTButton(label="Button "+str(i)) )
    anchor = MTAnchorLayout(animation_type='ease_in_out_elastic', animation_time=0.5)
    anchor.add_widget(box)
    
    #add a label at the top center (with some padding)
    label_anchor = MTAnchorLayout(anchor_y='top', padding=200)
    label = MTLabel(label="Welcome to Layout FUN!", anchor_x='center', align='center', font_size=32) 
    label_anchor.add_widget(label)

    #put teh two layouts into a stretch layout, so they fill the whole window (since stretch is put as root)
    stretch = MTStretchLayout()
    stretch.add_widget(anchor)
    stretch.add_widget(label_anchor)

    #simple function to change the layout of teh box and its anchor layouts randomly every 5 seconds
    def change(dt):
        anchor.anchor_x = random.choice(['left', 'right', 'center'])
        anchor.anchor_y = random.choice(['top', 'bottom', 'center'])
        box.orientation = random.choice(['horizontal', 'vertical'])
        label.label = "Anchor: '%s,%s'. | Box: '%s'" %(anchor.anchor_y, anchor.anchor_x, box.orientation)
    getClock().schedule_interval(change, 5)
    
    runTouchApp(stretch)

