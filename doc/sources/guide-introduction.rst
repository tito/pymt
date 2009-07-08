============
Introduction
============

This is a very early draft for what will hopefully turn into a programming guide / introduction to programming multitouch applications with PyMT.

What is PyMT ?
--------------

Developing software is hard. Developing software that utilizes new user interfaces (such as multi-touch displays, displays with stylus input, and others) is even harder, because they are relatively new. We don't know yet what works well, and what old methods of interaction aren't going to work at all. This is where Python and PyMT come in. 

PyMT is a Python framework for developing applications utilizing new user interfaces, such as multi-touch. You may have seen examples of this technology in use on CNN, at a mall, or on the Microsoft Surface(R). PyMT is designed to allow you to create applications just like those, with an emphasis on rapid prototype development and ease of use. We want to spend more time thinking about what we want our software to do, and how we interact with it, rather than wasting time figuring out why stuff doesn't compile or spend extra time making sure it runs on different platforms.

PyMT tries making developing novel and custom interfaces as easy as possible. We have built an event-based framework of widgets that you can use in your applications or to develop your own widgets ('widget' is a term frequently used in graphical user interface (GUI) programming; for PyMT a widget is anything that handles input events or draws itself or does both). For example, with a few lines of code you can add a widget that allows you to display an image on the screen that can be rotated or scaled based on the user's input. Or add a text input field with a touchable virtual keyboard. So, you concentrate on making your application work, while PyMT handles the low-level widget interactions!

The PyMT Architecture
"""""""""""""""""""""

PyMT is built primarily on top of two other libraries, OpenGL and Pyglet. More information on each of these is below, as well as a diagram to help you understand the relationship between the two:

HARDWARE (GRAPHICS CARD) <--- OPENGL <---- PYGLET <---- PYMT

It should be noted, however, that you can easily mix in commands and functions from any library that you wish in your application's code. So, you can just as easily feature a call to pymt.graphx.set_color() (a PyMT high-level graphics function) followed by pyglet.gl.draw() (which is a direct OpenGL call via a Pyglet wrapper).

OpenGL
------

OpenGL (Open Graphics Library) is a standard specification defining a cross-language cross-platform API for writing applications that produce high performance 2D and 3D computer graphics. If you need more general information about OpenGL, a great place to start is its entry on Wikipedia: http://en.wikipedia.org/wiki/OpenGL).

OpenGL is an API which can be used to draw graphics on your screen, utilizing the capabilities of the graphics accelerator present in almost all modern computers. OpenGL performs hardware accelerated drawing in 2D and 3D, offers shaders that run highly parallel directly on your GPU (graphics processing unit), and allows applications written using PyMT to run very quickly and look great at the same time.

If you are familar with OpenGL, you will be happy to learn that PyMT does all its drawing in OpenGL. The moment you sit down to write a widget or a simple app, your drawing functions can just make OpenGL calls without having to set anything up. On the other hand, if you're not familiar with OpenGL, you will be happy to learn that PyMT provides a series of helper functions  wrapped around OpenGL that make it easy to draw shapes, lines or images to the screen -- the pymt.graphx module.

OpenGL is a state machine
"""""""""""""""""""""""""

OpenGL works like a state machine, meaning that all the function calls you make either put the OpenGL state machine into a certain state (like setting the current color, or enabling lighting, etc.) or send data to the GPU to be drawn (e.g. giving the four points of a square to be drawn). The state machine concept can be a little hard to get used to if you're not familar with it, but once you get the hang of it you will really appreciate it.

Transformations, matrices and all that nasty linear algebra
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

While many PyMT applications will be strictly 2D, using OpenGL you also have the opportunity to work in 3D. Should you choose to do so, you will want to know a little bit about matrix multiplication and how that can be used for doing transformations. A full understanding of all the math behind it isn't necessary just to use the concept, however.

If your not scared of math: http://en.wikipedia.org/wiki/Transformation_matrix

Good places to learn OpenGL
"""""""""""""""""""""""""""

* http://nehe.gamedev.net/ - really good tutorials for OpenGL (most of them even have Python code available)
* TODO: more references

Pyglet
------

To further help ease the learning curve, PyMT has been built on top of a common Python media framework called Pyglet (http://www.pyglet.org). This makes using OpenGL as easy as possible, giving you all of the power of OpenGL with all the ease of Python. It has easy to understand functions for loading resources like images, video and sound file, and manages all the system dependent windowing and basic input (such as mouse and keyboard). Just one less thing for you to worry about!
