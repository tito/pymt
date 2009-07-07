
==============

CRAYON PHYSICS -- PyMT EDITION

==============

This is a simple game which allows you to draw shapes on the screen. Those shapes then become "physical objects", which bounce around and react realistically to input and to each other. It's based on Crayon Physics Deluxe -- http://www.crayonphysics.com/.

Project Goal:

Create a game of some sort. There would need to a "point" besides just a sandbox. In the original Crayon Physics, this is to move a ball onto a certain point on the screen, by drawing objects. This won't really work for this game (especially since there is no definite "down" direction, therefore no gravity), so we need a new objective!

How to use:

Touch and drag to draw lines on the screen. If you "close" a shape (meaning that the beginning point and end points are close together), it will be turned into an object, and it will fill in automatically. You can interact with objects (filled-in shapes) on the screen by dragging and flinging them.

If you double-tap (or Shift-Click if using a mouse) on a shape, you will enter "joint mode". All physics will halt (the shapes will stop moving around). The first part of the joint will be the shape you double-tapped on. Tap again on another shape, and a joint will be created between the two, tethering them together.

That's it for now!

PROGRAMMING TO-DO LIST:

- Add in textures for drawing lines and the polygons. Something that looks like you're drawing with a crayon!

- Add in background, something that looks like paper would be great.

- More realistic movement of objects (tweaking of velocities, step time). It would be nice to have a noticeable difference in speed depending on how far the object is moved.

- Add in some comforting music.

- Add in ability to drag 'n drop pre-made objects onto the "stage" -- for example, more complex shapes.

- Refine joint mode. Should show possible joints, and there is currently a bug where after you create a joint the second object doesn't start reacting to the physics again until after you move it.

- Add save screen/session ability. This would allow folks to a) return to an already existing game and b) allow us to easily create new levels/stages -- just draw it then save it!