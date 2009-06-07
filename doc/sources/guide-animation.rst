==========
Animations
==========

What is animation ?
-------------------

In PyMT, Animation is a package to change value of property over the time : this can only work with integer, float, list/tuple of integer/float.

Simple exemple of animation ::

    # Create a widget
    w = MTWidget()

    # Some event message
    @w.event
    def on_animation_start(self):
        print 'animation start, x=', w.x

    @w.event
    def on_animation_complete(self):
        print 'animation finished, x=', w.x

    # Create animation
    a = Animation(w, 'xmove', 'x', 100, 1, 20)
    a.start()

    # Run application
    runTouchApp()

