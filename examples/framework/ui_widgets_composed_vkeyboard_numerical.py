from pymt import *

# create a custom layout, a numerical one
class NumericKeyboardLayout(KeyboardLayout):
    ID              = 'numeric'
    TITLE           = 'Numeric keyboard'
    DESCRIPTION     = ''
    SIZE            = (4, 4)
    NORMAL_1 = [
        ('7', '7', None, 1),    ('8', '8', None, 1),    (u'9', u'9', None, 1),
        (u'\u2a2f', None, 'escape', 1),
    ]
    NORMAL_2 = [
        ('4', '4', None, 1),    ('5', '5', None, 1),    (u'6', u'6', None, 1),
    ]
    NORMAL_3 = [
        ('1', '1', None, 1),    ('2', '2', None, 1),    (u'3', u'3', None, 1),
        (u'\u232b', None, 'backspace', 1),
    ]
    NORMAL_4 = [
        ('0', '0', None, 1),    (',', ',', None, 2),
        (u'\u23ce', None, 'enter', 1)
    ]

# create a keyboard, with our custom layout
k = MTVKeyboard(layout=NumericKeyboardLayout(), size=(400, 300))

# create a instance of textinput, with this keyboard by default
m = MTTextInput(keyboard=k)

runTouchApp(m)
