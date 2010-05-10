'''
Css styling basic tests
'''

from init import test, import_pymt_no_window

def unittest_css():
    import_pymt_no_window()
    from pymt import MTWidget
    from pymt import css_add_sheet, css_reload
    css_add_sheet('''
    .style { bg-color: rgba(255, 255, 255, 255);}
    #my { bg-color : rgba(255, 0, 255, 0);}
    ''')
    w = MTWidget(cls='style')
    x = MTWidget(id='my',cls='style')
    test(w.style['bg-color'] == [1.0 ,1.0 ,1.0 ,1.0])
    test(x.style['bg-color'] == [1.0 ,0.0 ,1.0 ,0.0])
    x.style['bg-color'] = [0, 0, 0, 0]
    test(x.style['bg-color'] == [0 ,0 ,0 ,0])
