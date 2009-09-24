'''
===============================================
Introduction Part 2: A Simple Number Generator
===============================================

Well, its tutorial time again! In this tutorial I will guide you through
creating a _very_ simple app that will display a button and some text.
Every time you click the button the text will change. It's a Multi-Touch
Random Number Generator!

Start from a complete example
-----------------------------

Later in the tutorial it will get a little more advanced and allow you
to set a bound. Start by firing up your text editor and opening up tut2.py
(examples/tutorials/tut2.py). If you don't have PyMT yet, please
refer to the previous part of the tutorial.

It should look like this ::

    import random
    from pymt import *

    w = MTWindow()

    b = MTButton(label='Hello, World!', pos=(40, 40), size=(200, 200))
    w.add_widget(b)

    l = MTLabel(label='#', font_size=20, pos=(270, 40))
    w.add_widget(l)

    @b.event
    def on_press(touch):
        l.label = str(random.randrange(0, 100))

    runTouchApp()

If you run this app, you will notice that there is a button to the left that
says "Hello, World!', and a label to the right that has a # symbol in it. If you
tap (or click if you're on a computer), the # changes to a random number between 0
and 100.

Detail line by line of the content
----------------------------------

Lets go through this line by line ::

    import random

This is in no way related to PyMT. It is just here for random number generation,
and is usually not required in a PyMT app. For more info on Python's random
capabilities, see here ::

    from pymt import *

This imports all the PyMT classes into the namespace. Without this line your app
would not work, because it can't use what PyMT provides. This line is required
in every PyMT app (best practice says you should only import what you need and
nothing more, but we will get to that in a later tutorial).

    w = MTWindow()

MTWindow is the first PyMT class we will use. MTWindow is just like any other
window, except it supports Multi-Touch events.

MTWindow is a container for all of our widgets, and when a TUIO event occurs
MTWindow is responsible for dispatching it to the widgets. Each PyMT app needs
at least one MTWindow, and I doubt that anyone will ever use more than one.
The MTWindow has various options you can pass to it as well. They should be
outlined in the documentation.

    b = MTButton(label='Hello, World!', pos=(40, 40), size=(200, 200))

This line creates an instance of an MTButton. MTButton is just a button, nothing
more than that. When it is pressed it dispatches the "on_press" event. The
arguments passed into this button specify that it says "Hello, World!", is at
(40, 40), and is 200 by 200 pixels. Pretty self explanatory. We
mentioned earlier that MTWindow are containers, so the following just adds the
widget we created to the window (think of it as a hierarchy).

    w.add_widget(b)

PyMT is very much based around containers, every widget can have children, and
every widget has a parent. MTWindow is always the root. When you created the button
we agreed to refer to it with the name 'b', but this doesn't mean that it already
shows up. If you want the button to be in your app and show up, you have to add it
to the MTWindow. This is done with the add_widget method, to which you pass the
button instance, as we just did.

Now, since we want to display some output for the user to see that pressing the
button did indeed change something, we create another widget: An instance of MTLabel.
Think of these labels as a means to display text. ::

    l = MTLabel(label='#', font_size=20, pos=(270, 40))

As you might have guessed, we need to add this label to the window as well. ::

    w.add_widget(l)

All PyMT classes allow for their attributes to be set dynamically. As we will
see in a minute, you can change the MTLabel's text by editing the 'label' attribute
of it. For example: l.label = 'Foo'. 'l' is the variable holding our MTLabel, and
'label' is the attribute within 'l' that holds the text the label is displaying ::

    @b.event
    def on_press(touch):

The first line here is called a decorator. Decorators are a very powerful aspect
of Python, and will not be covered here in very much detail as you don't need to
understand the internals in order to use them. What this basically says is that
the function defined below should be called when the on_press event is dispatched
(The name of the event that we listen to is inferred from the function's name).
The second line is the actual function definition. I already mentioned that the
MTButton widget emits the 'on_press' event when it's pressed.

When MTButton emits the "on_press" signal it passes the touch ID and coordinates
of the touch location. The coordinates are very simple, just integer pixel coordinates.
We will cover those in a later tutorial as we don't need them just now.
Though that was a pretty large chunk of python jargon, all you really had to get
out of it was that these lines tell PyMT to call on_press whenever you touch the button ::

    l.label = str(random.randrange(0, 100))

I mentioned earlier that attributes of Python Classes can be edited dynamically,
and PyMT will recognize and apply this change. That is seen here. This line is
called every time the button is pressed, and it uses the "random" module to
generate a random number which is then set as the new text inside our MTLabel object.

    runTouchApp()

This final line tells PyMT to enter the main event loop and start dispatching touch
events. It will be covered in more detail in a later tutorial.
'''

import random
from pymt import *

w = MTWindow()

b = MTButton(label='Hello, World!', pos=(40, 40), size=(200, 200))
w.add_widget(b)

l = MTLabel(label='#', font_size=20, pos=(270, 40))
w.add_widget(l)

@b.event
def on_press(touch):
    l.label = str(random.randrange(0, 100))

runTouchApp()
