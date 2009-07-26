'''
Scatter package: provide lot of widgets based on scatter (base, svg, plane, image...)
'''

from __future__ import with_statement
__all__ = ['MTScatterWidget', 'MTScatterSvg', 'MTScatterPlane', 'MTScatterImage']

import pyglet
from pyglet.gl import *
from ...graphx import drawRectangle, gx_matrix, gx_matrix_identity, set_color
from ...vector import Vector, matrix_mult, matrix_inv_mult
from ..animation import Animation, AnimationAlpha
from ..factory import MTWidgetFactory
from svg import MTSvg
from widget import MTWidget

class MTScatterWidget(MTWidget):
    '''MTScatterWidget is a scatter widget based on MTWidget

    :Parameters:
        `rotation` : float, default to 0.0
            Set initial rotation of widget
        `translation` : list, default to (0,0)
            Set the initial translation of widget
        `scale` : float, default to 1.0
            Set the initial scaling of widget
        `do_rotation` : boolean, default to True
            Set to False for disabling rotation
        `do_translation` : boolean or list, default to True
            Set to False for disabling translation, and ['x'], ['y'] for limit translation only on x or y
        `do_scale` : boolean, default to True
            Set to False for disabling scale
        `scale_min` : float, default to 0.01
            Minimum scale allowed. Don't set to 0, or you can have error with singular matrix.
            The 0.01 mean you can de-zoom up to 10000% (1/0.01*100).

    :Styles:
        `bg-color` : color
            Background color of window
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('rotation', 0.0)
        kwargs.setdefault('translation', (0,0))
        kwargs.setdefault('scale', 1.0)
        kwargs.setdefault('do_scale', True)
        kwargs.setdefault('do_rotation', True)
        kwargs.setdefault('do_translation', True)
        kwargs.setdefault('scale_min', 0.01)

        super(MTScatterWidget, self).__init__(**kwargs)

        self.scale_min      = kwargs.get('scale_min')
        self.do_scale       = kwargs.get('do_scale')
        self.do_rotation    = kwargs.get('do_rotation')

        self.do_translation = kwargs.get('do_translation')
        self.do_translation_x = self.do_translation_y = 1.0
        if type(self.do_translation) == list:
            self.do_translation_x = self.do_translation_y = 0
            for p in self.do_translation:
                if p == 'x':
                    self.do_translation_x = 1.0
                elif p == 'y':
                    self.do_translation_y = 1.0
            self.do_translation = True

        # Cache to_local value
        self.__to_local = (-9999, 9999) # Invalid cache for the first run
        self.__to_local_x = 0
        self.__to_local_y = 0
        self.__to_parent = (-9999, 9999) # Invalid cache for the first run
        self.__to_parent_x = 0
        self.__to_parent_y = 0
        self.__width = 0
        self.__height = 0

        # For flipping animations
        self.zangle = 0
        self.side = 'front'

        # Holds children for both sides
        self.children_front = []
        self.children_back = []
        self.children = self.children_front

        self.anim = Animation(self, 'flip', 'zangle', 180, 1, 10, func=AnimationAlpha.ramp)

        self.touches        = {}
        self.scale          = 1
        self.transform_mat  = (GLfloat * 16)()
        if kwargs.get('translation')[0] != 0 or kwargs.get('translation')[1] != 0:
            self.init_transform(kwargs.get('translation'), kwargs.get('rotation'), kwargs.get('scale'))
        else:
            self.init_transform(super(MTScatterWidget, self).pos, kwargs.get('rotation'), kwargs.get('scale'))

    def add_widget(self, w, side='front', front=True):
        '''Add a widget to a side of scatter.
        :Parameters:
            `side` : str, default is 'front'
                Side to be added. Can be one of 'front', 'back' or '' (mean both.)
            `front` : bool, default is True
                Indicate if the widget must be pulled in the front of the screen
        '''
        if side == 'front':
            if front:
                self.children_front.append(w)
            else:
                self.children_front.insert(0, w)
        elif side == 'back':
            if front:
                self.children_back.append(w)
            else:
                self.children_back.insert(0, w)
        else:
            # add to both side
            self.add_widget(w, side='front', front=front)
            self.add_widget(w, side='back', front=front)

        try:
            w.parent = self
        except:
            pass

    def init_transform(self, pos, angle, scale):
        if scale < self.scale_min:
            scale = self.scale_min
        self.scale = scale
        with gx_matrix_identity:
            glTranslated(pos[0], pos[1], 0)
            glScalef(scale, scale, 1)
            glRotated(angle,0,0,1)
            glGetFloatv(GL_MODELVIEW_MATRIX, self.transform_mat)

    def draw(self):
        set_color(*self.style.get('bg-color'))
        drawRectangle((0,0), (self.width, self.height))

    def flip_children(self):
        '''Flips the children
        this has to be called exactly half way through the animation
        so it looks like there are actually two sides'''
        if self.side == 'front':
            self.side = 'back'
            self.children = self.children_back
        else:
            self.side = 'front'
            self.children = self.children_front

    def flip_to(self, to):
        if to == 'back' and self.side == 'front':
            self.flip_children()
        elif to == 'front' and self.side == 'back':
            self.flip_children()

    def flip(self):
       '''Triggers a flipping animation'''
       if self.side == 'front':
           self.anim.value_to = 180
       else:
           self.anim.value_to = 0
       self.anim.reset()
       self.anim.start()

    def on_draw(self):
        if self.zangle < 90:
            self.flip_to('front')
        else:
            self.flip_to('back')
        with gx_matrix:
            glMultMatrixf(self.transform_mat)
            glTranslatef(self.width / 2, 0, 0)
            if self.side == 'front':
                glRotatef(self.zangle, 0, 1, 0)
            else:
                glRotatef(self.zangle + 180, 0, 1, 0)
            glTranslatef(-self.width / 2, 0, 0)
            super(MTScatterWidget, self).on_draw()

    def to_parent(self, x, y):
        if self.__to_parent == (x, y):
            return (self.__to_parent_x, self.__to_parent_y)
        self.__to_parent = (x, y)
        self.new_point = matrix_mult(self.transform_mat, (x, y, 0, 1))
        self.__to_parent_x, self.__to_parent_y = self.new_point.x, self.new_point.y
        return (self.new_point.x, self.new_point.y)

    def to_local(self,x, y):
        if self.__to_local == (x, y):
            return (self.__to_local_x, self.__to_local_y)
        self.__to_local = (x, y)
        self.new_point = matrix_inv_mult(self.transform_mat, (x, y, 0, 1))
        self.__to_local_x, self.__to_local_y = self.new_point.x, self.new_point.y
        return (self.new_point.x, self.new_point.y)

    def collide_point(self, x, y):
        local_coords = self.to_local(x, y)
        if local_coords[0] > 0 and local_coords[0] < self.width \
           and local_coords[1] > 0 and local_coords[1] < self.height:
            return True
        else:
            return False

    def find_second_touch(self, touchID):
        for tID in self.touches.keys():
            x, y = self.touches[tID].x, self.touches[tID].y
            if self.collide_point(x, y) and tID!=touchID:
                return tID
        return None


    def apply_angle_scale_trans(self, angle, scale, trans, point):
        old_scale = self.scale
        self.scale *= scale
        if self.scale < self.scale_min:
            self.scale = old_scale
            scale = 1
        with gx_matrix_identity:
            if self.do_translation:
                glTranslated(trans.x * self.do_translation_x, trans.y * self.do_translation_y, 0)
            glTranslated(point.x, point.y, 0)
            if self.do_scale:
                glScaled(scale, scale, 1)
            if self.do_rotation:
                glRotated(angle, 0, 0, 1)
            glTranslated(-point.x, -point.y,0)
            glMultMatrixf(self.transform_mat)
            glGetFloatv(GL_MODELVIEW_MATRIX, self.transform_mat)

    def rotate_zoom_move(self, touchID, x, y):
        # we definitly have one point
        p1_start = Vector(*self.touches[touchID])
        p1_now   = Vector(x, y)

        # if we have a second point, do the scale/rotate/move thing
        second_touch = self.find_second_touch(touchID)
        if second_touch:
            # set default
            trans = Vector(0, 0)

            p2_start = Vector(*self.touches[second_touch])
            p2_now   = Vector(*self.touches[second_touch])

            # find intersection between lines...the point around which to rotate
            intersect = Vector.line_intersection(p1_start,  p2_start,p1_now, p2_now)
            if not intersect:
                intersect = Vector(0, 0)

            # compute scale factor
            old_dist = p1_start.distance(p2_start)
            if old_dist < 1:
                old_dist = 1.0
            new_dist = p1_now.distance(p2_now)
            scale = new_dist / old_dist

            # compute rotation angle
            old_line = p1_start - p2_start
            new_line = p1_now - p2_now
            rotation = -1.0 * old_line.angle(new_line)

        else:
            # set default
            intersect = Vector(0,0)
            rotation = 0.0
            scale = 1.0

            # just comnpute a translation component if we only have one point
            trans = p1_now - p1_start

        # apply to our transformation matrix
        self.apply_angle_scale_trans(rotation, scale, trans, intersect)

        # save new position of the current touch
        self.touches[touchID] = Vector(x, y)

    def _get_center(self):
        return self.to_parent(self.width / 2, self.height / 2)
    def _set_center(self, center, do_event=True):
        center = self.to_local(*center)
        if self._x == center[0] and self._y == center[1]:
            return
        self._x, self._y = center
        if do_event:
            self.dispatch_event('on_move', self._x, self._y)
    center = property(_get_center, _set_center)
    pos = property(_get_center, _set_center)

    # Scatter widget don't have write attribute on x/y
    def _get_x(self):
        return self.center[0]
    x = property(_get_x)
    def _get_y(self):
        return self.center[1]
    y = property(_get_y)

    def get_scale_factor(self, use_gl=False):
        '''Return the current scale factor.
        By default, the calculated scale is returned. You can set use_gl to
        calculate scale factor with opengl operation. Precision is not the
        same between them.

        Exemple for a scale factor :
            OpenGL version:     0.50279381376
            Calculated version: 0.502793060813
        '''
        if use_gl:
            p1_trans = matrix_mult(self.transform_mat, (1,1,0,1))
            p2_trans = matrix_mult(self.transform_mat, (2,1,0,1))
            dist_trans = p1_trans.distance(p2_trans)
            return dist_trans
        else:
            return self.scale

    def on_touch_down(self, touch):
        x, y = touch.x, touch.y

        # if the touch isnt on the widget we do nothing
        if not self.collide_point(x, y):
            return False

        # let the child widgets handle the event if they want
        touch.push()
        touch.x, touch.y = self.to_local(x, y)
        if super(MTScatterWidget, self).on_touch_down(touch):
            touch.pop()
            return True
        touch.pop()

        # if the children didnt handle it, we bring to front & keep track
        # of touches for rotate/scale/zoom action
        touch.grab(self)
        self.bring_to_front()
        self.touches[touch.id] = Vector(x, y)
        return True

    def on_touch_move(self, touch):
        x, y = touch.x, touch.y

        # let the child widgets handle the event if they want
        if self.collide_point(x, y) and not touch.grab_current == self:
            touch.push()
            touch.x, touch.y = self.to_local(x, y)
            if super(MTScatterWidget, self).on_touch_move(touch):
                touch.pop()
                return True
            touch.pop()

        # rotate/scale/translate
        if touch.id in self.touches and touch.grab_current == self:

            self.rotate_zoom_move(touch.id, x, y)

            # precalculate size of container
            container_width = int(self.width * self.get_scale_factor())
            container_height = int(self.height * self.get_scale_factor())

            # dispatch event only if it change
            if container_width != self.__width or container_height != self.__height:
                self.dispatch_event('on_resize', container_width, container_height)
                self.__width = container_width
                self.__height = container_height

            # dispatch move event
            self._set_center(self.to_parent(0, 0), do_event=False)
            self.dispatch_event('on_move', self.x, self.y)
            return True

        # stop porpagation if its within our bounds
        if self.collide_point(x, y):
            return True

    def on_touch_up(self, touch):
        x, y = touch.x, touch.y

        # if the touch isnt on the widget we do nothing
        if not touch.grab_state:
            touch.push()
            touch.x, touch.y = self.to_local(x, y)
            if super(MTScatterWidget, self).on_touch_up(touch):
                touch.pop()
                return True
            touch.pop()

        # remove it from our saved touches
        if touch.id in self.touches and touch.grab_state:
            del self.touches[touch.id]

        # stop porpagating if its within our bounds
        if self.collide_point(x, y):
            return True


class MTScatterPlane(MTScatterWidget):
    '''A Plane that transforms for zoom/rotate/pan.
         if none of the childwidgets handles the input (the background is touched), all of them are transformed together'''
    def find_second_touch(self, touchID):
        for tID in self.touches.keys():
            if  tID!=touchID:
                return tID
        return None

    def draw(self):
        pass

    def on_touch_down(self, touch):

        # save pos
        touch.push()
        touch.x, touch.y = self.to_local(touch.x, touch.y)
        if super(MTScatterWidget, self).on_touch_down(touch):
            touch.pop()
            return True
        touch.pop()

        self.bring_to_front()
        self.touches[touch.id] = Vector(touch.x, touch.y)
        return True

    def on_touch_move(self, touch):
        if touch.id in self.touches:
            self.rotate_zoom_move(touch.id, touch.x, touch.y)
            self.dispatch_event('on_resize',
                int(self.width*self.get_scale_factor()),
                int(self.height*self.get_scale_factor()))
            self.dispatch_event('on_move', self.x, self.y)
            return True

        # save pos
        touch.push()
        touch.x, touch.y = self.to_local(touch.x, touch.y)
        if MTWidget.on_touch_move(self, touch):
            touch.pop()
            return True
        touch.pop()


    def on_touch_up(self, touch):
        touch.push()
        touch.x, touch.y = self.to_local(touch.x, touch.y)
        MTWidget.on_touch_up(self, touch)
        if touch.id in self.touches:
            del self.touches[touch.id]
            touch.pop()
            return True
        touch.pop()


class MTScatterImage(MTScatterWidget):
    '''MTScatterImage is a image showed in a Scatter widget

    :Parameters:
        `filename` : str
            Filename of image
        `loader` : Loader instance
            Use the loader to load image
    '''
    def __init__(self, **kwargs):
        # Preserve this way to do
        # Later, we'll give another possibility, like using a loader...
        kwargs.setdefault('filename', None)
        if kwargs.get('filename') is None:
            raise Exception('No filename given to MTScatterImage')
        kwargs.setdefault('loader', None)

        super(MTScatterImage, self).__init__(**kwargs)

        # Use loader if available
        loader = kwargs.get('loader')
        if loader:
            self.image  = loader.sprite(kwargs.get('filename'))
        else:
            img         = pyglet.image.load(kwargs.get('filename'))
            self.image  = pyglet.sprite.Sprite(img)

    def draw(self):
        with gx_matrix:
            glScaled(float(self.width)/self.image.width, float(self.height)/self.image.height, 2.0)
            self.image.draw()

class MTScatterSvg(MTScatterWidget):
    '''Render an svg image into a scatter widget

    :Parameters:
        `filename` : str
            Filename of image
        `rawdata` : str
            Raw data of the image. If given, the filename property is used only for cache purposes.
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('filename', None)
        if kwargs.get('filename') is None:
            raise Exception('No filename given to MTSvg')
        kwargs.setdefault('rawdata', None)
        super(MTScatterSvg, self).__init__(**kwargs)
        self.squirt = MTSvg(filename=kwargs.get('filename'), rawdata=kwargs.get('rawdata'))
        self.size = (self.squirt.svg.width, self.squirt.svg.height)

    def draw(self):
        self.squirt.draw()

MTWidgetFactory.register('MTScatterImage', MTScatterImage)
MTWidgetFactory.register('MTScatterPlane', MTScatterPlane)
MTWidgetFactory.register('MTScatterSvg', MTScatterSvg)
MTWidgetFactory.register('MTScatterWidget', MTScatterWidget)

