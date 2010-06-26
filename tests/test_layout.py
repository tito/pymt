'''
Layout
'''

from init import test, import_pymt_no_window

def unittest_boxlayout_horizontal():
    _test_boxlayout('horizontal')

def unittest_boxlayout_vertical():
    _test_boxlayout('vertical')

def _test_boxlayout(orientation):
    import_pymt_no_window()
    from pymt import MTBoxLayout, MTWidget

    # note: this test act always if orientation
    # is a horizontal one. use sw() around pos or size
    # to ensure that the swap is done.

    # note: default spacing is 1
    # default padding is 0

    def sw(tpl):
        if orientation == 'vertical':
            return tpl[1], tpl[0]
        return tpl

    # default add
    m = MTBoxLayout(orientation=orientation)
    for x in xrange(10):
        m.add_widget(MTWidget(size=(10,10)))
    print m.size
    test(sw(m.size) == (109, 10))

    # spacing to 10
    m = MTBoxLayout(orientation=orientation, spacing=10)
    for x in xrange(10):
        m.add_widget(MTWidget(size=(10,10)))
    test(sw(m.size) == (190, 10))

