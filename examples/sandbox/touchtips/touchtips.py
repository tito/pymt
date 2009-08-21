# -*- coding: utf-8 -*-
from pymt import *
import pyglet

# PYMT Plugin integration
IS_PYMT_PLUGIN = False
PLUGIN_TITLE = 'Touch Tips'
PLUGIN_AUTHOR = 'Riley Dutton'
PLUGIN_DESCRIPTION = 'An example of TouchTips, a system for showing hints to users of a multi-touch table regarding appropriate gestures for an object.'

class MTTouchTip(MTWidget):
    
    def __init__(self, **kwargs):
        super(MTTouchTip, self).__init__(**kwargs)
        
        self.tips = []
        self.clock = pyglet.clock.Clock()
        
        #Load all of our necessary images.
        pinch_1 = pyglet.image.load("pinch_1.png")
        pinch_2 = pyglet.image.load("pinch_2.png")
        pinch_3 = pyglet.image.load("pinch_3.png")
        self.pinch_seq = [pinch_1, pinch_2, pinch_3, pinch_3, pinch_3, pinch_2, pinch_1, pinch_1, pinch_1]
        
        tap_1 = pyglet.image.load("tap_1.png")
        tap_2 = pyglet.image.load("tap_2.png")
        self.tap_seq = [tap_1, tap_1, tap_2, tap_2, tap_2, tap_2]
        
    
    def attach(self, obj, type, rot=0.0, delay=0.0):
        '''Attach a TouchTip to the supplied object. Note that the object must be derived from MTWidget at some level.'''
        
        tip = MTWidget()
        
        tip.target = obj
        
        if(type == "pinch"):
            tip.anim = MTAnimatedGif(sequence = self.pinch_seq, delay=0.2, rotation=rot)
            tip.target.push_handlers(on_touch_down=curry(self.handle_event, tip, "touch_down"))
            tip.target.push_handlers(on_resize=curry(self.handle_event, tip, "resize"))
            tip.requirements = ['touch_down', 'resize']
        
        if(type == "tap"):
            tip.anim = MTAnimatedGif(sequence = self.tap_seq, delay=0.2, rotation=rot)
            tip.target.push_handlers(on_touch_down=curry(self.handle_event, tip, "touch_down"))
            tip.requirements = ['touch_down']
            
        tip.size = tip.anim.size
        tip.origsize = tip.size
        tip.shown = False
        tip.opacity = 0
        tip.delay = delay
        tip.add_animation('show','opacity', 150, 1.0/60, 2.0) 
        self.tips.append(tip)
        self.add_widget(tip)
    
    def handle_event(*largs):
        if largs[2] in largs[1].requirements:
            print "Removing", largs[2]
            largs[1].requirements.remove(largs[2])
    
    def on_draw(self):
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
            tip.pos = tip.target.pos[0] + tip.target.size[0]/2 - offset_x, tip.target.pos[1] + tip.target.size[1]/2 - offset_y
            
            tip.anim.pos = tip.pos
            tip.anim.scale = tip.scale
            tip.anim.opacity = tip.opacity
            
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
            tip.bring_to_front()
            tip.anim.draw()
        super(MTTouchTip, self).draw()


def pymt_plugin_activate(w, ctx):
    Tips = MTTouchTip()
    
    ctx.c = MTKinetic()
    
    test = MTAnimatedGif(filename="test.gif")
    test.scale = 3.0
    test.pos = (300, 300)
    
    test2 = MTScatterImage(filename='../../pictures/images/pic1.jpg')
    test2.pos = (600, 600)
    test2.rot = 60
    
    ctx.c.add_widget(test)
    ctx.c.add_widget(test2)
    ctx.c.add_widget(Tips)
    w.add_widget(ctx.c)
    Tips.attach(test, "tap", delay=5.0)
    Tips.attach(test2, "pinch", delay=5.0)

def pymt_plugin_deactivate(w, ctx):
    w.remove_widget(ctx.c)

if __name__ == '__main__':
    w = MTWindow()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
