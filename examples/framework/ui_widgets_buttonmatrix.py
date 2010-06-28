from pymt import *

# create a custom 10x10 matrix, fullscreen
m = MTButtonMatrix(matrix_size=(10, 10), size_hint=(1, 1))

# create a default handler for the on_press event
def m_on_press(args):
    # extract row / column / state
    row, column, state = args
    print 'matrix change at %d x %d = %s' % (row, column, state)

# connect the handler to the widget
m.connect('on_press', m_on_press)

runTouchApp(m)
