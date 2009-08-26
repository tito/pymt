# -*- coding: utf-8 -*-
from pymt import *
import pyglet

# PYMT Plugin integration
IS_PYMT_PLUGIN = False
PLUGIN_TITLE = 'Touch Tips'
PLUGIN_AUTHOR = 'Riley Dutton'
PLUGIN_DESCRIPTION = 'An example of TouchTips, a system for showing hints to users of a multi-touch table regarding appropriate gestures for an object.'

iconPath = os.path.join('touchtips', '')

class MTAnimatedGif(MTWidget):
    '''MTAnimatedGif is a simple MT widget with support for Pyglet's animated gif functions.

    Note: either the 'filename' or 'sequence' parameter is required. You must pass one or the other!

    :Parameters:
        `filename` : str
            Filename of animated gif image.
        `sequence` : list
            A list of pyglet.image objects that will be combined into an animation.
        `delay` : float, defaults to 0.1
            The time in seconds to put between each image if a sequence was passed.
        `scale` : float, defaults to 1.0
            The scale of the object.
        `opacity`: int, defaults to 250
            The opacity of the object. See pyglet.Sprite for more information on opacity.
        `rotation`: float, defaults to 0.0
            The rotation of the object, in degrees.

    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('delay', 0.1)
        kwargs.setdefault('scale', 1.0)
        kwargs.setdefault('opacity', 250)
        kwargs.setdefault('rotation', 0.0)

        super(MTAnimatedGif, self).__init__(**kwargs)

        self.scale = kwargs.get('scale')
        self.opacity = kwargs.get('opacity')
        self.rotation = kwargs.get('rotation')

        #Check to see if we're loading a file or an image sequence.
        if kwargs.get('filename') != None:
            self.animation = pyglet.image.load_animation(kwargs.get('filename'))
        elif kwargs.get('sequence') != None:
            self.animation = pyglet.image.Animation.from_image_sequence(sequence=kwargs.get('sequence'), period=kwargs.get('delay'), loop=True)
        else:
            pymt_logger.error("Unable to load MTAnimatedGif: you must pass either a filename or a sequence of images.")
            return False #Must pass at least a filename or a sequence of images.

        self.bin = pyglet.image.atlas.TextureBin()
        self.animation.add_to_texture_bin(self.bin)

        #Set the anchor of the image to the center of the image.
        anchor_x = self.animation.get_max_width() / 2
        anchor_y = self.animation.get_max_height() / 2
        for f in self.animation.frames:
            f.image.anchor_x = anchor_x
            f.image.anchor_y = anchor_y

        self.image = pyglet.sprite.Sprite(self.animation)

        #Set the initial size to the maximum size of the animation.
        self.size = self.animation.get_max_width(), self.animation.get_max_height()

    #The center and the position (should be) the same thing.
    def _get_center(self):
        return self.pos
    center = property(_get_center)


    def draw(self):
        self.image.x        = self.x
        self.image.y        = self.y
        self.image.scale    = self.scale
        self.size           = self.image.width, self.image.height
        self.image.opacity  = self.opacity
        self.image.rotation = self.rotation
        self.image.draw()


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


    def attach(self, obj, type, delay=0.0, rotation=0.0, offset=(0,0)):
        '''Ataches a TouchTip to an existing object (must be, at some level, derived from MTWidget)

           :Parameters:
               `obj` : MTWidget-derived object
                   The object that the touchtip will be attached to. If the object is moved on the screen, the touchtip will move as well.
               `type` : string
                   Type of hint to give. Options are currently 'tap' or 'pinch'
               `delay` : float, default to 0.0
                   The length of time before the TouchTip will be displayed by the object. If the requirements (see below) are all met before this time is reached, then the TouchTip will never be displayed.
                   This time is in seconds.
               `rotation` : float, default to 0.0
                   Set the rotation (in degrees) of the TouchTip.
               `offset` : tuple of two integers, default to (0, 0)
                   Set the offset of the touchtip from the normal position (close to the center) of the attached object. Useful for precise positioning on an individual basis.

            A note on requirements:
                The following requirements are present for each of the following hint types before the hint is considered "complete" and will disappear:

                "tap": touch_down
                "pinch": touch_down, resize (this is meant to be used with MTScatterWidget objects)
            '''

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

        tip.offset = offset
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

            global_offset_x = tip.offset[0]
            global_offset_y = tip.offset[1]

            #Does this object have a center_pos? If so, use that. If not, do it ourselves.
            if tip.target.center != None:
                tip.pos = tip.target.center[0] + (tip.origsize[0] * tip.scale * 0.25) + global_offset_x, tip.target.center[1] - (tip.origsize[1] * tip.scale * 0.10) + global_offset_y
            else:
                tip.pos = tip.target.pos[0] + tip.target.size[0]/2 - offset_x + global_offset_x, tip.target.pos[1] + tip.target.size[1]/2 - offset_y + global_offset_y

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

def pymt_plugin_activate(w, ctx):
    Tips = MTTouchTip()

    ctx.c = MTKinetic()

    test = MTAnimatedGif(filename="test.gif")
    test.scale = 3.0
    test.pos = (300, 300)

    test2 = MTScatterImage(filename='../../pictures/images/pic1.jpg', pos=(200, 600), rotation=60, size=(500, 500))

    test3 = MTImageButton(filename="../../pictures/images/pic2.jpg", pos=(600, 200), scale=0.50)

    ctx.c.add_widget(test)
    ctx.c.add_widget(test2)
    ctx.c.add_widget(test3)
    ctx.c.add_widget(Tips)
    w.add_widget(ctx.c)
    Tips.attach(test, "tap", delay=5.0)
    Tips.attach(test2, "pinch", delay=5.0, rotation=-60)
    Tips.attach(test3, "tap", delay=0.0)

def pymt_plugin_deactivate(w, ctx):
    w.remove_widget(ctx.c)

if __name__ == '__main__':
    w = MTWindow()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
