'''
Scatter package: provide lot of widgets based on scatter (base, svg, plane, image...)
'''

__all__ = ('MTScatterWidget', 'MTScatterSvg', 'MTScatterPlane',
           'MTScatterImage')

import pymt
from pymt.logger import pymt_logger
from numpy import array, dot, float64

try:
    from pymt.c_ext._transformations import *
except ImportError:
    pymt_logger.warning('Unable to import accelerated transformation, falling back to plain python.');
    from pymt.lib.transformations import *

from math import atan,cos, radians, degrees
from OpenGL.GL import *

from pymt.graphx import drawRectangle, drawCSSRectangle, gx_matrix, gx_matrix_identity, set_color, \
    drawTexturedRectangle, gx_blending, drawTriangle
from pymt.vector import Vector, matrix_mult, matrix_inv_mult
from pymt.utils import deprecated, serialize_numpy, deserialize_numpy
from pymt.ui.animation import Animation, AnimationAlpha
from pymt.ui.factory import MTWidgetFactory
from pymt.ui.widgets.widget import MTWidget
from pymt.ui.widgets.svg import MTSvg


class MTScatter(MTWidget):
    '''MTScatter is a scatter widget based on MTWidget.
    You can scale, rotate and move with one and two finger.

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
        `auto_bring_to_front` : boolean, default to True
            Set to False for disabling widget bring to front
        `scale_min` : float, default to 0.01
            Minimum scale allowed. Don't set to 0, or you can have error with singular matrix.
            The 0.01 mean you can de-zoom up to 10000% (1/0.01*100).
        `scale_max` : float, default to None
            Maximum scale allowed.

    :Events:
        `on_transform` (rotation, scale, trans, intersect)
            Fired whenever the Scatter Widget is transformed (rotate, scale, moved, or zoomed).
    '''

    def __init__(self, **kwargs):

        kwargs.setdefault('pos', (0,0))
        kwargs.setdefault('center', (0,0))
        kwargs.setdefault('rotation', 0.0)
        kwargs.setdefault('scale', 1.0)

        super(MTScatter, self).__init__(**kwargs)

        self.register_event_type('on_transform')

        self.auto_bring_to_front = kwargs.get('auto_bring_to_front', True)
        self.scale_min      = kwargs.get('scale_min', 0.01)
        self.scale_max      = kwargs.get('scale_max', None)
        self.do_scale       = kwargs.get('do_scale', True)
        self.do_rotation    = kwargs.get('do_rotation', True)
        self.do_translation = kwargs.get('do_translation', True)

        # private properties
        self._touches = []

        self._transform = identity_matrix()
        self._transform_inv = identity_matrix()
        self._transform_gl = identity_matrix().T.tolist()  #openGL matrix
        self._transform_inv_gl = identity_matrix().T.tolist()  #openGL matrix
        self._current_transform = identity_matrix()
        self._prior_transform = identity_matrix()

        self.update_matrices()

        #inital transformation
        self.center = kwargs['center']
        self.pos = kwargs['pos']
        self.scale = kwargs['scale']
        self.rotation = kwargs['rotation']


    def _get_do_translation(self):
        return self._do_translation
    def _set_do_translation(self, val):
        self._do_translation = val
        self._do_translation_x = self._do_translation_y = 0.0
        if type(val) in (list, tuple, str):
            if 'x' in self.do_translation:
                self._do_translation_x = 1.0
            if 'y' in self.do_translation:
                self._do_translation_y = 1.0
        elif val:
            self._do_translation_x = self._do_translation_y = 1.0
    do_translation = property(_get_do_translation, _set_do_translation)


    def _get_transform_gl(self):
        return self._transform_gl
    transform_gl = property(_get_transform_gl,
        doc = " Return the transformation matrix for OpenGL,  read only!'")

    @deprecated
    def _get_transform_mat(self):
        '''Use transform_gl for an OpenGL transformation instead.'''
        return self._transform_gl
    transform_mat = property(_get_transform_mat,
        doc = "DEPRECATED Return the transformation matrix for OpenGL,  read only!'")


    def _get_transform_inv_gl(self):
        return self._transform_inv_gl
    transform_inv_gl = property(_get_transform_inv_gl,
        doc = " Return the inverse transformation matrix for OpenGL,  read only!'")

    def _get_transform(self):
        return self._transform
    def _set_transform(self, x):
        self.reset_transformation_origin()
        self._prior_transform = x
        self.update_matrices()
    transform = property(_get_transform, _set_transform,
        doc='Get/Set transformation matrix (numpy matrix)')

    def _get_transform_inv(self):
        return self._transform_inv
    transform_inv = property(_get_transform_inv,
        doc = "Inverse of transformation matrix (numpy matrix),  read only!'")

    def _get_state(self):
        return serialize_numpy(self._transform)
    def _set_state(self, state):
        self.transform = deserialize_numpy(state)
    state = property(
        lambda self: self._get_state(),
        lambda self, x: self._set_state(x),
        doc='Save/restore the state of matrix widget (require numpy)'
    )

    @property
    def bbox(self):
        '''
        Returns teh bounding box of teh widget in parent space
            returns "bbox":  ((x,y),(w,h))  x,y = lower left corner
        '''
        xmin, ymin = xmax, ymax = self.to_parent(0,0)
        for point in [(self.width,0),(0, self.height), self.size]:
            x,y = self.to_parent(*point)
            if x < xmin: xmin = x
            if y < ymin: ymin = y
            if x > xmax: xmax = x
            if y > ymax: ymax = y
        return (xmin, ymin), (xmax-xmin, ymax-ymin)

    def _get_center(self):
        return (self.bbox[0][0] + self.bbox[1][0]/2.0,
                self.bbox[0][1] + self.bbox[1][1]/2.0)
    def _set_center(self, center):
        trans = Vector(*center) - self.center
        new_pos = trans + self.pos
        self.pos = new_pos
    center = property(_get_center, _set_center)

    def _get_pos(self):
        return self.bbox[0]
    def _set_pos(self, pos):
        _pos = self.bbox[0]
        if pos == _pos:
            return False
        t = Vector(*pos) - _pos
        trans = translation_matrix( (t.x, t.y, 0) )
        self.apply_transform(trans)
        return True
    pos = property(_get_pos, _set_pos,
                   doc='Object position (x, y).  Lower left of bounding box for rotated scatter')

    def _get_x(self):
        return self.pos[0]
    def _set_x(self, x):
        if x == self.pos[0]:
            return False
        self.pos = (x, self.y)
        return True
    x = property(_get_x, _set_x,
                 doc = 'Object X position')

    def _get_y(self):
        return self.pos[1]
    def _set_y(self, y):
        if y == self.pos[1]:
            return False
        self.pos = (self.x, y)
        return True
    y = property(_get_y, _set_y,
                 doc = 'Object Y position')


    def _get_rotation(self):
        # v1 = vetor from (0,0) to (0,10)
        # v2 = vector from center to center + (0,10) (in widget space)
        v1 = Vector(0,10)
        v2 = Vector(*self.to_parent(*self.pos)) - self.to_parent(self.x, self.y+10)
        return -1.0 *(v1.angle(v2) + 180) % 360
    def _set_rotation(self, rotation):
        angle_change = self.rotation - rotation
        trans = translation_matrix( (self.width / 2, self.height / 2, 0) )
        trans = dot(trans,rotation_matrix( -radians(angle_change), (0, 0, 1)))
        trans = dot(trans,translation_matrix( (-self.width / 2, -self.height / 2, 0) ))
        self.apply_transform(trans,post_multiply=True)
    rotation = property(_get_rotation, _set_rotation,
                        doc='''Get/set the rotation of the object (in degree)''')


    def _get_scale(self):
        p1 = Vector(*self.to_parent(0,0))
        p2 = Vector(*self.to_parent(1,0))
        scale = p1.distance(p2)
        return scale
    def _set_scale(self, scale):
        scale_now = self.scale
        rescale = scale * (1.0/scale_now)
        trans = translation_matrix( (self.width / 2, self.height / 2, 0) )
        trans = dot(trans,scale_matrix(rescale))
        trans = dot(trans,translation_matrix( (-self.width / 2, -self.height / 2, 0) ))
        self.apply_transform(trans,post_multiply=True)
    scale = property(_get_scale, _set_scale,
                     doc='''Get/set the scaling of the object''')
    _scale = property(_get_scale, _set_scale,
                     doc='''Get/set the scaling of the object''')


    def to_parent(self, x, y, **k):
        p = dot(self._transform, (x,y,0,1))
        return (p[0],p[1])

    def to_local(self, x, y, **k):
        p = dot(self._transform_inv, (x,y,0,1))
        return (p[0],p[1])

    def collide_point(self, x, y):
        if not self.visible:
            return False
        local_coords = self.to_local(x, y)
        if local_coords[0] > 0 and local_coords[0] < self.width \
           and local_coords[1] > 0 and local_coords[1] < self.height:
            return True
        else:
            return False

    def reset_transformation_origin(self):
        for t in self._touches:
            t.userdata['transform_origin'] = t.pos

        trans = self._current_transform
        self._current_transform = identity_matrix()
        self.apply_transform(trans)

    def apply_transform(self, trans, post_multiply=False):
        '''
        transforms scatter by trans (on top of its current transformation state
        args:
            trans, transformation to be applied to teh scatter widget)
        '''
        if post_multiply:
            self._prior_transform = dot(self._prior_transform, trans)
        else:
            self._prior_transform = dot(trans, self._prior_transform)
        self.update_matrices()

    def update_matrices(self):
        #compute the OpenGL matrix
        trans = dot( self._current_transform, self._prior_transform)
        if not is_same_transform(trans, self._transform):
            self._transform = trans
            self._transform_inv = inverse_matrix(self._transform)
            self._transform_gl = self._transform.T.tolist() #for openGL
            self._transform_inv_gl = self._transform.T.tolist() #for openGL
            self.dispatch_event('on_transform')

    def update_transformation(self):
        if not self._touches:
            return

        # optimization
        touch0 = self._touches[0]

        # in the case of one touch, we really just have to translate
        if len(self._touches) == 1:
            dx = (touch0.x - touch0.userdata['transform_origin'][0]) * self._do_translation_x
            dy = (touch0.y - touch0.userdata['transform_origin'][1]) * self._do_translation_x
            self._current_transform = translation_matrix((dx,dy,0))
            self.update_matrices()
            return
        else:
            touch1 = self._touches[1]

        #if the twon fingers are too close dont compute...would cause div by zero error or singular matrix transform
        dist = Vector(*touch0.pos).distance(touch1.pos)
        if dist < 2: #in pixels
            return

        #two or more touches...lets do some math!
        """
        heres an attempt at an exmplanation of the math

        we are given two sets of points P1,P2 and P1',P2' (before and after)
        now we are trying to compute the transformation that takes both
        P1->P1' and P2->P2'.  To do this, we have to rely on teh fact that
        teh affine transformation we want is conformal.

        because we know we want a 2D conformal transformation (no shearing, stretching etc)
        we can state the following:

            P1' = M*P1 + t
            P2' = M*P2 + t

            where:
            M is a 2x2 matrix that describes the rotation and scale of the transformation
            t is a 2X1 vector that descrobes the translation of the transformation

        becasue this is a conformal affine transformation (only rotation and scale in M)
        we also know that we can write M as follows:
            |  a  b |
            | -b  a |

            where:
            a = scale * cos(angle)
            b = scale * sin(angle)

        given this and the two equations above, we can rewrite as a system of linear equations:
            x1' =  a*x1 + b*y1 + cx
            y1' = -b*x1 + a*y1 + cy
            x2' =  a*x2 + b*y2 + cx
            y2' = -b*x1 + a*y2 + cy

        the easiest way to solve this is to construct a matrix that takes (a,b,tx,ty)-> (x1',y1',x2',y2')
        and then take its inverse so we can computer a,b,tx,ad ty from the known parameters

           v    =          T         *    x

         |x1'|     | x1  y1  1  0 |      | a|  (notice how multiplying this gives teh 4 equations above)
         |y1'|  =  | y1 -x1  0  1 |  *   | b|
         |x2'|     | x2  y2  1  0 |      |tx|
         |y2'|     | y2 -x2  0  1 |      |ty|

        Now we can easily compute x by multiplying both sides by the inverse of T

            inv(T) * v = inv(T)*T *x  (everything but x cancels out on the right)

        once we have a,b,tx, and ty, we just have to extract teh angle and scale

            angle = artan(b/a)     (based on teh definitionsof a and b above)
            scale = a/cos(angle)
        """

        # old coordinates
        x1, y1 = touch0.userdata['transform_origin']
        x2, y2 = touch1.userdata['transform_origin']

        # new coordinates
        v = (touch0.x, touch0.y, touch1.x, touch1.y)

        # transformation matrix, use 64bit precision
        T = array(
            ((x1,  y1, 1.0, 0.0),
             (y1, -x1, 0.0, 1.0),
             (x2,  y2, 1.0, 0.0),
             (y2, -x2, 0.0, 1.0)), dtype=float64 )

        #compute the conformal parameters
        x = dot(inverse_matrix(T), v)

        a  = x[0]
        b  = x[1]
        tx = x[2] 
        ty = x[3] 

        angle = atan(b / a)
        scale = a / cos(angle)

        old_center = self.center
        old_scale = self.scale
        old_rotation = self.rotation

        # concatenate transformations to find new transform and update tranformations
        trans = translation_matrix( (tx, ty, 0) )
        trans = dot( trans, scale_matrix(scale))
        trans = dot(trans, rotation_matrix( -angle, (0, 0, 1)))
        self._current_transform = trans
        self.update_matrices()

        if not self.do_scale:
            self.scale = old_scale
        if not self.do_rotation:
            self.rotation = old_rotation
        if (not self._do_translation_x) and (not self._do_translation_y):
            self.reset_transformation_origin()
            if self._do_translation_x:
                self.center = (self.center[0], old_center[1])
            elif self._do_translation_y:
                self.center = (old_center[0], self.center[1])
            else:
                self.center = old_center

    def on_transform(self, *largs):
        pass

    def on_touch_down(self, touch):
        x, y = touch.x, touch.y

        # if the touch isnt on the widget we do nothing
        if not self.collide_point(x, y):
            return False

        # let the child widgets handle the event if they want
        touch.push()
        touch.x, touch.y = self.to_local(x, y)
        if super(MTScatter, self).on_touch_down(touch):
            touch.pop()
            return True
        touch.pop()

        #grab the touch so we get all it later move events for sure
        touch.grab(self)
        self._touches.append(touch)
        self.reset_transformation_origin()

        #bring to front if auto_bring to front is on
        if self.auto_bring_to_front:
            self.bring_to_front()

        return True

    def on_touch_move(self, touch):
        x, y = touch.x, touch.y

        # let the child widgets handle the event if they want
        if self.collide_point(x, y) and not touch.grab_current == self:
            touch.push()
            touch.x, touch.y = self.to_local(x, y)
            if super(MTScatter, self).on_touch_move(touch):
                touch.pop()
                return True
            touch.pop()

        # rotate/scale/translate
        if touch in self._touches and touch.grab_current == self:
            self.update_transformation()

        # stop porpagating if its within our bounds
        if self.collide_point(x, y):
            return True

    def on_touch_up(self, touch):
        x, y = touch.x, touch.y

        # if the touch isnt on the widget we do nothing
        if not touch.grab_state:
            touch.push()
            touch.x, touch.y = self.to_local(x, y)
            if super(MTScatter, self).on_touch_up(touch):
                touch.pop()
                return True
            touch.pop()

        # remove it from our saved touches
        if touch in self._touches and touch.grab_state:
            touch.ungrab(self)
            self._touches.remove(touch)
            self.reset_transformation_origin()

        # stop porpagating if its within our bounds
        if self.collide_point(x, y):
            return True

    def on_draw(self):
        if not self.visible:
            return
        with gx_matrix:
            glMultMatrixf(self._transform_gl)
            super(MTScatter, self).on_draw()

    def draw(self):
        set_color(*self.style['bg-color'])
        drawCSSRectangle((0,0), (self.width, self.height), style=self.style)


class MTScatterWidget(MTScatter):
    '''This class is deprecated, you should use MTScatter now.'''
    pass


class MTScatterPlane(MTScatterWidget):
    '''A Plane that transforms for zoom/rotate/pan.
    if none of the childwidgets handles the input
    (the background is touched), all of them are transformed
    together
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('auto_bring_to_front', False)
        super(MTScatterPlane, self).__init__(**kwargs)

    def draw(self):
        pass

    def collide_point(self, x, y):
        return self.visible


class MTScatterImage(MTScatterWidget):
    '''MTScatterImage is a image showed in a Scatter widget

    :Parameters:
        `filename` : str
            Filename of image
        `image` : Image
            Instead of using filename, use a Image object
        `opacity` : float, default to 1.0
            Used to set the opacity of the image.
        `scale` : float, default is 1.0
            Scaling of image, default is 100%, ie 1.0
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('filename', None)
        kwargs.setdefault('opacity', 1.0)
        kwargs.setdefault('scale', 1.0)
        kwargs.setdefault('image', None)
        if kwargs.get('filename') is None and kwargs.get('image') is None:
            raise Exception('No filename or image given to MTScatterImage')

        super(MTScatterImage, self).__init__(**kwargs)
        self.image          = kwargs.get('image')
        self.scale          = kwargs.get('scale')
        self.filename       = kwargs.get('filename')
        self.opacity        = kwargs.get('opacity')
        self.size           = self.image.size

    def _get_filename(self):
        return self._filename
    def _set_filename(self, filename):
        self._filename = filename
        if filename:
            self.image = pymt.Image(self.filename)
    filename = property(_get_filename, _set_filename)

    def draw(self):
        self.size           = self.image.size
        self.image.opacity  = self.opacity
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
