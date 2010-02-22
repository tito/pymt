import random
from pymt import *




def set_screen(id, *ev_args):
    getWidgetByID('screens').select(id)

def anchor_test():
    #create a box layout with 5 buttons, and put it into a Anchor layout so its layed out in center
    box = MTBoxLayout(orientation='horizontal')
    for i in range(3):
        b =  MTButton(label="next screen")
        b.push_handlers( on_press=curry(set_screen, 'size hint') )
        box.add_widget(b)
    anchor = MTAnchorLayout(anchor_x="right", animation_type='ease_in_out_elastic', animation_time=0.5)
    anchor.add_widget(box)
        
    #add a button at the top center (with some padding), to change the main AcnhorLayouts anchor
    def change_anchor(button, *ev_args):
        anchor.anchor_x = random.choice(['left', 'right'])
        anchor.anchor_y = random.choice(['top', 'bottom', 'center'])
        box.orientation = random.choice(['horizontal', 'vertical'])
        button.label = "Anchor: '%s,%s'. Boxlayout:%s" %(anchor.anchor_y, anchor.anchor_x, box.orientation)
    button = MTButton(label="Set Random Anchor Position", width=500)
    button.push_handlers(on_press=curry(change_anchor,button))
    center_anchor = MTAnchorLayout()
    center_anchor.add_widget(button)

    #put teh two layouts into a stretch layout, so they fill the whole window (since stretch is put as root)
    stretch = MTStretchLayout(id='anchor fun')
    stretch.add_widget(anchor)
    stretch.add_widget(center_anchor)
 
    return stretch


def size_hint_test():
    box = MTBoxLayout()
    #box.add_widget( MTButton(label="size_hint=(None, None)") )
    box.add_widget( MTButton(label="size_hint=(1.0,1.0)", size_hint=(0.5, None)) )
    box.add_widget( MTButton(label="size_hint=(1.0,1.0)", size_hint=(0.25, 1.0)) )
    box.add_widget( MTButton(label="size_hint=(1.0,1.0)", size_hint=(0.25, 0.5)) )
    for b in box.children:
        b.push_handlers( on_press=curry(set_screen, 'anchor_fun') )
    stretch = MTStretchLayout(id="size hint")
    stretch.add_widget(box)
    return stretch


if __name__ == '__main__':
    
    screens = MTScreenLayout(id='screens')
    screens.add_widget(size_hint_test())
    screens.add_widget(anchor_test())
    
    root = MTStretchLayout()
    root.add_widget(size_hint_test())
    runTouchApp(root)