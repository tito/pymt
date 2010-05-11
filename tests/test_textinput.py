'''
test usage of MTTextInput widget
'''

from init import test, import_pymt_no_window

def instance():
    import_pymt_no_window()
    from pymt import MTTextInput
    from pymt import css_add_sheet, css_reload
    try:
        t = MTTextInput()
        return True
    except:
        return False

def unittest_mttextinput():
    test(instance())

