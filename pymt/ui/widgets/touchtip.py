'''
TouchTip: A simple animated hint system for interacting with multi-touch tables.
'''

from __future__ import with_statement

__all__ = ['MTTouchTip']

import pyglet
from ..factory import MTWidgetFactory
from widget import MTWidget
from animatedgif import MTAnimatedGif
from ...utils import curry
import os
import pymt

iconPath = os.path.join(pymt.pymt_data_dir, 'icons', 'touchtips', '')

class MTTouchTip(MTWidget):
    
    def __init__(self, **kwargs):
        super(MTTouchTip, self).__init__(**kwargs)
        
        self.tips = []
        self.clock = pyglet.clock.Clock()
        
        #Load all of our necessary images.
        pinch_1 = pyglet.image.load(iconPath+"pinch_1.png")
        pinch_2 = pyglet.image.load(iconPath+"pinch_2.png")
        pinch_3 = pyglet.image.load(iconPath+"pinch_3.png")
        self.pinch_seq = [pinch_1, pinch_2, pinch_3, pinch_3, pinch_3, pinch_2, pinch_1, pinch_1, pinch_1]
        
        tap_1 = pyglet.image.load(iconPath+"tap_1.png")
        tap_2 = pyglet.image.load(iconPath+"tap_2.png")
        self.tap_seq = [tap_1, tap_1, tap_2, tap_2, tap_2, tap_2]
        
    
    def attach(self, obj, type, delay=0.0, rotation=0.0):
        '''Attach a TouchTip to the supplied object. Note that the object must be derived from MTWidget at some level.'''
        
        tip = MTWidget()
        
        tip.target = obj
        
        if(type == "pinch"):
            tip.anim = MTAnimatedGif(sequence = self.pinch_seq, delay=0.2)
            tip.target.push_handlers(on_touch_down=curry(self.handle_touch_event, tip, "touch_down"))
            tip.target.push_handlers(on_resize=curry(self.handle_event, tip, "resize"))
            tip.requirements = ['touch_down', 'resize']
        
        if(type == "tap"):
            tip.anim = MTAnimatedGif(sequence = self.tap_seq, delay=0.2)
            tip.target.push_handlers(on_touch_down=curry(self.handle_touch_event, tip, "touch_down"))
            tip.requirements = ['touch_down']
            
        tip.size = tip.anim.size
        tip.rotation = rotation
        tip.origsize = tip.size
        tip.shown = False
        tip.opacity = 0
        tip.delay = delay
        tip.add_animation('show','opacity', 120, 1.0/60, 2.0) 
        self.tips.append(tip)
        self.add_widget(tip)
    
    def handle_event(*largs):
        requirement = largs[2]
        tip = largs[1]
        if requirement in tip.requirements:
            tip.requirements.remove(requirement)
    
    def handle_touch_event(self, tip, requirement, touch):
        if tip.target.collide_point(touch.x, touch.y):
            if requirement in tip.requirements:
                tip.requirements.remove(requirement)
    
    def on_draw(self):
        
        self.bring_to_front()
        
        dt = self.clock.tick()
        deletetips = []
        
        for tip in self.tips:
            
            #Track the object the tip is assigned to.
            
            #Determine our scale based on the size of the object.
            scale_x = float(tip.target.size[0])/float(tip.origsize[0])
            scale_y = float(tip.target.size[1])/float(tip.origsize[1])
            
            if scale_x > scale_y:
                tip.scale = scale_y
            else:
                tip.scale = scale_x
            
            #we want our top-left corner to be in the middle of the thing we're attaching to...
            offset_x = 75 * tip.scale
            offset_y = (tip.origsize[0] - 40) * tip.scale
            
            #Does this object have a center_pos? If so, use that. If not, do it ourselves.
            if tip.target.center != None:
                tip.pos = tip.target.center[0] + (tip.origsize[0] * tip.scale * 0.25), tip.target.center[1] - (tip.origsize[1] * tip.scale * 0.10)
            else:
                tip.pos = tip.target.pos[0] + tip.target.size[0]/2 - offset_x, tip.target.pos[1] + tip.target.size[1]/2 - offset_y
            
            tip.anim.pos = tip.pos
            tip.anim.scale = tip.scale
            tip.anim.opacity = tip.opacity
            tip.anim.rotation = tip.rotation
            
            tip.anim.on_draw()
            
            #Check on our delay timing.
            if not tip.shown:
                tip.delay = tip.delay - dt
                if tip.delay < 0:
                    tip.shown = True
                    tip.start_animations('show')
            
            #Check on our requirements
            if len(tip.requirements) < 1:
                deletetips.append(tip)
        
        for tip in deletetips:
            self.tips.remove(tip)
            self.remove_widget(tip)
        
        super(MTTouchTip, self).on_draw()
            
    
    def draw(self):
        for tip in self.tips:
            tip.anim.draw()
        super(MTTouchTip, self).draw()

        
MTWidgetFactory.register('MTTouchTip', MTTouchTip)