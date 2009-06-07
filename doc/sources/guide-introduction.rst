============
Introduction
============

This is avery early draft for what will hopefully turn into a programming guide / introduction to programming multitouch applications with PyMT.

What is PyMT ?
--------------

Lets get a general idea about PyMT is meant to be; understanding how all the parts of PyMT work together will be easier with that in mind.

PyMT is meant to be a python module for developing multitouch applications (yeah..the cool awesome futuristic stuff you have seen from Jeff Han, the Microsoft Surface Team, and the nuigroup community).

Developing software is hard. Developing software for novel user interfaces like multi touch displays (and really all sorts of novel input /interaction devices) is even harder, because we haven't had them for all that long and dont really know what works yet. This is where python and PyMT come in. We want to spend more time thinking about what we want our software to do, and how we interact with it, rather than wasting time figuring out why stuff doesn't compile or spend extra time making sure it runs on different platforms.

PyMT tries making developing novel, and custom interfaces as easy as possible. We have built an event based framework of widgets that you can use in your applications or to develop your own widgets. 'Widget' is a term frequently used in Graphical User interface(GUI) programming. For PyMT a widget is anything that handles input events or draws itself or does both.

OpenGL
------

OpenGL (Open Graphics Library) is a standard specification defining a cross-language cross-platform API for writing applications that produce high performance 2D and 3D computer graphics. (that sentence is straight from wikipedia, which is probably a good place to start if you dont know what OpenGL is: http://en.wikipedia.org/wiki/OpenGL).

OpenGL is an API which you can use to draw grahics on your screen, while making good use of the expensive video card sitting in your computer. With OpenGL you can do hardware accelerated drawing in 2D and 3D, you can write shaders that run highly parallel directly on your GPU(graphics processing unit).

If you are familar with OpenGL, you will be happy to leanr that PyMT does all its drawing in OpenGL. The moment you sit down to write a widget or a simple app, your drawing functions can just make OpenGL calls without having to set anything up. If your not familiar with OpenGL, you will be happy to learn that PyMT provides a bunch of helper functions around OpenGL that make is really easy to draw shapes, lines or images to the screen.

OpenGL is a state machine
"""""""""""""""""""""""""

OpenGL works like a state machine, all the function calls you make either put the OpenGL state machine into a certain state (like setting the current color, or enabling lighting, etc.) or send data to the gpu to be drawn (e.g. giving the four points of a square to be drawn). The state machine concept can be a little hard to get used to if your not familar with it, but it actually makes a LOT of sense if you spend a little time figuring it out.

Transformations, matrices and all that nasty linear algebra
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Especially if you want to do 3D drawing, you will want to know a little bit about matrix multiplication and how that can be used for doing transformations. you dont really have to understand all the math to use the concept.

If your not scared of math: http://en.wikipedia.org/wiki/Transformation_matrix

Good places to learn OpenGL
"""""""""""""""""""""""""""

* http://nehe.gamedev.net/ - really good tutorials for OpenGL (most of them even have python code available)
* TODO: more references

Pyglet
------

OpenGL can be hard to learn. we have built PyMT on top of pyglet (http://www.pyglet.org) to make using OpenGL as easy as possible. pyglet is awesome, it gives you all the power of OpenGL, easily accesible through python. It has a bunch of nice functions for loading resources like images, video and sound files, takes care of all the system dependent windowing and basic input (mouse, keyboard), so you (and us for that matter :P) dont have to worry about that.

