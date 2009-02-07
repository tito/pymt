from pymt import *

if __name__ == '__main__':
    w = MTWindow()
    sun = MTSquirtle(filename = 'squirtle/svgs/sun.svg', pos = (200,200))
    cloud = MTSquirtle(filename = 'squirtle/svgs/cloud.svg', pos = (50,100))
    ship = MTSquirtle(filename = 'squirtle/svgs/ship.svg', pos = (280,100))
    w.add_widget(sun)
    w.add_widget(cloud)
    w.add_widget(ship)
    runTouchApp()
