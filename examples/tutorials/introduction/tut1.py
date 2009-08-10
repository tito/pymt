'''
==========================================
Introduction part 1 : installation of PyMT
==========================================

Wondering how we did all that in PyMT ? How we managed to create all examples.
Then your wait is over, we are starting a series of tutorials for PyMT. In this
first tutorial, i'm going to teach you how to setup a PyMT development
environment and to get the examples up and running.

Behind the scene (The Process Involved)
---------------------------------------

PyMT is a framework developed to make life easier for python based multitouch
applications developers and researchers.

Every computer vision based multitouch system requires something called as a
Tracker. Trackers are softwares which captures video frames and analyzes them to
recognize where you are touching the surface. One such opensource tracker is
CCV (You can also use TouchLib).

CCV is the tracking software which recognizes where you are touching the
screen and gives out the coordinates of the touch input using the TUIO protocol,
this TUIO information is used by our Framework to generate the touch events. You
can then handle the touch events appropriately in your application (I'll explain
more about handling the touch events in my upcoming tutorials).

Requirements
------------

1. Python 2.6 - http://www.python.org/download/
2. pyglet 1.1.2 - http://www.pyglet.org/download.html
3. numpy - http://sourceforge.net/project/showfiles.php?group_id=1369&package_id=175103
4. PyMT - http://pymt.txzone.net/pages/Downloads
5. CCV (The tracker) - http://ccv.nuigroup.com/


.. warning ::

    This tutorial assumes that you have prior knowledge of python


Step 1: Packages installations
------------------------------

* Install all the mentioned packages
* There is no official build of Numpy for windows xp , so use this package
* The installation instructions for pymt is given here
* Once you are done with this step you should have the PyMT development
  environment up and running, you can then import the PyMT library from any
  location
* You can test it out using IDLE (python interpreter)

1. Go to command-line and type ::

    python

2. Now you are inside the IDLE, now type ::

    import pymt

3. If you don't get any errors then your PyMT development environment is up and
running. If you do get errors then repeat the steps above.
4. To exit python shell, just hit Control+d (on linux), or type exit() (on
windows) ::

    exit()


Step 2 : Configuration of CCV tracker
-------------------------------------

PyMT can take touch inputs from either a external tracker, or from its built in
touch simulator :

* the built-in simulator works with mouse, and is used to debug applications.
* the external tracker (CCV in our case) sends multitouch information to a TUIO server.

We'll focus on the external tracker part. Let's assume our external tracker is
CCV, CCV sends out TUIO data which will be processed by the PyMT framework and
used as touch coordinates.

1. Start the CCV and calibrate it :)
2. Activate TUIO message sending, by clicking on send TUIO button
3. Double click on the example apps and that's it the app should be recognizing
   the touch inputs.

'''

from pymt import *
m = MTWindow()
m.add_widget(MTLabel(label='Hello world'))
runTouchApp()
