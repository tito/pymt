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

__all__ = ['AnimationAlpha', 'Animation', 'Repeat', 'Delay']

import math
from copy import deepcopy, copy
from ..clock import getClock
from ..event import EventDispatcher

class AnimationBase(object):
    # This is the base animation object class. Everytime a do or animate method is called 
    # a new animobject is created.
    def __init__(self,**kwargs):
        self.widget = kwargs.get('widget')
        self.params = kwargs.get('key_args')
        self.duration =  float(self.params['duration'])
        self.animator = kwargs.get('animator')

        if 'f' in self.params.keys():
            f = getattr(AnimationAlpha, self.params['f'])
        elif 'alpha_function' in self.params.keys(): 
            f = getattr(AnimationAlpha, self.params['alpha_function'])
        else:
            f = AnimationAlpha.linear
        self.alpha_function = f

        if "generate_event" in self.params.keys():
            self.generate_event = self.params['generate_event']
        else:
            self.generate_event = True

        self._frame_pointer = 0.0
        self._progress = 0.0
        self.running = False
    
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
            self.update(self.alpha_function(self._progress, self))
            return True
        else:
            self.stop()
            return False

    def is_running(self):
        return self.running
    
    def get_frame_pointer(self):
        return self._frame_pointer
    
    def get_duration(self):
        return self.duration

    def _repopulate_attrib(self, widget):
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
            if item not in ("duration", "anim1", "anim2", "generate_event", "single_event", "animation_type", "alpha_function", "d", "f"):
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
        self._frame_pointer = 0.0
        self._progress = 0.0
        self.running = False
        self._prop_list = self._initial_state

class DeltaAnimationBase(AnimationBase):
    #Animation Objects of sort MoveBy, RotateBy etc depend on this class
    def __init__(self,**kwargs):
        super(DeltaAnimationBase, self).__init__(**kwargs)
        self._prop_list = {}
        for item in self.params:
            if item not in ("duration", "anim1", "anim2", "generate_event", "single_event", "animation_type", "alpha_function", "d", "f"):
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
        self._frame_pointer = 0.0
        self._progress = 0.0
        self.running = False
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
        temp_list = []
        for i in range(0, len(ip_list)):
            temp_list.append(ip_list[i]+op_list[i])
        return  temp_list
    
    def _update_dict(self, ip_dict, op_dict):
        temp_dict = {}
        for key in ip_dict.keys():
            if type(ip_dict[key]) in (tuple, list):
                temp_dict[key] = self._update_list(ip_dict[key], op_dict[key])
            else:
                temp_dict[key] = ip_dict[key]+op_dict[key]
        return  temp_dict



class Animation(EventDispatcher):
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
        `animation_type` : str, default to absolute
            Specifies what type of animation we are defining, Absolute or Delta
        `alpha_function` : str, default to AnimationAlpha.linear
            Specifies which kind of time variation function to use
    '''
    def __init__(self,**kwargs):
        super(Animation, self).__init__()
        kwargs.setdefault('duration', 1.0)
        kwargs.setdefault('d', 1.0)
        kwargs.setdefault('animation_type', "absolute")
        if kwargs.get('d'):
            self.duration = kwargs.get('d')
        else:
            self.duration = kwargs.get('duration')
        self.children = {}
        self.params = kwargs
        self._animation_type = kwargs.get('animation_type')
        self._repeater =  None

        self.register_event_type('on_start')
        self.register_event_type('on_complete')

    def start(self, widget, repeater=None):
        self._repeater = repeater
        animobj = self.children[widget]
        animobj.start()
        self.dispatch_event('on_start', widget)

    def stop(self, widget):
        if self.children[widget].generate_event:
            widget.dispatch_event('on_animation_complete', self)
            self.dispatch_event('on_complete', widget)
        if self._repeater is not None:
            self._repeater.repeat(widget)
        else:
            self._del_child(widget)

    def pause(self):
        pass

    def reset(self, widget):
        self.children[widget].reset()

    def set_widget(self, widgetx):
        if widgetx in self.children.keys():
            return False
        else:
            if self._animation_type == "absolute":
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
        del self.children[child]

    def _return_params(self):
        return self.params

    def _repopulate_attrib(self, widget):
        self.children[widget]._repopulate_attrib(widget)

    def _set_params(self, key, value):
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
        self._repeater = None

    def set_widget(self, widgetx):
        for animation in self.animations:
            try:
                if animation.children[widgetx].is_running():
                    return False
            except:
                continue
        for animation in self.animations:
            if animation._animation_type == "absolute":
                new_animobj = AbsoluteAnimationBase(widget=widgetx, key_args=animation.params, animator=self)
            else:
                new_animobj = DeltaAnimationBase(widget=widgetx, key_args=animation.params, animator=self)
            animation.children[widgetx] = new_animobj
        return True

    def generate_single_event(self, value):
        self.single_event = value

class SequenceAnimation(ComplexAnimation):
    #A class for sequential type animation
    def __init__(self, **kwargs):
        super(SequenceAnimation, self).__init__(**kwargs)
        self.anim_counter = 0

    def start(self, widget, repeater=None):
        if self.anim_counter == 0:
            self.dispatch_event('on_start', widget)
        self._repeater = repeater
        if self.anim_counter >= len(self.animations):
            self.anim_counter = 0
            self.dispatch_event('on_complete', widget)
            if self.single_event:                
                widget.dispatch_event('on_animation_complete', self)
                if self._repeater is not None:
                    self._repeater.repeat(widget)            
            return
        current_anim = self.animations[self.anim_counter]
        current_anim.start(widget)

    def stop(self,widget):
        if self.animations[self.anim_counter].children[widget].generate_event and not self.single_event:
            widget.dispatch_event('on_animation_complete', self)
        if self._repeater is None:
            self.animations[self.anim_counter]._del_child(widget)
        self.anim_counter += 1
        if self.anim_counter < len(self.animations):
            self.animations[self.anim_counter]._repopulate_attrib(widget)
        self.start(widget, repeater=self._repeater)

    def reset(self, widget):
        self.anim_counter = 0
        for animation in self.animations:
            animation.reset(widget)

    def __add__(self, animation):
        return SequenceAnimation(anim1=self.animations, anim2=animation)


class ParallelAnimation(ComplexAnimation):
    #A class for Parallel type animation
    def __init__(self, **kwargs):
        super(ParallelAnimation, self).__init__(**kwargs)
        self.dispatch_counter = 0

    def start(self, widget, repeater=None):
        self._repeater = repeater
        if self.dispatch_counter == 0:
            self.dispatch_event('on_start', widget)
        for animation in self.animations:
            animation.start(widget)

    def stop(self,widget, animobj = None):
        self.dispatch_counter += 1
        if self.dispatch_counter == len(self.animations):
            self.dispatch_event('on_complete', widget)
            if self.single_event:
                widget.dispatch_event('on_animation_complete', self)
            self.dispatch_counter = 0
            if self._repeater is not None:
                self._repeater.repeat(widget)            
            return
        if animobj.generate_event and not self.single_event:
            widget.dispatch_event('on_animation_complete', self)
    
    def reset(self, widget):
        self.dispatch_counter = 0
        for animation in self.animations:
            animation.reset(widget)

    def __and__(self, animation):
        return ParallelAnimation(anim1=self.animations, anim2=animation)


#Controller Classes

class Repeat(ComplexAnimation):
    '''Repeat Controller class is used to repeat a particular animations. It repeats
      n times as specified or repeats indefinately if number of times to repeat is not 
      specified. 
      Usage:
            widget = SomeWidget()
            animobj = Animation(duration=5,x=100,style={'bg-color':(1.0,1.0,1.0,1.0)})
            rept = Repeat(animobj, times=5) #Repeats 5 times
            rept_n = Repeat(animobj) #Repeats indefinately            

    :Parameters:
        `times` : integer, default to infinity
            Number of times to repeat the Animation
    '''
    def __init__(self, animation, **kwargs):
        super(Repeat, self).__init__(**kwargs)
        kwargs.setdefault('times', -1)
        self.animations = animation
        self.single_event = True
        self._repeat_counter = 0
        self._times = kwargs.get('times')

    def set_widget(self, widgetx):
        self.animations.set_widget(widgetx)
        if isinstance(self.animations, ParallelAnimation) or isinstance(self.animations, SequenceAnimation):
            self.animations.generate_single_event(True)
        return True

    def start(self, widget):
        self.animations.start(widget, repeater=self)

    def stop(self,widget):
        widget.dispatch_event('on_animation_complete', self)
        self._repeat_counter = 0
        if not (isinstance(self.animations, ParallelAnimation) or isinstance(self.animations, SequenceAnimation)):
            self.animations._del_child(widget)

    def repeat(self, widget):
        self._repeat_counter += 1
        if self._times == -1:
            self.animations.reset(widget)
            self.start(widget)
        elif self._repeat_counter < self._times:
            self.animations.reset(widget)
            self.start(widget)
        else:
            self.stop(widget)

class Delay(Animation):
    def init(self,**kwargs):
        self.duration = kwargs.get('duration')

#Older animation class code

class AnimationAlpha(object):
    """Collection of animation function, to be used with Animation object.
        Easing Functions ported into PyMT from Clutter Project
        http://www.clutter-project.org/docs/clutter/stable/ClutterAlpha.html
    """
    @staticmethod
    def linear(progress, animation):
        return progress

    @staticmethod
    def ease_in_quad(progress, animation):
        return progress*progress

    @staticmethod
    def ease_out_quad(progress, animation):
        return -1.0 * progress * (progress - 2.0)

    @staticmethod
    def ease_in_out_quad(progress, animation):
        t = animation.get_frame_pointer()
        d = animation.get_duration()
        p = t / (d / 2.0)
        if p < 1 :
           return 0.5 * p * p
        p -= 1.0
        return -0.5 * (p * (p - 2.0) - 1.0)

    @staticmethod
    def ease_in_cubic(progress, animation):
        return progress * progress * progress

    @staticmethod
    def ease_out_cubic(progress, animation):
        t = animation.get_frame_pointer()
        d = animation.get_duration()
        p = t / d - 1.0
        return p * p * p + 1.0

    @staticmethod
    def ease_in_out_cubic(progress, animation):
        t = animation.get_frame_pointer()
        d = animation.get_duration()
        p = t / (d / 2.0)
        if p < 1 :
            return 0.5 * p * p * p
        p -= 2
        return 0.5 * (p * p * p + 2.0)

    @staticmethod
    def ease_in_quart(progress, animation):
        return progress * progress * progress * progress

    @staticmethod
    def ease_out_quart(progress, animation):
        t = animation.get_frame_pointer()
        d = animation.get_duration()
        p = t / d - 1.0
        return -1.0 * (p * p * p * p - 1.0);

    @staticmethod
    def ease_in_out_quart(progress, animation):
        t = animation.get_frame_pointer()
        d = animation.get_duration()
        p = t / (d / 2.0)
        if p < 1 :
            return 0.5 * p * p * p * p
        p -= 2
        return -0.5 * (p * p * p * p - 2.0)

    @staticmethod
    def ease_in_quint(progress, animation):
        return progress * progress * progress * progress * progress

    @staticmethod
    def ease_out_quint(progress, animation):
        t = animation.get_frame_pointer()
        d = animation.get_duration()
        p = t / d - 1.0
        return p * p * p * p * p + 1.0;

    @staticmethod
    def ease_in_out_quint(progress, animation):
        t = animation.get_frame_pointer()
        d = animation.get_duration()
        p = t / (d / 2.0)
        if p < 1 :
            return 0.5 * p * p * p * p * p
        p -= 2.0
        return 0.5 * (p * p * p * p * p + 2.0)

    @staticmethod
    def ease_in_sine(progress, animation):
        t = animation.get_frame_pointer()
        d = animation.get_duration()
        return -1.0 * math.cos(t / d * (math.pi/2.0)) + 1.0

    @staticmethod
    def ease_out_sine(progress, animation):
        t = animation.get_frame_pointer()
        d = animation.get_duration()
        return math.sin(t / d * (math.pi/2.0))

    @staticmethod
    def ease_in_out_sine(progress, animation):
        t = animation.get_frame_pointer()
        d = animation.get_duration()
        return -0.5 * (math.cos(math.pi * t / d) - 1.0)

    @staticmethod
    def ease_in_expo(progress, animation):
        t = animation.get_frame_pointer()
        d = animation.get_duration()
        if t == 0:
            return 0.0            
        return math.pow(2, 10 * (t / d - 1.0))

    @staticmethod
    def ease_out_expo(progress, animation):
        t = animation.get_frame_pointer()
        d = animation.get_duration()
        if t == d:
            return 1.0            
        return  -math.pow(2, -10 * t / d) + 1.0

    @staticmethod
    def ease_in_out_expo(progress, animation):
        t = animation.get_frame_pointer()
        d = animation.get_duration()
        if t == 0:
            return 0.0
        if t == d:
            return 1.0
        p = t / (d / 2.0)
        if p < 1:
            return 0.5 * math.pow(2, 10 * (p - 1.0))
        p -= 1.0
        return 0.5 * (-math.pow(2, -10 * p) + 2.0)

    @staticmethod
    def ease_in_circ(progress, animation):
        return -1.0 * (math.sqrt(1.0 - progress * progress) - 1.0)

    @staticmethod
    def ease_out_circ(progress, animation):
        t = animation.get_frame_pointer()
        d = animation.get_duration()
        p = t / d - 1.0
        return math.sqrt(1.0 - p * p)

    @staticmethod
    def ease_in_out_circ(progress, animation):
        t = animation.get_frame_pointer()
        d = animation.get_duration()
        p = t / (d / 2)
        if p < 1:
            return -0.5 * (math.sqrt(1.0 - p * p) - 1.0)
        p -= 2.0
        return 0.5 * (math.sqrt(1.0 - p * p) + 1.0)

    @staticmethod
    def ease_in_elastic(progress, animation):
        t = animation.get_frame_pointer()
        d = animation.get_duration()
        p = d * .3
        s = p / 4.0
        q = t / d
        if q == 1:
            return 1.0
        q -= 1.0
        return -(math.pow(2, 10 * q) * math.sin((q * d - s) * (2 * math.pi) / p))

    @staticmethod
    def ease_out_elastic(progress, animation):
        t = animation.get_frame_pointer()
        d = animation.get_duration()
        p = d * .3
        s = p / 4.0
        q = t / d
        if q == 1:
            return 1.0
        return math.pow(2, -10 * q) * math.sin ((q * d - s) * (2 * math.pi) / p) + 1.0

    @staticmethod
    def ease_in_out_elastic(progress, animation):
        t = animation.get_frame_pointer()
        d = animation.get_duration()
        p = d * (.3 * 1.5)
        s = p / 4.0
        q = t / (d / 2.0)
        if q == 2:
            return 1.0
        if q < 1:
            q -= 1.0;
            return -.5 * (math.pow(2, 10 * q) * math.sin((q * d - s) * (2.0 *math.pi) / p));
        else:
            q -= 1.0;
            return math.pow(2, -10 * q) * math.sin((q * d - s) * (2.0 * math.pi) / p) * .5 + 1.0;

    @staticmethod
    def ease_in_back(progress, animation):
        return progress * progress * ((1.70158 + 1.0) * progress - 1.70158)

    @staticmethod
    def ease_out_back(progress, animation):
        t = animation.get_frame_pointer()
        d = animation.get_duration()
        p = t / d - 1.0
        return p * p * ((1.70158 + 1) * p + 1.70158) + 1.0

    @staticmethod
    def ease_in_out_back(progress, animation):
        t = animation.get_frame_pointer()
        d = animation.get_duration()
        p = t / (d / 2.0)
        s = 1.70158 * 1.525
        if p < 1:
            return 0.5 * (p * p * ((s + 1.0) * p - s))
        p -= 2.0
        return 0.5 * (p * p * ((s + 1.0) * p + s) + 2.0)

    @staticmethod
    def _ease_out_bounce_internal(t,d):
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
    def _ease_in_bounce_internal(t,d):
        return 1.0 - AnimationAlpha._ease_out_bounce_internal (d - t, d)

    @staticmethod
    def ease_in_bounce(progress, animation):
        t = animation.get_frame_pointer()
        d = animation.get_duration()
        return AnimationAlpha._ease_in_bounce_internal(t, d)

    @staticmethod
    def ease_out_bounce(progress, animation):
        t = animation.get_frame_pointer()
        d = animation.get_duration()
        return AnimationAlpha._ease_out_bounce_internal (t, d)

    @staticmethod
    def ease_in_out_bounce(progress, animation):
        t = animation.get_frame_pointer()
        d = animation.get_duration()
        if t < d / 2.0 :
            return AnimationAlpha._ease_in_bounce_internal (t * 2.0, d) * 0.5
        else:
            return AnimationAlpha._ease_out_bounce_internal (t * 2.0 - d, d) * 0.5 + 1.0 * 0.5