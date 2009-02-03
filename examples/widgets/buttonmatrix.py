# -*- coding: utf-8 -*-

from pymt import *

m = MTButtonMatrix(matrix_size = (30,30))

slider = MTSlider(pos = (10,10))
for btn in range(len(m.buttons)):
    if not btn % 2:
        m.buttons[btn].set_state('down')

if __name__ == '__main__':
    w = MTWindow()
    w.add_widget(m)
    runTouchApp()
