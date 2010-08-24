'''
Test usage of MTTextArea widget
'''

from init import test, import_pymt_window

def instance(**kwargs):
    ''' Individual test framework'''
    import_pymt_window()
    from pymt import MTTextArea
    from pymt import css_add_sheet, css_reload
    try:
        return MTTextArea(**kwargs)
    except:
        return None
        
    
def unittest_mttextarea():
    '''Test  driver'''
    
    # Test defaults
    t = instance()
    test(t is not None)
    if t is None: return
    test(t.height == 100)
    test(t.width == 100)
    test(t.value == '')
    test(len(t._glyph_size) == 0)
    test(len(t.lines) == 1)
    
    # Test operations with a single line in widget
    tline1 = 'This is a single line'
    t.value =tline1
    test(tline1 == t.value)
    test(len(t.lines) == 1)
    test(t.height == 100)
    test(t.width == 100)
    
    # Replace text with an empty string
    emptyline = ''
    t.value = emptyline
    test(emptyline == t.value)
    test(len(t.lines) == 1)
    test(t.height == 100)
    test(t.width == 100)
    
    # Now lets put in a string of 12 lines and see what happens
    tline2 = ['', 'Line 1', ('Line 2 which is rather long and should overflow'
              ' horizontally ........................'),
              'Line 3', 'Line 4', 'Line 5   ', 'Line 6', '   Line 7',
              'Line 8', '', 'Line 10', '']
    tline2b = '\n'.join(tline2)
    t.value = tline2b
    # Among other things, make sure leading and trailing white space
    # are not lost
    test(tline2b == t.value)
    test(len(t.lines) == 12)
    test(t.height == 100)
    test(t.width == 100)
    
    # Lets replace line 8
    lt1 = 'Replacement text for line 8'
    tline2[7] = lt1
    tline2c = '\n'.join(tline2)
    t.set_line_text(7, lt1)
    test(tline2c == t.value)
    test(len(t.lines) == 12)
    test(t.height == 100)
    test(t.width == 100)
    
    # Test full auto-sizing
    del t
    t = instance(autosize=True)
    test(t is not None)
    if t is None: return
    
    # Test defaults
    test(int(t.height) == 25)
    test(int(t.width) == 1)
    test(t.value == '')
    test(len(t._glyph_size) == 0)
    test(len(t.lines) == 1)
    
    # Test operations with a single line in widget
    # This test assumes the default font and Pygame as text manager running
    # on Ubuntu 10.04.
    # Other text managers may give slightly different results for dimensions
    # and different fonts could cause larger variations
    t.value =tline1
    test(tline1 == t.value)
    test(len(t.lines) == 1)
    test(int(t.height) == 25)
    test(int(t.width) == 203)
    
    # Replace text with an empty string
    t.value = emptyline
    test(emptyline == t.value)
    test(len(t.lines) == 1)
    test(int(t.height) == 25)
    test(int(t.width) == 1)

    # Now lets put in a string of 12 lines and see what happens
    t.value = tline2b
    # Among other things, make sure leading and trailing white space
    # are not lost
    test(tline2b == t.value)
    test(len(t.lines) == 12)
    test(int(t.height) == 322)
    test(int(t.width) == 809)
