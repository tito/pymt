'''
Animation package: handle animation, and default alpha method
'''

__all__ = ['AnimationAlpha', 'Animation','Delay']

import math
from ..clock import getClock

class AnimationBase(object):
    def __init__(self,**kwargs):
        self.widget = kwargs.get('widget')
        self.params = kwargs.get('key_args')
        self.duration =  self.params['duration']
        self.animator = kwargs.get('animator')

        self._frame_pointer = 0.0
        self._progress = 0.0
        self.running = False

        self._prop_list = {}
        for item in self.params:
            if item not in ["duration","anim1","anim2"]:
                self._prop_list[item] = self.params[item]

        for prop in self._prop_list:
            cval = self._get_value_from(prop)
            if type(cval) in (tuple, list):
                self._prop_list[prop] = (cval,self._prop_list[prop])
            elif isinstance(cval, dict):
                #contruct a temp dict of only required keys
                temp_dict = {}
                for each_key in self._prop_list[prop]:
                    temp_dict[each_key] = cval[each_key]
                self._prop_list[prop] = (temp_dict,self._prop_list[prop])
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

class Animation(object):
    def __init__(self,**kwargs):
        kwargs.setdefault('duration', 5.0) #default animation duration set to 1 sec
        self.duration = kwargs.get('duration')
        self.children = {}
        self.params = kwargs
        
    def start(self,widget):
        animobj = self.children[widget]
        animobj.start()

    def stop(self,widget):
        widget.dispatch_event('on_animation_complete', self)
        self._del_child(widget)

    def pause(self):
        pass

    def set_widget(self,widgetx):
        if widgetx not in self.children.keys():
            new_animobj = AnimationBase(widget=widgetx,key_args=self.params,animator=self)
            self.children[widgetx] = new_animobj
            self.setup()
            return True
        return False

    def setup(self):
        pass
        
    def animate(self, *largs):
        for widget in largs:
            self.set_widget(widget)
            self.start(widget)
        
    def _del_child(self,child):
        del self.children[child]
        
    def _return_params(self):
        return self.params
        
    def _set_params(self,key,value):
        self.params[key] = value
        
    def __add__(self, animation):
        return SequenceAnimation(anim1=self,anim2=animation)
    
    def __and__(self, animation):
        return ParallelAnimation(anim1=self,anim2=animation)

class SequenceAnimation(Animation):
    def __init__(self, **kwargs):
        super(SequenceAnimation, self).__init__(**kwargs)        
        self.animations = []
        anim1 = kwargs.get('anim1')
        anim2 = kwargs.get('anim2')
        if type(anim1) in (tuple, list):
            for anim in anim1:
                self.animations.append(anim)
        else:
            self.animations.append(anim1)
        self.animations.append(anim2)
        self.anim_counter = 0
        
    def start(self, widget):
        if self.anim_counter >= len(self.animations):
            widget.dispatch_event('on_animation_complete', self)
            return
        current_anim = self.animations[self.anim_counter]
        current_anim.start(widget)
    
    def stop(self,widget):
        self.anim_counter += 1
        #self.animations[self.anim_counter]._del_child(widget)
        self.start(widget)
            
    def set_widget(self,widgetx):
        for animation in self.animations:            
            if widgetx not in animation.children.keys():
                new_animobj = AnimationBase(widget=widgetx,key_args=animation.params,animator=self)
                animation.children[widgetx] = new_animobj
                animation.setup()
        return True
        
    def __add__(self, animation):
        return SequenceAnimation(anim1=self.animations,anim2=animation)
        
class ParallelAnimation(Animation):
    def __init__(self, **kwargs):
        super(ParallelAnimation, self).__init__(**kwargs)        
        self.animations = []
        anim1 = kwargs.get('anim1')
        anim2 = kwargs.get('anim2')
        if type(anim1) in (tuple, list):
            for anim in anim1:
                self.animations.append(anim)
        else:
            self.animations.append(anim1)
        self.animations.append(anim2)
        
    def start(self, widget):
        for animation in self.animations:
            animation.start(widget)
            
    def set_widget(self,widgetx):
        for animation in self.animations:            
            if widgetx not in animation.children.keys():
                new_animobj = AnimationBase(widget=widgetx,key_args=animation.params,animator=animation)
                animation.children[widgetx] = new_animobj
                animation.setup()
        return True
        
    def __and__(self, animation):
        return ParallelAnimation(anim1=self.animations,anim2=animation)



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
