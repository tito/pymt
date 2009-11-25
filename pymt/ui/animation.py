'''
Animation package: handle animation with ease in PyMT

Animation
=========

This is an Animation Framework, using which you can animate any
property of an object over a provided duration. You can even animate 
CSS property.

Simple Animation
----------------

::
    widget = SomeWidget()
    animobj = Animation(duration=5,x=100,style={'bg-color':(1.0,1.0,1.0,1.0)})
    widget.do (animobj)
 
You create a animation class object and pass the object into the widget
that you would like to animate, the object will be animated from its current state
to the state specified in the animation object.

You can also use animate() method of the Animation class to animate the widget ::
    
    animobj.animate(widget)
  
You can also pass multiple widgets, to animate the same way ::

     # solution 1
     animobj.animate(widget1, widget2)
     
     # solution 2
     widget1.do(animobj)
     widget2.do(animobj)
 

Complex Animations
------------------

You can sequence several animations together ::

::
    anim1 = Animation(duration=1, x=100)
    anim2 = Animation(duration=2, y = 200)
    anim3 = Animation(duration=1, rotation = 60)
    
    anim_xyrot = anim1 + anim2 + anim3
    
    widget.do(anim_xyrot)
    
This is execute the animations sequentially, "+" is used to execute them sequentially.
First the widget will move to x=100 in 1 sec then it will move to y=200 in secs and
finally rotate clockwise 60 Degress in 1 sec.

You can also run several animations parallel ::

::
    anim1 = Animation(duration=1, x=100)
    anim2 = Animation(duration=2, y = 200)
    anim3 = Animation(duration=1, rotation = 60)
    
    anim_xyrot = anim1 & anim2 & anim3
    
    widget.do(anim_xyrot)
    
This will execute all the animations on the properties togather. "&" operator is used
to run them parallel 
'''

__all__ = ['AnimationAlpha', 'Animation']

import math
from ..clock import getClock

class AnimationBase(object):
    # This is the base animation object class. Everytime a do or animate method is called 
    # a new animobject is created.
    def __init__(self,**kwargs):
        self.widget = kwargs.get('widget')
        self.params = kwargs.get('key_args')
        self.duration =  self.params['duration']
        self.animator = kwargs.get('animator')
        if "generate_event" in self.params.keys():
            self.generate_event = self.params['generate_event']
        else:
            self.generate_event = True

        self._frame_pointer = 0.0
        self._progress = 0.0
        self.running = False

        self._prop_list = {}
        for item in self.params:
            if item not in ("duration", "anim1", "anim2", "generate_event", "single_event"):
                self._prop_list[item] = self.params[item]

        for prop in self._prop_list:
            cval = self._get_value_from(prop)
            if type(cval) in (tuple, list):
                self._prop_list[prop] = (cval, self._prop_list[prop])
            elif isinstance(cval, dict):
                #contruct a temp dict of only required keys
                temp_dict = {}
                for each_key in self._prop_list[prop]:
                    temp_dict[each_key] = cval[each_key]
                self._prop_list[prop] = (temp_dict, self._prop_list[prop])
            else:
                self._prop_list[prop] = (cval,self._prop_list[prop])

    def _get_value_from(self, prop):
        if hasattr(self.widget, prop):
            return self.widget.__getattribute__(prop)
        return self.widget.__dict__[prop]

    def _set_value_from(self, value, prop):
        if hasattr(self.widget, prop):
            kwargs = {}
            try:
                self.widget.__setattr__(prop, value, **kwargs)
            except:
                self.widget.__setattr__(prop, value)
        else:
            self.widget.__dict__[prop] = value

    def update(self, t):
        for prop in self._prop_list:
            vstart, vend =  self._prop_list[prop]
            value = self._calculate_attribute_value(vstart, vend, t)
            self._set_value_from(value, prop)

    def _calculate_attribute_value(self, vstart, vend, t):
        value = None
        # we handle recursively tuple and list
        if type(vstart) in (tuple, list):

            assert(type(vend) in (tuple, list))
            assert(len(vstart) == len(vend))

            value = []
            for x in range(len(vstart)):
                result = self._calculate_attribute_value(vstart[x], vend[x], t)
                value.append(type(vstart[x])(result))

        elif isinstance(vstart, dict):
                assert(isinstance(vstart, dict))
                assert(len(vstart) == len(vend))
                value = {}
                for item in vstart:
                    result = self._calculate_attribute_value(vstart[item], vend[item], t)
                    value[item]= type(vstart[item])(result)
                return value
		# try to do like a normal value
        else:
            value = type(vstart)(vstart * (1. - t) + vend * t )

        return value

    def start(self):
         if not self.running:
            self.running = True
            getClock().schedule_interval(self._next_frame, 1/60.0)

    def stop(self):
        if self.running:
            self.running = False
            if isinstance(self.animator, ParallelAnimation):
                self.animator.stop(self.widget, animobj=self)
            else:
                self.animator.stop(self.widget)
            return False

    def pause(self):
        pass

    def _next_frame(self,dt):
        if self._frame_pointer <= self.duration and self.running:
            self._frame_pointer += dt
            self._progress = self._frame_pointer/self.duration
            if self._progress > 1.0:
                self._progress = 1.0
            self.update(self._progress)
            return True
        else:
            self.stop()
            return False

    def is_running(self):
        return self.running


class Animation(object):
    '''Animation Class is used to animate any widget. You pass duration of animation
      and the property that has to be animated in that duration. 
      Usage:
            widget = SomeWidget()
            animobj = Animation(duration=5,x=100,style={'bg-color':(1.0,1.0,1.0,1.0)})
            widget.do(animobj)     

    :Parameters:
        `duration` : float, default to 1
            Number of seconds you want the animation to execute.
        `generate_event` : bool, default to True
            Generate on_animation_complete event at the end of the animation

    '''
    def __init__(self,**kwargs):
        kwargs.setdefault('duration', 1.0)
        self.duration = kwargs.get('duration')
        self.children = {}
        self.params = kwargs

    def start(self,widget):
        animobj = self.children[widget]
        animobj.start()

    def stop(self,widget):
        if self.children[widget].generate_event:
            widget.dispatch_event('on_animation_complete', self)
        self._del_child(widget)

    def pause(self):
        pass

    def set_widget(self,widgetx):
        if widgetx in self.children.keys():
            return False
        else:
            new_animobj = AnimationBase(widget=widgetx, key_args=self.params, animator=self)
            self.children[widgetx] = new_animobj
            return True

    def animate(self, *largs):
        '''Animate the widgets specified as parameters to this method.
        :Parameters:
            `widget` : Widget
                A Widget or a group of widgets separated by comma ","
        '''
        for widget in largs:
            self.set_widget(widget)
            self.start(widget)

    def _del_child(self,child):
        del self.children[child]

    def _return_params(self):
        return self.params

    def _set_params(self, key, value):
        self.params[key] = value

    def __add__(self, animation):
        return SequenceAnimation(anim1=self, anim2=animation)

    def __and__(self, animation):
        return ParallelAnimation(anim1=self, anim2=animation)

class ComplexAnimation(Animation):
    # Base class for complex animations like sequences and parallel animations
    def __init__(self, **kwargs):
        super(ComplexAnimation, self).__init__(**kwargs)
        kwargs.setdefault('single_event', False)
        self.single_event = kwargs.get('single_event')
        self.animations = []
        anim1 = kwargs.get('anim1')
        anim2 = kwargs.get('anim2')
        if type(anim1) in (tuple, list):
            for anim in anim1:
                self.animations.append(anim)
        else:
            self.animations.append(anim1)
        self.animations.append(anim2)

    def set_widget(self, widgetx):
        for animation in self.animations:
            try:
                if animation.children[widgetx].is_running():
                    return False
            except:
                continue
        for animation in self.animations:
            new_animobj = AnimationBase(widget=widgetx, key_args=animation.params, animator=self)
            animation.children[widgetx] = new_animobj
        return True

    def generate_single_event(self, value):
        self.single_event = value

class SequenceAnimation(ComplexAnimation):
    #A class for sequential type animation
    def __init__(self, **kwargs):
        super(SequenceAnimation, self).__init__(**kwargs)
        self.anim_counter = 0

    def start(self, widget):
        if self.anim_counter >= len(self.animations):
            if self.single_event:
                widget.dispatch_event('on_animation_complete', self)
            self.anim_counter = 0
            return
        current_anim = self.animations[self.anim_counter]
        current_anim.start(widget)

    def stop(self,widget):
        if self.animations[self.anim_counter].children[widget].generate_event and not self.single_event:
            widget.dispatch_event('on_animation_complete', self)
        self.animations[self.anim_counter]._del_child(widget)
        self.anim_counter += 1
        self.start(widget)

    def __add__(self, animation):
        return SequenceAnimation(anim1=self.animations, anim2=animation)


class ParallelAnimation(ComplexAnimation):
    #A class for Parallel type animation
    def __init__(self, **kwargs):
        super(ParallelAnimation, self).__init__(**kwargs)
        self.dispatch_counter = 0

    def start(self, widget):
        for animation in self.animations:
            animation.start(widget)

    def stop(self,widget, animobj = None):
        self.dispatch_counter += 1
        if self.dispatch_counter == len(self.animations) and self.single_event:
            widget.dispatch_event('on_animation_complete', self)
            self.dispatch_counter = 0
            return
        if animobj.generate_event and not self.single_event:
            widget.dispatch_event('on_animation_complete', self)

    def __and__(self, animation):
        return ParallelAnimation(anim1=self.animations, anim2=animation)

class Delay(Animation):
    def init(self,**kwargs):
        self.duration = kwargs.get('duration')

#Older animation class code

class AnimationAlpha(object):
    """#Collection of animation function, to be used with Animation object.
    """
    @staticmethod
    def ramp(value_from, value_to, length, frame):
        return (1.0 - frame / length) * value_from  +  frame / length * value_to

    @staticmethod
    def sin(value_from, value_to, length, frame):
        return math.sin(math.pi / 2 * (1.0 - frame / length)) * value_from  + \
            math.sin(math.pi / 2  * (frame / length)) * value_to

    @staticmethod
    def bubble(value_from, value_to, length, frame):
        s = -math.pi / 2
        p = math.pi
        return math.sin(s + p * (1.0 - frame / length)) * value_from  + \
            math.sin(s + p  * (frame / length)) * value_to
