'''
============================
Introduction to PyMT, part 2
============================

Well, its tutorial time again ! In this tutorial I will guide you through
creating a _very_ simple app that will display a button and some text.
Every time you click the button the text will change. Its a Multi-Touch
Random Number Generator !

Later in the tutorial it will get a little more advanced, and allow you
to set a bound! Start by firing up your text editor and opening up tut1.py
in the tutorials folder in the examples folder of the subversion
tree(trunk/examples/tutorials/tut2.py). If you don't have pymt checked out yet,
or its not installed, see Tutorial Part 1 by Sharath.

It should look like this ::

    import random
    from pymt import *

    w = MTWindow()

    b = MTButton(label='Hello, World!', pos=(40, 40), size=(200, 200))
    w.add_widget(b)

    l = MTLabel(text='#', font_size=200, pos=(270, 40))
    w.add_widget(l)

    @b.event
    def on_press(touch):
    l.text = str(random.randrange(0, 100))

    runTouchApp()

If you run this app, you will notice that there is a button to the left that
says "Hello, World!', and a label to the right that has a # symbol in it. If you
tap (or click if your on a computer), the # changes to a random number between 0
and 100.

Lets go through this line by line ::

    import random

This is in no way related to PyMT. It is just here for random number generation,
and is usually not required in a PyMT app. For more info on Python's random
capabilities, see here ::

    from pymt import *

This imports all the PyMT classes into the namespace. Without this line your app
would not work, because it can't use what PyMT provides. This line is required
in every PyMT app(best practice says you should only import what you need and
nothing more, but we will get to that in a later tutorial).

    w = MTWindow()

MTWindow is the first PyMT class we will use. MTWindow is just like any other
window, except it supports Multi-Touch events.

MTWindow is a container for all of our widgets, and when a TUIO event occurs
MTWindow is responsible for dispatching it to the widgets. Each PyMT app needs
at least one MTWindow, and I doubt that anyone will ever use more than one.

The MTWindow has various options you can pass to it as well. They should be
outlined in the documentation. The one I pass it here tells it not to run
fullscreen, because I assume most people won't be going through these tutorials
on their table. If you want it to be fullscreen, either set it to True(with a
capital 'T'), or just delete it, as it defaults to true ::

    b = MTButton(label='Hello, World!', pos=(40, 40), size=(200, 200))

This line creates an instance of an MTButton. MTButton is just a button, nothing
more then that. When it is pressed it dispatches the "on_press" event. The
arguments passed into this button specify that it says "Hello, World!", is at
(40, 40), and is 200 by 200 pixels. Pretty self explanatory. w.add_widget(b)
mentioned earlier that MTWindow are containers.

PyMT is very much based around containers, every widget can have children, and
every widget has a parent. MTWindow is always the root (unless you get into
InnerWindow, but that is WAY out of the scope of the second tutorial, and we are
working on removing it). When you create the button(previous line), it gets put
in 'b', but it doesn't show up. If you want the button to be in your app and
show up, you have to add it to the MTWindow. This is done with the add_widget
method, to which you pass the button instance.

I hope to cover containers in a later tutorial, as they are a fascinating and
useful aspect of PyMT ::

    l = MTLabel(text='#', font_size=200, pos=(270, 40)) w.add_widget(l)

This works the same as the previous two lines, except we instantiate an MTLabel
instead of a button.

All PyMT classes allow for their attributes to be set dynamically. As we will
see in a minute, you can change the MTLabel's text by editing the text attribute
of it. For example: l.text = 'Foo'. l is the variable holding our MTLabel, and
text is the attribute within l that holds the text the label is displaying ::

    @b.event
    def on_press(touch):

The first line here is called a decorator. Decorators are a very powerful aspect
of Python, and will not be covered here in very much detai.

The second line is a function definition for a function called on_press. If you
remember back to the MTButton line I mentioned that MTButton emits the
"on_press" event when it is pressed. What these two lines essentially mean is:
    "When b puts out an event, see if it is this function, and if it is, call
    this function".

When MTButton emits the "on_press" signal it passes the touch ID and coordinates
of the location. The coordinates are very simple, just integer pixel locations.
You will have to wait till a later tutorial to you the touch ID, though for a
button it is rarely needed. Though that was a pretty large chunk of python
jargon, all you really had to get out of it was that these lines tell PyMT to
call on_press whenever you touch the button ::

    l.text = str(random.randrange(0, 100))

I mentioned earlier that attributes of Python Classes can be edited dynamically,
and PyMT will recognize and apply this change. That is seen here. This line is
called every time the button is pressed, and it uses the "random" module to
generate a random number.

    runTouchApp()

This tells PyMT to enter the main event loop and start dispatching touch events.
It will be covered in more detail in a later tutorial.
'''

import random
from pymt import *

w = MTWindow()

b = MTButton(label='Hello, World!', pos=(40, 40), size=(200, 200))
w.add_widget(b)

l = MTLabel(label='#', font_size=200, pos=(270, 40))
w.add_widget(l)

@b.event
def on_press(touch):
    l.label = str(random.randrange(0, 100))

runTouchApp()
