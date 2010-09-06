import random
from pymt import *


def simple_box_layout_test():
    root = MTBoxLayout()
    root.add_widget(MTButton(label="button 1"))
    root.add_widget(MTButton(label="button 2"))
    root.add_widget(MTButton(label="button 3"))
    return root

def vertical_box_layout_test():
    root = MTBoxLayout(orientation='vertical', id='vertical', size_hint=(2.0,1.0), bg_color=(0,1,0,0.3))
    root.add_widget(MTButton(label="button 1"))
    root.add_widget(MTButton(label="button 2"))
    root.add_widget(MTButton(label="button 3"))
    return root

def size_hint_box_layout_test():
    root = MTBoxLayout(width=())
    root.add_widget(MTButton(label="button 1"))
    root.add_widget(MTButton(label="button 2"))
    root.add_widget(MTButton(label="button 3"))
    return root

def stacked_box_layout():
    root = MTBoxLayout(id='root', size_hint=(1.0,1.0),bg_color=(1,0,0,0.3))
    root.add_widget(MTButton(label="button", size_hint=(1.0, 1.0)))
    root.add_widget(simple_box_layout_test())
    root.add_widget(vertical_box_layout_test())
    root.add_widget(MTButton(label="button"))
    return root

if __name__ == '__main__':
    root = stacked_box_layout()
    runTouchApp(root)