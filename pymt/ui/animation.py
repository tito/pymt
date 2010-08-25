'''
Animation package: handle animation with ease in PyMT

Animation
=========

This is an Animation Framework, using which you can animate any
property of an object over a provided duration. You can even animate
CSS property.

Simple Animation
----------------

Example of a widget ::

    widget = SomeWidget()
    animobj = Animation(duration=5,x=100,
                        style={'bg-color':(1.0,1.0,1.0,1.0)})
    widget.do (animobj)

You create a animation class object and pass the object into the widget
that you would like to animate, the object will be animated from its
current state to the state specified in the animation object.

You can also use animate() method of the Animation class to animate
the widget ::

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

    anim1 = Animation(duration=1, x=100)
    anim2 = Animation(duration=2, y = 200)
    anim3 = Animation(duration=1, rotation = 60)

    anim_xyrot = anim1 + anim2 + anim3

    widget.do(anim_xyrot)

This is execute the animations sequentially, "+" is used to execute them
sequentially. First the widget will move to x=100 in 1 sec then it will
move to y=200 in secs and finally rotate clockwise 60 Degress in 1 sec.

You can also run several animations parallel ::

    anim1 = Animation(duration=1, x=100)
    anim2 = Animation(duration=2, y = 200)
    anim3 = Animation(duration=1, rotation = 60)

    anim_xyrot = anim1 & anim2 & anim3

    widget.do(anim_xyrot)

This will execute all the animations on the properties togather.
"&" operator is used to run them parallel
'''

__all__ = ('AnimationAlpha', 'Animation', 'Repeat', 'Delay')

import math
import types
from copy import deepcopy, copy
from pymt.clock import getClock
from pymt.event import EventDispatcher

class AnimationBase(object):
    # This is the base animation object class. Everytime a do or animate
    #  method is called a new animobject is created.
    def __init__(self,**kwargs):
        self.widget = kwargs.get('widget')
        self.params = kwargs.get('key_args')
        self._duration =  float(self.params['duration'])
        self.animator = kwargs.get('animator')

        if 'alpha_function' in self.params:
            f = type(self.params['alpha_function'])
            if f in (types.FunctionType, types.LambdaType):
                f = self.params['alpha_function']
            else:
                f = getattr(AnimationAlpha, self.params['alpha_function'])
        else:
            f = AnimationAlpha.linear
        self.alpha_function = f

        if 'generate_event' in self.params.keys():
            self.generate_event = self.params['generate_event']
        else:
            self.generate_event = True

        self._frame_pointer = 0.0
        self._progress = 0.0
        self._running = False

    def _get_value_from(self, prop):
        if hasattr(self.widget, prop):
            return self.widget.__getattribute__(prop)
        return self.widget.__dict__[prop]

    def _set_value_from(self, value, prop):
        if hasattr(self.widget, prop):
            kwargs = {}
            attr = getattr(self.widget, prop)
            try:
                if type(attr) == dict and type(value) == dict:
                    for k, v in value.iteritems():
                        attr[k] = v
                else:
                    self.widget.__setattr__(prop, value, **kwargs)
            except:
                self.widget.__setattr__(prop, value)
        else:
            self.widget.__dict__[prop] = value

    def update(self, t):
        '''Updates the properties of the widget based on the progress
          pointer t
        '''
        for prop in self._prop_list:
            vstart, vend =  self._prop_list[prop]
            value = self._calculate_attribute_value(vstart, vend, t)
            self._set_value_from(value, prop)

    def _calculate_attribute_value(self, vstart, vend, t):
        '''A recursive function to calculate the resultant value of property.'''
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
        '''Starts animating the AnimationBase Object'''
        if not self._running:
            self._running = True
            getClock().schedule_interval(self._next_frame, 0)

    def stop(self):
        '''Stops animating the AnimationBase Object'''
        if self._running:
            self._running = False
            if isinstance(self.animator, ParallelAnimation):
                self.animator.stop(self.widget, animobj=self)
            else:
                self.animator.stop(self.widget)
            return False

    def pause(self):
        #not yet implemented
        pass

    def _next_frame(self,dt):
        '''Calculate the progress of animation and the frame location
          pointers. This function also decides when to stop the animation.
        '''
        if self._frame_pointer <= self._duration and self._running:
            self._frame_pointer += dt
            self._progress = self._frame_pointer/self._duration
            if self._progress > 1.0:
                self._progress = 1.0
            self.update(self.alpha_function(self._progress))
            return True
        else:
            self.stop()
            return False

    @property
    def running(self):
        return self._running

    @property
    def frame_pointer(self):
        '''Returns the current progress of the animation.
          Ranges from (0.0 to duration)
        '''
        return self._frame_pointer

    @property
    def duration(self):
        '''Returns the animation duration'''
        return self._duration

    def _repopulate_attrib(self, widget):
        '''This function is used by Sequencer to repopluate the properties
           list based on current status of the widget.
        '''
        self.widget = widget
        prop_keys = {}
        for prop in self._prop_list:
            prop_keys[prop] = self._prop_list[prop][1]
        self._prop_list = {}
        for prop in prop_keys:
            cval = self._get_value_from(prop)
            if type(cval) in (tuple, list):
                self._prop_list[prop] = (cval, prop_keys[prop])
        for prop in prop_keys:
            cval = self._get_value_from(prop)
            if type(cval) in (tuple, list):
                self._prop_list[prop] = (cval, prop_keys[prop])
            elif isinstance(cval, dict):
                #contruct a temp dict of only required keys
                temp_dict = {}
                for each_key in prop_keys[prop]:
                    temp_dict[each_key] = cval[each_key]
                self._prop_list[prop] = (temp_dict, prop_keys[prop])
            else:
                self._prop_list[prop] = (cval,prop_keys[prop])

class AbsoluteAnimationBase(AnimationBase):
    #Animation Objects of sort MoveTo, RotateTo etc depend on this class
    def __init__(self,**kwargs):
        super(AbsoluteAnimationBase, self).__init__(**kwargs)
        self._prop_list = {}
        for item in self.params:
            if item not in ('duration', 'anim1', 'anim2', 'generate_event',
                            'single_event', 'type', 'alpha_function', 'd', 'f'):
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

        #Store state values for repeating
        self._initial_state = deepcopy(self._prop_list)

    def reset(self):
        #repeating a absolute animation doesnt make sense atleast for now
        pass

class DeltaAnimationBase(AnimationBase):
    #Animation Objects of sort MoveBy, RotateBy etc depend on this class
    def __init__(self,**kwargs):
        super(DeltaAnimationBase, self).__init__(**kwargs)
        self._prop_list = {}
        for item in self.params:
            if item not in ('duration', 'anim1', 'anim2', 'generate_event',
                            'single_event', 'type', 'alpha_function', 'd', 'f'):
                self._prop_list[item] = self.params[item]

        #save proplist for repeatation
        self._saved_prop_list = {}
        self._saved_prop_list = deepcopy(self._prop_list)

        for prop in self._prop_list:
            cval = self._get_value_from(prop)
            if type(cval) in (tuple, list):
                self._prop_list[prop] = (cval, self._update_list(cval , self._prop_list[prop]))
            elif isinstance(cval, dict):
                #contruct a temp dict of only required keys
                temp_dict = {}
                for each_key in self._prop_list[prop]:
                    temp_dict[each_key] = cval[each_key]
                self._prop_list[prop] = (temp_dict, self._update_dict(temp_dict, self._prop_list[prop]))
            else:
                self._prop_list[prop] = (cval,cval+self._prop_list[prop])

    def reset(self):
        '''used by Repeater to reset the property list'''
        self._frame_pointer = 0.0
        self._progress = 0.0
        self._running = False
        for prop in self._saved_prop_list:
            cval = self._get_value_from(prop)
            if type(cval) in (tuple, list):
                self._prop_list[prop] = (cval, self._update_list(cval, self._saved_prop_list[prop]))
            elif isinstance(cval, dict):
                #contruct a temp dict of only required keys
                temp_dict = {}
                for each_key in self._saved_prop_list[prop]:
                    temp_dict[each_key] = cval[each_key]
                self._prop_list[prop] = (temp_dict,  self._update_dict(temp_dict, self._saved_prop_list[prop]))
            else:
                self._prop_list[prop] = (cval,cval+self._saved_prop_list[prop])

    def _update_list(self, ip_list, op_list):
        '''Used by reset function to update a list type data'''
        temp_list = []
        for i in range(0, len(ip_list)):
            temp_list.append(ip_list[i]+op_list[i])
        return  temp_list

    def _update_dict(self, ip_dict, op_dict):
        '''Used by reset function to update a dict type data'''
        temp_dict = {}
        for key in ip_dict.iterkeys():
            if type(ip_dict[key]) in (tuple, list):
                temp_dict[key] = self._update_list(ip_dict[key], op_dict[key])
            else:
                temp_dict[key] = ip_dict[key]+op_dict[key]
        return  temp_dict

class Animation(EventDispatcher):
    '''Animation Class is used to animate any widget. You pass duration of
    animation and the property that has to be animated in that duration.

    Usage ::

        widget = SomeWidget()
        animobj = Animation(duration=5, x=100,
                            style={'bg-color':(1.0,1.0,1.0,1.0)})
        widget.do(animobj)

    :Parameters:
        `duration` or `d`: float, default to 1
            Number of seconds you want the animation to execute.
        `generate_event` : bool, default to True
            Generate on_animation_complete event at the end of the
            animation
        `type` : str, default to absolute
            Specifies what type of animation we are defining, Absolute
            or Delta
        `alpha_function` or `f`: str, default to AnimationAlpha.linear
            Specifies which kind of time variation function to use

    :Events:
        `on_start`
            Fired when animation starts
        `on_complete`
            Fired when animation completes

    '''
    def __init__(self,**kwargs):
        super(Animation, self).__init__()
        kwargs.setdefault('type', 'absolute')

        if 'd' in kwargs and 'duration' in kwargs:
            raise Exception('d and duration are in Animation(), use only one.')
        if 'f' in kwargs and 'alpha_function' in kwargs:
            raise Exception('f and alpha_function are in Animation(), use only one.')

        if 'd' in kwargs:
            kwargs['duration'] = kwargs['d']
            del kwargs['d']
        if 'duration' in kwargs:
            self._duration = kwargs.get('duration')
        else:
            self._duration = 1.0
        kwargs['duration'] = self._duration

        if 'f' in kwargs:
            kwargs['alpha_function'] = kwargs['f']
            del kwargs['f']

        self.children = {}
        self.params = kwargs
        self._animation_type = kwargs.get('type')

        self.register_event_type('on_start')
        self.register_event_type('on_complete')

    def start(self, widget):
        '''Starts animating the widget. This function should not be used
          by the user directly. Users have to use do() method of the
          widget to animate.
        '''
        animobj = self.children[widget]
        animobj.start()
        self.dispatch_event('on_start', widget)
        return animobj

    def stop(self, widget):
        '''Stops animating the widget and raises a event.'''
        if self.children[widget].generate_event:
            widget.dispatch_event('on_animation_complete', self)
            self.dispatch_event('on_complete', widget)
        self._del_child(widget)

    def pause(self):
        pass

    def reset(self, widget):
        '''Calls AnimationBase objects reset function.'''
        self.children[widget].reset()

    def set_widget(self, widgetx):
        '''Creates a new animationBase object and sets the widget to it for
        animation. This is a internal function and should not be used by user.

        :Parameters:
            `widget` : MTWidget, default is None
                Indicates which widget is to be set.

        '''
        if widgetx in self.children.keys():
            return False
        else:
            if self._animation_type == 'absolute':
                new_animobj = AbsoluteAnimationBase(widget=widgetx, key_args=self.params, animator=self)
            else:
                new_animobj = DeltaAnimationBase(widget=widgetx, key_args=self.params, animator=self)
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
        '''Deletes a child from the list'''
        del self.children[child]

    def _return_params(self):
        '''Returns the animation parameters.'''
        return self.params

    def _repopulate_attrib(self, widget):
        '''Calls calls repopulate function of the animationBase object'''
        self.children[widget]._repopulate_attrib(widget)

    def _set_params(self, key, value):
        '''reset the value for the params list'''
        self.params[key] = value

    def __add__(self, animation):
        return SequenceAnimation(anim1=self, anim2=animation)

    def __and__(self, animation):
        return ParallelAnimation(anim1=self, anim2=animation)

    def on_start(self, widget):
        pass

    def on_complete(self, widget):
        pass

class ComplexAnimation(Animation):
    # Base class for complex animations like sequences and parallel
    # animations
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
        '''Used by complex animations like Parallel and Sequential to set
          widgets to its child animations
        '''
        for animation in self.animations:
            try:
                if animation.children[widgetx].running():
                    return False
            except:
                continue
        for animation in self.animations:
            if animation._animation_type == 'absolute':
                new_animobj = AbsoluteAnimationBase(widget=widgetx, key_args=animation.params, animator=self)
            else:
                new_animobj = DeltaAnimationBase(widget=widgetx, key_args=animation.params, animator=self)
            animation.children[widgetx] = new_animobj
        return True

    def generate_single_event(self, value):
        '''If a user wants to generate only one event for the entire complex
        animation he can use this function.

        :Parameters:
            `value` : bool
                True or False value
        '''
        self.single_event = value

class SequenceAnimation(ComplexAnimation):
    #A class for sequential type animation
    def __init__(self, **kwargs):
        super(SequenceAnimation, self).__init__(**kwargs)
        self.anim_counter = 0

    def start(self, widget):
        '''Starts the sequential animation'''
        if self.anim_counter == 0:
            self.dispatch_event('on_start', widget)
        if self.anim_counter >= len(self.animations):
            self.anim_counter = 0
            self.dispatch_event('on_complete', widget)
            if self.single_event:
                widget.dispatch_event('on_animation_complete', self)
            return
        current_anim = self.animations[self.anim_counter]
        current_anim.start(widget)
        return self

    def stop(self, widget = None):
        '''Stops the sequential animation'''
        if widget == None:
            widget = self.animations[self.anim_counter].children.keys()[0]
        if self.animations[self.anim_counter].children[widget].generate_event and not self.single_event:
            widget.dispatch_event('on_animation_complete', self)
        #self.animations[self.anim_counter]._del_child(widget)
        self.anim_counter += 1
        if self.anim_counter < len(self.animations):
            self.animations[self.anim_counter]._repopulate_attrib(widget)
        self.start(widget)

    def reset(self, widget):
        '''Resets the sequential animation'''
        self.anim_counter = 0
        for animation in self.animations:
            animation.reset(widget)

    def __add__(self, animation):
        '''Operator overloading + symbol is overloaded'''
        return SequenceAnimation(anim1=self.animations, anim2=animation)


class ParallelAnimation(ComplexAnimation):
    #A class for Parallel type animation
    def __init__(self, **kwargs):
        super(ParallelAnimation, self).__init__(**kwargs)
        self.dispatch_counter = 0

    def start(self, widget):
        '''Starts the parallel animation'''
        if self.dispatch_counter == 0:
            self.dispatch_event('on_start', widget)
        for animation in self.animations:
            animation.start(widget)
        return self

    def stop(self, widget = None, animobj = None):
        '''Stops the parallel animation'''
        if widget == None:
            widget = self.animations[self.dispatch_counter].children.keys()[0]

        if animobj == None:
            animobj = self.animations[self.dispatch_counter].children[widget]

        self.dispatch_counter += 1        
        if self.dispatch_counter == len(self.animations):
            self.dispatch_event('on_complete', widget)
            if self.single_event:
                widget.dispatch_event('on_animation_complete', self)
            self.dispatch_counter = 0
            return

        if animobj.generate_event and not self.single_event:
            widget.dispatch_event('on_animation_complete', self)

    def reset(self, widget):
        '''Resets the parallel animation'''
        self.dispatch_counter = 0
        for animation in self.animations:
            animation.reset(widget)

    def __and__(self, animation):
        '''Operator overloading & symbol is overloaded'''
        return ParallelAnimation(anim1=self.animations, anim2=animation)


#Controller Classes

class Repeat(EventDispatcher):
    '''Repeat Controller class is used to repeat a particular animations. It
    repeats n times as specified or repeats indefinately if number of times
    to repeat is not specified. Repeat class is useful only for delta
    animations.

    Usage ::

        widget = SomeWidget()
        animobj = Animation(duration=5, x=100,
                            style={'bg-color':(1.0,1.0,1.0,1.0)})
        rept = Repeat(animobj, times=5) #Repeats 5 times
        rept_n = Repeat(animobj) #Repeats indefinately

    :Parameters:
        `times` : integer, default to infinity
            Number of times to repeat the Animation

    :Events:
        `on_start`
            Fired when animation starts
        `on_complete`
            Fired when animation completes
        `on_repeat`
            Fired on every repetition. It also returns what is the current
            repetition count.

    '''
    def __init__(self, animation, **kwargs):
        super(Repeat, self).__init__()
        kwargs.setdefault('times', -1)
        self.animations = animation
        self.single_event = True
        self._repeat_counter = 0
        self._times = kwargs.get('times')
        self.register_event_type('on_start')
        self.register_event_type('on_repeat')
        self.register_event_type('on_complete')
        @self.animations.event
        def on_complete(widget):
            self.repeat(widget)

    def set_widget(self, widgetx):
        '''Called by the widget to set the widget which has to be animated'''
        self.animations.set_widget(widgetx)
        return True

    def start(self, widget):
        '''Starts the animation'''
        if self._repeat_counter == 0:
            self.dispatch_event('on_start', widget)
        self.animations.start(widget)

    def stop(self,widget):
        '''Stops the animation'''
        widget.dispatch_event('on_animation_complete', self)
        self.dispatch_event('on_complete', widget)
        self._repeat_counter = 0
        if not (isinstance(self.animations, ParallelAnimation) or isinstance(self.animations, SequenceAnimation)):
            self.animations._del_child(widget)

    def repeat(self, widget):
        '''Internal function used by the Repeat controller to check for
          repetitions
        '''
        self._repeat_counter += 1
        self.dispatch_event('on_repeat', widget , self._repeat_counter)
        if self._times == -1:
            self.animations.reset(widget)
            self.start(widget)
        elif self._repeat_counter < self._times:
            self.animations.reset(widget)
            self.start(widget)
        else:
            self.stop(widget)

    def on_start(self, widget):
        pass

    def on_complete(self, widget):
        pass

    def on_repeat(self, widget, count):
        pass

class Delay(Animation):
    '''Delay class is used to introduce delay in your animations.
    You can provide the duration in your animation class creation

    Usage ::

        widget = SomeWidget()
        moveX = Animation(duration=5, x=100,
                          style={'bg-color':(1.0,1.0,1.0,1.0)})
        delay5 = Delay(duration=5)
        animobj = delay5 + moveX
        # This will wait for 5 secs and then start animating moveX

    :Parameters:
        `duration` : float, default to 1
            Number of seconds you want delay.

    '''
    def __init__(self, **kwargs):
        super(Delay, self).__init__(**kwargs)
        self._duration = kwargs.get('duration')


class AnimationAlpha(object):
    '''Collection of animation function, to be used with Animation object.
        Easing Functions ported into PyMT from Clutter Project
        http://www.clutter-project.org/docs/clutter/stable/ClutterAlpha.html
    '''
    @staticmethod
    def linear(progress):
        '''See documentation at http://pymt.eu/wiki/DevGuide/EasingFunctions#linear'''
        return progress

    @staticmethod
    def ease_in_quad(progress):
        '''See documentation at http://pymt.eu/wiki/DevGuide/EasingFunctions#ease_in_quad'''
        return progress * progress

    @staticmethod
    def ease_out_quad(progress):
        '''See documentation at http://pymt.eu/wiki/DevGuide/EasingFunctions#ease_out_quad'''
        return -1.0 * progress * (progress - 2.0)

    @staticmethod
    def ease_in_out_quad(progress):
        '''See documentation at http://pymt.eu/wiki/DevGuide/EasingFunctions#ease_in_out_quad'''
        p = progress * 2
        if p < 1 :
           return 0.5 * p * p
        p -= 1.0
        return -0.5 * (p * (p - 2.0) - 1.0)

    @staticmethod
    def ease_in_cubic(progress):
        '''See documentation at http://pymt.eu/wiki/DevGuide/EasingFunctions#ease_in_cubic'''
        return progress * progress * progress

    @staticmethod
    def ease_out_cubic(progress):
        '''See documentation at http://pymt.eu/wiki/DevGuide/EasingFunctions#ease_out_cubic'''
        p = progress - 1.0
        return p * p * p + 1.0

    @staticmethod
    def ease_in_out_cubic(progress):
        '''See documentation at http://pymt.eu/wiki/DevGuide/EasingFunctions#ease_in_out_cubic'''
        p = progress * 2
        if p < 1 :
            return 0.5 * p * p * p
        p -= 2
        return 0.5 * (p * p * p + 2.0)

    @staticmethod
    def ease_in_quart(progress):
        '''See documentation at http://pymt.eu/wiki/DevGuide/EasingFunctions#ease_in_quart'''
        return progress * progress * progress * progress

    @staticmethod
    def ease_out_quart(progress):
        '''See documentation at http://pymt.eu/wiki/DevGuide/EasingFunctions#ease_out_quart'''
        p = progress - 1.0
        return -1.0 * (p * p * p * p - 1.0);

    @staticmethod
    def ease_in_out_quart(progress):
        '''See documentation at http://pymt.eu/wiki/DevGuide/EasingFunctions#ease_in_out_quart'''
        p = progress * 2
        if p < 1 :
            return 0.5 * p * p * p * p
        p -= 2
        return -0.5 * (p * p * p * p - 2.0)

    @staticmethod
    def ease_in_quint(progress):
        '''See documentation at http://pymt.eu/wiki/DevGuide/EasingFunctions#ease_in_quint'''
        return progress * progress * progress * progress * progress

    @staticmethod
    def ease_out_quint(progress):
        '''See documentation at http://pymt.eu/wiki/DevGuide/EasingFunctions#ease_out_quint'''
        p = progress - 1.0
        return p * p * p * p * p + 1.0;

    @staticmethod
    def ease_in_out_quint(progress):
        '''See documentation at http://pymt.eu/wiki/DevGuide/EasingFunctions#ease_in_out_quint'''
        p = progress * 2
        if p < 1 :
            return 0.5 * p * p * p * p * p
        p -= 2.0
        return 0.5 * (p * p * p * p * p + 2.0)

    @staticmethod
    def ease_in_sine(progress):
        '''See documentation at http://pymt.eu/wiki/DevGuide/EasingFunctions#ease_in_sine'''
        return -1.0 * math.cos(progress * (math.pi/2.0)) + 1.0

    @staticmethod
    def ease_out_sine(progress):
        '''See documentation at http://pymt.eu/wiki/DevGuide/EasingFunctions#ease_out_sine'''
        return math.sin(progress * (math.pi/2.0))

    @staticmethod
    def ease_in_out_sine(progress):
        '''See documentation at http://pymt.eu/wiki/DevGuide/EasingFunctions#ease_in_out_sine'''
        return -0.5 * (math.cos(math.pi * progress) - 1.0)

    @staticmethod
    def ease_in_expo(progress):
        '''See documentation at http://pymt.eu/wiki/DevGuide/EasingFunctions#ease_in_expo'''
        if progress == 0:
            return 0.0
        return math.pow(2, 10 * (progress - 1.0))

    @staticmethod
    def ease_out_expo(progress):
        '''See documentation at http://pymt.eu/wiki/DevGuide/EasingFunctions#ease_out_expo'''
        if progress == 1.0:
            return 1.0
        return  -math.pow(2, -10 * progress) + 1.0

    @staticmethod
    def ease_in_out_expo(progress):
        '''See documentation at http://pymt.eu/wiki/DevGuide/EasingFunctions#ease_in_out_expo'''
        if progress == 0:
            return 0.0
        if progress == 1.:
            return 1.0
        p = progress * 2
        if p < 1:
            return 0.5 * math.pow(2, 10 * (p - 1.0))
        p -= 1.0
        return 0.5 * (-math.pow(2, -10 * p) + 2.0)

    @staticmethod
    def ease_in_circ(progress):
        '''See documentation at http://pymt.eu/wiki/DevGuide/EasingFunctions#ease_in_circ'''
        return -1.0 * (math.sqrt(1.0 - progress * progress) - 1.0)

    @staticmethod
    def ease_out_circ(progress):
        '''See documentation at http://pymt.eu/wiki/DevGuide/EasingFunctions#ease_out_circ'''
        p = progress - 1.0
        return math.sqrt(1.0 - p * p)

    @staticmethod
    def ease_in_out_circ(progress):
        '''See documentation at http://pymt.eu/wiki/DevGuide/EasingFunctions#ease_in_out_circ'''
        p = progress * 2
        if p < 1:
            return -0.5 * (math.sqrt(1.0 - p * p) - 1.0)
        p -= 2.0
        return 0.5 * (math.sqrt(1.0 - p * p) + 1.0)

    @staticmethod
    def ease_in_elastic(progress):
        '''See documentation at http://pymt.eu/wiki/DevGuide/EasingFunctions#ease_in_elastic'''
        p = .3
        s = p / 4.0
        q = progress
        if q == 1:
            return 1.0
        q -= 1.0
        return -(math.pow(2, 10 * q) * math.sin((q - s) * (2 * math.pi) / p))

    @staticmethod
    def ease_out_elastic(progress):
        '''See documentation at http://pymt.eu/wiki/DevGuide/EasingFunctions#ease_out_elastic'''
        p = .3
        s = p / 4.0
        q = progress
        if q == 1:
            return 1.0
        return math.pow(2, -10 * q) * math.sin ((q - s) * (2 * math.pi) / p) + 1.0

    @staticmethod
    def ease_in_out_elastic(progress):
        '''See documentation at http://pymt.eu/wiki/DevGuide/EasingFunctions#ease_in_out_elastic'''
        p = .3 * 1.5
        s = p / 4.0
        q = progress * 2
        if q == 2:
            return 1.0
        if q < 1:
            q -= 1.0;
            return -.5 * (math.pow(2, 10 * q) * math.sin((q - s) * (2.0 *math.pi) / p));
        else:
            q -= 1.0;
            return math.pow(2, -10 * q) * math.sin((q - s) * (2.0 * math.pi) / p) * .5 + 1.0;

    @staticmethod
    def ease_in_back(progress):
        '''See documentation at http://pymt.eu/wiki/DevGuide/EasingFunctions#ease_in_back'''
        return progress * progress * ((1.70158 + 1.0) * progress - 1.70158)

    @staticmethod
    def ease_out_back(progress):
        '''See documentation at http://pymt.eu/wiki/DevGuide/EasingFunctions#ease_out_back'''
        p = progress - 1.0
        return p * p * ((1.70158 + 1) * p + 1.70158) + 1.0

    @staticmethod
    def ease_in_out_back(progress):
        '''See documentation at http://pymt.eu/wiki/DevGuide/EasingFunctions#ease_in_out_back'''
        p = progress * 2.
        s = 1.70158 * 1.525
        if p < 1:
            return 0.5 * (p * p * ((s + 1.0) * p - s))
        p -= 2.0
        return 0.5 * (p * p * ((s + 1.0) * p + s) + 2.0)

    @staticmethod
    def _ease_out_bounce_internal(t, d):
        p = t / d
        if p < (1.0 / 2.75):
            return 7.5625 * p * p
        elif p < (2.0 / 2.75):
            p -= (1.5 / 2.75)
            return 7.5625 * p * p + .75
        elif p < (2.5 / 2.75):
            p -= (2.25 / 2.75)
            return 7.5625 * p * p + .9375
        else:
            p -= (2.625 / 2.75)
            return 7.5625 * p * p + .984375

    @staticmethod
    def _ease_in_bounce_internal(t, d):
        return 1.0 - AnimationAlpha._ease_out_bounce_internal(d - t, d)

    @staticmethod
    def ease_in_bounce(progress):
        '''See documentation at http://pymt.eu/wiki/DevGuide/EasingFunctions#ease_in_bounce'''
        return AnimationAlpha._ease_in_bounce_internal(progress, 1.)

    @staticmethod
    def ease_out_bounce(progress):
        '''See documentation at http://pymt.eu/wiki/DevGuide/EasingFunctions#ease_out_bounce'''
        return AnimationAlpha._ease_out_bounce_internal(progress, 1.)

    @staticmethod
    def ease_in_out_bounce(progress):
        '''See documentation at http://pymt.eu/wiki/DevGuide/EasingFunctions#ease_in_out_bounce'''
        p = progress * 2
        if p < 1.:
            return AnimationAlpha._ease_in_bounce_internal(progress * 2.0, 1.) * 0.5
        return AnimationAlpha._ease_out_bounce_internal(progress * 2.0 - 1., 1.) * 0.5 + 1.0 * 0.5
