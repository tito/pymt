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
    test(w.visible == True)
    test(w.draw_children == True)
    test(w.cls == '')

def unittest_visible_methods():
    import_pymt_no_window()
    from pymt import MTWidget
    w = MTWidget()
    w.hide()
    test(w.visible == False)
    w.show()
    test(w.visible == True)

def unittest_visible_events():
    import_pymt_no_window()
    from pymt import MTWidget

    global on_update_called
    on_update_called = 0

    def on_update():
        global on_update_called
        on_update_called += 1

    # by default, visible is True
    w = MTWidget()
    w.connect('on_update', on_update)
    w.dispatch_event('on_update')
    test(on_update_called == 1)

    # make it invisible
    w.visible = False
    w.dispatch_event('on_update')
    test(on_update_called == 1)

    # make it visible
    w.visible = True
    w.dispatch_event('on_update')
    test(on_update_called == 2)

    # create a new widget, visible default to False
    on_update_called = 0
    w = MTWidget(visible=False)
    try:
        # XXX FIXME unable to connect to default on_update
        # since it's not yet register.
        w.connect('on_update', on_update)
    except:
        pass
    w.dispatch_event('on_update')
    test(on_update_called == 0)

    w.visible = True
    w.connect('on_update', on_update)
    w.dispatch_event('on_update')
    test(on_update_called == 1)

