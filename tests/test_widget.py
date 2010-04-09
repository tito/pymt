'''
Widgets
'''

from init import test, import_pymt_no_window

def unittest_defaults():
    import_pymt_no_window()
    from pymt import MTWidget
    w = MTWidget()
    test(w.x == 0)
    test(w.y == 0)
    test(w.width == 100)
    test(w.height == 100)
