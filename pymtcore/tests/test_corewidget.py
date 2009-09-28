import unittest
import pymtcore

__all__ = ['CoreWidgetTestCase']

class CoreWidgetTestCase(unittest.TestCase):
    def testWidgetMethodsAvailability(self):
        self.failUnless(hasattr(pymtcore.CoreWidget, 'add_widget'))
        self.failUnless(hasattr(pymtcore.CoreWidget, 'remove_widget'))
        self.failUnless(hasattr(pymtcore.CoreWidget, 'draw'))
        self.failUnless(hasattr(pymtcore.CoreWidget, 'on_draw'))
        self.failUnless(hasattr(pymtcore.CoreWidget, 'on_touch_down'))
        self.failUnless(hasattr(pymtcore.CoreWidget, 'on_touch_move'))
        self.failUnless(hasattr(pymtcore.CoreWidget, 'on_touch_up'))
        self.failUnless(hasattr(pymtcore.CoreWidget, 'on_update'))
        self.failUnless(hasattr(pymtcore.CoreWidget, 'to_local'))
        self.failUnless(hasattr(pymtcore.CoreWidget, 'to_parent'))
        self.failUnless(hasattr(pymtcore.CoreWidget, 'to_widget'))
        self.failUnless(hasattr(pymtcore.CoreWidget, 'to_window'))
        self.failUnless(hasattr(pymtcore.CoreWidget, 'get_parent_window'))
        self.failUnless(hasattr(pymtcore.CoreWidget, 'get_parent_layout'))
        self.failUnless(hasattr(pymtcore.CoreWidget, 'get_root_window'))
        self.failUnless(hasattr(pymtcore.CoreWidget, 'connect'))
        self.failUnless(hasattr(pymtcore.CoreWidget, 'disconnect'))
        self.failUnless(hasattr(pymtcore.CoreWidget, 'dispatch_event'))
        self.failUnless(hasattr(pymtcore.CoreWidget, 'dispatch_event_internal'))

    def testWidgetDefaultValues(self):
        widget = pymtcore.CoreWidget()
        self.failUnless(widget.visible == True)
        self.failUnless(widget._get_x() == 0)
        self.failUnless(widget._get_y() == 0)
        self.failUnless(widget._get_width() == 100)
        self.failUnless(widget._get_height() == 100)
        self.failUnless(widget._get_pos() == (0, 0))
        self.failUnless(widget._get_size() == (100, 100))
        self.failUnless(widget._get_center() == (50, 50))

    def testWidgetCreation(self):
        widget = pymtcore.CoreWidget()
        self.failUnless(widget is not None)

    def testWidgetChildrenVectorIn(self):
        widget1 = pymtcore.CoreWidget()
        widget2 = pymtcore.CoreWidget()
        widget1.add_widget(widget2)
        self.failUnless(widget2 in widget1.children)

    def testWidgetChildrenVector0(self):
        widget1 = pymtcore.CoreWidget()
        widget2 = pymtcore.CoreWidget()
        widget1.add_widget(widget2)
        self.failUnless(widget1.children[0] == widget2)

    def testWidgetAppendRemoveChildren(self):
        widget1 = pymtcore.CoreWidget()
        widget2 = pymtcore.CoreWidget()
        self.failUnless(widget2 not in widget1.children)
        self.failUnless(len(widget1.children) == 0)

        widget1.add_widget(widget2)
        self.failUnless(len(widget1.children) == 1)
        self.failUnless(widget2 in widget1.children)

        widget1.remove_widget(widget2)
        self.failUnless(len(widget1.children) == 0)
        self.failUnless(widget2 not in widget1.children)

    def testWidgetInvalidRemoveChildren(self):
        widget1 = pymtcore.CoreWidget()
        widget1.remove_widget(None)

    def testWidgetInheritance(self):
        class SubWidget(pymtcore.CoreWidget):
            def __init__(self):
                super(SubWidget, self).__init__()
                self.var = 0
            def on_update(self, data):
                self.var += 1
                super(SubWidget, self).on_update(data)
        widget1 = pymtcore.CoreWidget()
        widget2 = SubWidget()
        widget1.add_widget(widget2)
        widget2.dispatch_event('on_update', ())
        self.failUnless(widget2.var == 1)

    def testWidgetReferenceCount(self):
        widget = pymtcore.CoreWidget()
        child = pymtcore.CoreWidget()
        self.failUnless(widget.get_ref_count() == 1)
        self.failUnless(child.get_ref_count() == 1)
        widget.add_widget(child)
        self.failUnless(widget.get_ref_count() == 2)
        self.failUnless(child.get_ref_count() == 2)

        # we stay in python, and swig is still used
        # normally, reference counter don't move.
        a = widget
        self.failUnless(a.get_ref_count() == 2)
        self.failUnless(child.get_ref_count() == 2)

        # we remove one widget, but a still exist.
        del widget
        self.failUnless(a.get_ref_count() == 2)
        self.failUnless(child.get_ref_count() == 2)

        # no more reference on initial widget
        # the child is now orphan
        del a
        self.failUnless(child.get_ref_count() == 1)
        self.failUnless(child.parent == None)

    def testWidgetTransformationToLocal(self):
        widget = pymtcore.CoreWidget()
        res = widget.to_local(1, 2)
        self.failUnless(type(res) == tuple)
        self.failUnless(len(res) == 2)
        self.failUnless(res == (1, 2))

    def testWidgetTransformationToParent(self):
        widget = pymtcore.CoreWidget()
        res = widget.to_parent(1, 2)
        self.failUnless(type(res) == tuple)
        self.failUnless(len(res) == 2)
        self.failUnless(res == (1, 2))

    def testWidgetTransformationToWidget(self):
        widget = pymtcore.CoreWidget()
        res = widget.to_widget(1, 2)
        self.failUnless(type(res) == tuple)
        self.failUnless(len(res) == 2)
        self.failUnless(res == (1, 2))

    def testWidgetTransformationToWindow(self):
        widget = pymtcore.CoreWidget()
        res = widget.to_widget(1, 2)
        self.failUnless(type(res) == tuple)
        self.failUnless(len(res) == 2)
        self.failUnless(res == (1, 2))

    def testWidgetVisible(self):
        widget = pymtcore.CoreWidget()
        self.failUnless(widget.visible == True)
        widget.hide()
        self.failUnless(widget.visible == False)
        widget.show()
        self.failUnless(widget.visible == True)

    def testWidgetPosWithAccessor(self):
        widget = pymtcore.CoreWidget()
        widget._set_pos((54, 32))
        self.failUnless(widget._get_x() == 54)
        self.failUnless(widget._get_y() == 32)
        self.failUnless(widget._get_pos() == (54, 32))
        self.failUnless(widget._get_center() == (104, 82))
        self.failUnless(widget.x == 54)
        self.failUnless(widget.y == 32)
        self.failUnless(widget.pos == (54, 32))
        self.failUnless(widget.center == (104, 82))

    def testWidgetPosWithProperties(self):
        widget = pymtcore.CoreWidget()
        widget.pos = (54, 32)
        self.failUnless(widget.x == 54)
        self.failUnless(widget.y == 32)
        self.failUnless(widget.pos == (54, 32))
        self.failUnless(widget.center == (104, 82))

    def testWidgetPositionProperties(self):
        widget = pymtcore.CoreWidget()
        widget.x = 2
        self.failUnless(widget.x == 2)
        self.failUnless(widget.pos == (2, 0))
        widget.x += 2
        self.failUnless(widget.x == 4)
        self.failUnless(widget.pos == (4, 0))
        widget.y = 2
        self.failUnless(widget.y == 2)
        self.failUnless(widget.pos == (4, 2))
        widget.y += 2
        self.failUnless(widget.y == 4)
        self.failUnless(widget.pos == (4, 4))
        widget.pos = (10, 10)
        self.failUnless(widget.x == 10)
        self.failUnless(widget.y == 10)
        self.failUnless(widget.pos == (10, 10))

    def testWidgetCenterProperties(self):
        widget = pymtcore.CoreWidget()
        widget.size = 10, 10
        widget.center = 10, 10
        self.failUnless(widget.x == 5)
        self.failUnless(widget.y == 5)
        self.failUnless(widget.center == (10, 10))
        widget.pos = 10, 10
        self.failUnless(widget.center == (15, 15))

    def testWidgetSizeProperties(self):
        widget = pymtcore.CoreWidget()
        widget.width = 2
        self.failUnless(widget.width == 2)
        self.failUnless(widget.size == (2, 100))
        widget.width += 2
        self.failUnless(widget.width == 4)
        self.failUnless(widget.size == (4, 100))
        widget.height = 2
        self.failUnless(widget.height == 2)
        self.failUnless(widget.size == (4, 2))
        widget.height += 2
        self.failUnless(widget.height == 4)
        self.failUnless(widget.size == (4, 4))
        widget.size = (10, 10)
        self.failUnless(widget.width == 10)
        self.failUnless(widget.height == 10)
        self.failUnless(widget.size == (10, 10))
