'''
Coverflow: a coverflow widget
'''

__all__ = ('MTCoverFlow', )

from OpenGL.GL import glRotatef, glTranslatef
from pymt.graphx import set_color, drawRectangle, drawTexturedRectangle, \
        Fbo, drawLabel
from pymt.utils import boundary
from pymt.vector import Vector
from pymt.ui.animation import Animation
from pymt.ui.widgets.widget import MTWidget

class MTCoverFlow(MTWidget):
    '''A coverflow widget, that support mostly any widget in :)

    :Parameters:
        `cover_angle` : int, default to 90
            Angle to turn cover when they are displayed on the left/right side
        `cover_distance` : int, default to 400
            Distance in pixels for starting drawing left/right side from the
            current displayed cover
        `cover_spacing` : int, default to 50
            Distance in pixels between covers
        `cover_blend` : bool, default to False
            Activate background blending for the cover. If you set a background
            color, without blending, the blending will look wrong. Activate
            blending if you want to use your background color for fading or if
            you want to use a img with an alpha channel (i.e. png with transparent background)
        `cover_blend_start` : float, default 1.0
            Alpha value to use for the cover blending (0 means transparent)
        `cover_blend_stop` : float, default to 1.0
            Alpha value to use for the cover blending
        `reflection_blend` : bool, default to False
            Activate background blending for reflection. If you set a background
            color, without blending, the reflection will look wrong. Activate
            blending if you want to use your background color for fading.
        `reflection_percent` : float, default to 0.3
            Percentage of the thumbnail height to be showed. For example, if the
            thumbnail is 400 height, and reflection_percent is 0.4, only
            (0.3 * 400) pixels will be showed for reflection
        `reflection_start` : float, default 0.4
            Alpha value to use for top reflection (0 mean transparent)
        `reflection_stop` : float, default to 0
            Alpha value to use for the bottom reflection
        `thumbnail_size` : list, default to (400, 400)
            Size of a thumbnail
        `trigger_cover_distance` : int, default to 30
            Distance in pixels to trigger the switch of cover
        `trigger_distance` : int, default to 3
            Distance within a click is considered and fired
        `title_attributes` : dict, default to {}
            Attributes to pass to drawLabel
        `title_draw` : bool, default to True
            If a title attribute is found on the child, it will be drawed on
            screen
        `title_position` : int, default to -50
            Y position of title (starting from the bottom of the cover)

    :Events:
        `on_change` : widget
            Fired when the selected cover change
        `on_select` : widget
            Fired when the user "click" on the current cover
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('cover_angle', 90)
        kwargs.setdefault('cover_distance', 400)
        kwargs.setdefault('cover_spacing', 50)
        kwargs.setdefault('cover_blend', False)
        kwargs.setdefault('cover_blend_start', 1.0)
        kwargs.setdefault('cover_blend_stop', 1.0)
        kwargs.setdefault('reflection_blend', False)
        kwargs.setdefault('reflection_percent', .3)
        kwargs.setdefault('reflection_start', .4)
        kwargs.setdefault('reflection_stop', 0)
        kwargs.setdefault('thumbnail_size', (400, 400))
        kwargs.setdefault('title_attributes', {})
        kwargs.setdefault('title_draw', True)
        kwargs.setdefault('title_position', -50)
        kwargs.setdefault('trigger_cover_distance', 30)
        kwargs.setdefault('trigger_distance', 3)

        super(MTCoverFlow, self).__init__(**kwargs)

        self.register_event_type('on_select')
        self.register_event_type('on_change')

        self.cover_angle            = kwargs.get('cover_angle')
        self.cover_distance         = kwargs.get('cover_distance')
        self.cover_spacing          = kwargs.get('cover_spacing')
        self.cover_blend            = kwargs.get('cover_blend')
        self.cover_blend_start      = kwargs.get('cover_blend_start')
        self.cover_blend_stop       = kwargs.get('cover_blend_stop')
        self.reflection_blend    = kwargs.get('reflection_blend')
        self.reflection_percent     = kwargs.get('reflection_percent')
        self.reflection_start       = kwargs.get('reflection_start')
        self.reflection_stop        = kwargs.get('reflection_stop')
        self.thumbnail_size         = kwargs.get('thumbnail_size')
        self.title_attributes       = kwargs.get('title_attributes')
        self.title_draw             = kwargs.get('title_draw')
        self.title_position         = kwargs.get('title_position')
        self.trigger_cover_distance = kwargs.get('trigger_cover_distance')
        self.trigger_distance       = kwargs.get('trigger_distance')

        self._animation             = None
        self._fbo                   = Fbo(size=self.thumbnail_size)
        self._reflection_coords     = None
        self._cover_blend_coords    = None
        self._selection             = 0
        self._touch                 = None
        self._transition            = 0

    def on_touch_down(self, touch):
        if not len(self.children) or \
           self._touch or \
           not self.collide_point(*touch.pos):
            return
        # we got one touch for coverflow !
        self._touch = touch
        touch.grab(self)
        touch.userdata['coverflow.firstpos']    = touch.pos
        touch.userdata['coverflow.pos']         = touch.pos
        touch.userdata['coverflow.noclick']     = False
        return True

    def on_touch_move(self, touch):
        # accept only the touch we've got first.
        if touch.grab_current != self:
            return

        # stop transition animation if exist
        if self._animation:
            self._animation.stop()
            self._animation = None

        # calculate the distance between the touch and the old position
        d = touch.userdata['coverflow.pos'][0] - touch.xpos

        # cancel on-select if needed
        if abs(d) > self.trigger_distance:
            touch.userdata['coverflow.noclick'] = True

        # and calculate transition: the delta movement between
        # old and new cover position
        self._transition = d / self.trigger_cover_distance

        # don't make transition go farther than possible
        if self._transition < 0 and self._selection == 0:
            self._transition = 0
        if self._transition > 0 and self._selection == len(self.children) - 1:
            self._transition = 0

        # are we able to switch cover ?
        if abs(self._transition) < 1.:
            return

        # cover switch !
        self._selection += int(self._transition)
        self._selection = boundary(self._selection, 0, len(self.children) - 1)

        # adjust transition
        self._transition -= int(self._transition)

        # save the position of the touch
        # to restart a switch from this position
        touch.userdata['coverflow.pos'] = touch.pos

        # fire on_change
        self.dispatch_event('on_change', self.children[self._selection])
        return True

    def on_touch_up(self, touch):
        # accept only the touch we've got first.
        if touch.grab_current != self:
            return
        touch.ungrab(self)
        self._touch = None

        # animate the transition to back to 0
        # cover will back to position in nicer way
        self._animation = self.do(Animation(f='ease_out_expo', _transition=0))

        # launch on_select ?
        if not touch.userdata['coverflow.noclick']:
            distance = Vector(touch.userdata['coverflow.firstpos']).distance(Vector(touch.pos))
            if distance <= self.trigger_distance:
                self.dispatch_event('on_select', self.children[self._selection])
        return True

    def on_select(self, widget):
        pass

    def on_change(self, widget):
        pass

    def _get_cover_position(self, index, alpha=0):
        x2 = self.center[0]
        if index < self._selection:
            angle = self.cover_angle
            x = x2 - self.cover_distance - (self._selection - index) * self.cover_spacing
        elif index > self._selection:
            angle = 90 + (90 - self.cover_angle)
            x = x2 + self.cover_distance + (index - self._selection) * self.cover_spacing
        else:
            angle = 0
            x = x2 - self.thumbnail_size[0] / 2.
        return angle, x

    def _calculate_coords(self):
        # calculate reflection coordinate
        c1, c2 = self.reflection_start, self.reflection_stop
        cb1, cb2 = self.cover_blend_start, self.cover_blend_stop
        self._reflection_coords = (
            (c2, c2, c2, c2), (c2, c2, c2, c2),
            (c1, c1, c1, c1), (c1, c1, c1, c1))
        self._cover_blend_coords = (
            (cb2, cb2, cb2, cb2), (cb2, cb2, cb2, cb2),
            (cb1, cb1, cb1, cb1), (c1, cb1, cb1, cb1))

    def _draw_title(self, widget):
        if hasattr(widget, 'title'):
            y2 = self.center[1] - self.thumbnail_size[1] / 2.
            drawLabel(str(getattr(widget, 'title')),
                      pos=(self.center[0], y2 + self.title_position))

    def _render_cover(self, index):
        # render the children on a fbo
        child = self.children[index]
        with self._fbo:
            self._fbo.clear()
            child.dispatch_event('on_draw')

        # pre-calculate
        y2 = self.center[1] - self.thumbnail_size[1] / 2.
        angle, x = self._get_cover_position(index, 0)

        # if a transition is in way,
        # use it to calculate angle/position from
        # current position and future position
        if self._transition != 0:
            i2 = index
            if self._transition > 0:
                i2 -= 1
            elif self._transition < 0:
                i2 += 1

            i2          = min(max(-1, i2), len(self.children))
            angle2, x2  = self._get_cover_position(i2, self._transition)

            # do linear alpha
            if self._transition > 0:
                angle   += self._transition * (angle2 - angle)
                x       += self._transition * (x2 - x)
            else:
                angle   -= self._transition * (angle2 - angle)
                x       -= self._transition * (x2 - x)

        # calculate alpha coordinate
        # this is to make cover more darker on the farest side
        # and make brighter the current displayed cover

        a = 1. - .7 * (angle / 90.)
        alpha_coords = (
            (1, 1, 1, 0), (a, a, a, 0),
            (a, a, a, 0), (1, 1, 1, 0))

        # draw !
        glTranslatef(x, y2, 0)
        glRotatef(angle, 0, 1, 0)

        # draw the cover
        if self.cover_blend:
            set_color(1, blend=True)
            drawTexturedRectangle(
                texture=self._fbo.texture,
                size=self.thumbnail_size,
                color_coords=self._cover_blend_coords)
        else:
            set_color(1)
            drawTexturedRectangle(
                texture=self._fbo.texture,
                size=self.thumbnail_size,
                color_coords=alpha_coords)

        # now, for reflection, don't do matrix transformation
        # just invert texcoord + play with color
        old_texcoords = self._fbo.texture.tex_coords
        self._fbo.texture.flip_vertical()
        self._fbo.texture.tex_coords = list(self._fbo.texture.tex_coords)
        self._fbo.texture.tex_coords[1] = self.reflection_percent
        self._fbo.texture.tex_coords[3] = self.reflection_percent

        # draw reflection
        pos = (0, -self.thumbnail_size[1] * self.reflection_percent)
        size = (self.thumbnail_size[0], self.thumbnail_size[1] * self.reflection_percent)

        # activate blending with background ?
        if self.reflection_blend:
            set_color(*self.style['bg-color'])
            drawRectangle(pos=pos, size=size)
            set_color(1, 1, 1, blend=True)

        drawTexturedRectangle(
            texture=self._fbo.texture,
            pos=pos, size=size,
            color_coords=self._reflection_coords)

        # restore fbo tex_coords
        self._fbo.texture.tex_coords = old_texcoords

        # reset our position changes
        glRotatef(angle, 0, -1, 0)
        glTranslatef(-x, -y2, 0)

    def on_update(self):
        self._calculate_coords()
        super(MTCoverFlow, self).on_update()

    def on_draw(self):
        # background
        set_color(*self.style['bg-color'])
        drawRectangle(pos=self.pos, size=self.size)

        if not len(self.children):
            return

        # draw left side
        for i in xrange(0, self._selection):
            self._render_cover(i)

        # draw right side in reverse order
        for i in xrange(len(self.children) - 1, self._selection, - 1):
            self._render_cover(i)

        # draw cover
        self._render_cover(self._selection)

        # draw title ?
        if self.title_draw:
            child = self.children[self._selection]
            self._draw_title(child)
    def remove_widget(self, widget):
        super(MTCoverFlow,self).remove_widget(widget)
        _len = len(self.children)
        if self._selection >=  _len:
            self._selection = _len -1
        if self._selection < 0:
            #No more children
            #Do something appropriate (maybe hide, maybe nothing)            
            pass