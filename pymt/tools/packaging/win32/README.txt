!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
READ THIS FIRST
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

This version of PyMT is a portable win32 version, 32 bits. (it work also for
64 bits Windows.) This means everything you need to run pymt (including 
python and all other dependencies etc) are included.

This README only addresses the things specific to the portable version of pymt.  
For general information on how to get started, where to find the documentation 
and configuration see the README file in the pymt directory about PyMT.

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


Running portable PyMT
=====================

The same directory that has this README file in it, contains a file called pymt.bat
running this pymt.bat file will set up the environment for pymt and starts the 
python interpreter with any arguments you passed

Example
~~~~~~~

If you open a command line and go to the directory (or add it to your PATH) 
You can run the following:

pymt -m pymt.tools.demo  <-- will run a simple pymt demo from teh pymt.tools module

pymt test.py -w  <-- will run test.py as a python script with pymt ready to use


Run a PyMT application without going to the command line
========================================================

Two options :

1. You can drag your python script on top the pymt.bat file and it will launch

2. If you right click on your python script (.py ending or whatever you named it), 
you can select properties and select an application to open this type of file with.
Navigate to the folder that includes this README and select the pymt.bat file.  
Now all you have to do is double click (check do this always for this file type 
to make this the default)


If you already have Python installed
====================================

The portable PyMT version shouldn't cause any conflicts and cooperate fairly well 
(at least if it's Python 2.6, otherwise some modules might cause problems if there
is entries on PYTHONPATH)


Install PyMT as a standard python module
========================================

Please refer to the install instructions in the complete README :
* inside the pymt folder inside this one
* or the wiki at http://pymt.eu/wiki

