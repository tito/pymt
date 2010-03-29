'''
Widgets
'''

from init import test, test_runpymt, test_image

def unittest_defaults():
    from pymt import MTWidget
    w = MTWidget()
    test(w.x == 0)
    test(w.y == 0)
    test(w.width == 100)
    test(w.height == 100)

    test_runpymt(w)
    test_image()

