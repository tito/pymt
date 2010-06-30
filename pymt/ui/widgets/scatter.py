'''
Scatter package: provide lot of widgets based on scatter (base, svg, plane, image...)
'''


__all__ = ['MTScatterWidget', 'MTScatterSvg', 'MTScatterPlane', 'MTScatterImage']

import pymt
from OpenGL.GL import *
from ...graphx import drawRectangle, drawCSSRectangle, gx_matrix, gx_matrix_identity, set_color, \
    drawTexturedRectangle, gx_blending
from ...logger import pymt_logger
from ...vector import Vector, matrix_mult, matrix_inv_mult
from ...utils import deprecated, serialize_numpy, deserialize_numpy
from ..animation import Animation, AnimationAlpha
from ..factory import MTWidgetFactory

from svg import MTSvg
from widget import MTWidget

#new scatter imports
try:
    from ...lib._transformations import *
except:
    from ...lib.transformations import *
import numpy
from math import atan,cos
from OpenGL.GL import glMultMatrixf



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

        kwargs.setdefault('rotation', 0.0)
        kwargs.setdefault('center', (0,0))
        kwargs.setdefault('scale', 1.0)
        kwargs.setdefault('do_scale', True)
        kwargs.setdefault('do_rotation', True)
        kwargs.setdefault('do_translation', True)
        kwargs.setdefault('auto_bring_to_front', True)
        kwargs.setdefault('scale_min', 0.01)
        kwargs.setdefault('scale_max', None)

        super(MTScatter, self).__init__(**kwargs)

        self.register_event_type('on_transform')

        self.auto_bring_to_front = kwargs.get('auto_bring_to_front')
        self.scale_min      = kwargs.get('scale_min')
        self.scale_max      = kwargs.get('scale_max')
        self.do_scale       = kwargs.get('do_scale')
        self.do_rotation    = kwargs.get('do_rotation')
        self.do_translation = kwargs.get('do_translation')
        self.do_translation_x = self.do_translation_y = 1.0
        if type(self.do_translation) == list:
            self.do_translation_x = self.do_translation_y = 0
            if 'x' in self.do_translation:
                self.do_translation_x = 1.0
            if 'y' in self.do_translation:
                self.do_translation_y = 1.0
            self.do_translation = True


        self.touches = []

        self._transform_gl = identity_matrix().T.tolist()  #openGL matrix
        self.transform = identity_matrix()
        self.transform_inv = identity_matrix()
        self._current_transform = identity_matrix()
        self._prior_transform = identity_matrix()


        #inital transformation
        if kwargs.get("pos"):
            pymt_logger.warning('Deprecation Warning: "pos" attribute set in MTScatter constructor. Use "center" instead!!  Using the value given as "pos" for center property.  In scatter pos==center')
            kwargs['center'] = kwargs['pos']
        if kwargs.get("translation"):
            pymt_logger.warning('Deprecation Warning: "translation" attribute set in MTScatter constructor.  Use "center" instead!!  Using the value given as "translation" for center property.  In scatter pos==center')
            kwargs['center'] = kwargs['pos']

        #self.center = kwargs['center']
        self.scale = kwargs['scale']
        self.rotation = kwargs['rotation']

    @property
    def transform_gl(self):
        return self._transform_gl

    def _get_transform_mat(self):
        return self.transform
    def _set_transform_mat(self, x):
        self.reset_transformation_origin()
        self._prior_transform = x
        self.update_matrices()
    transform_mat = property(
        _get_transform_mat,
        _set_transform_mat,
        doc='Get/Set transformation matrix (numpy matrix)')

    def _get_state(self):
        return serialize_numpy(self.transform_mat)
    def _set_state(self, state):
        self.transform_mat = deserialize_numpy(state)
    state = property(
        lambda self: self._get_state(),
        lambda self, x: self._set_state(x),
        doc='Save/restore the state of matrix widget (require numpy)'
    )


    def _get_center(self):
        return self.to_parent(self.width / 2, self.height / 2)
    def _set_center(self, center, do_event=True):
        curr_center = self.center
        if curr_center[0] == center[0] and curr_center[1] == center[1]:
            return
        p1_start = Vector(self.width / 2, self.height / 2)
        p1_now   = Vector(*self.to_local(*center))
        t = p1_now - p1_start
        trans = translation_matrix( (t.x, t.y, 0) )
        self.apply_transform(trans)
        if do_event:
            self.dispatch_event('on_move', *self.pos)
    center = property(_get_center, _set_center)
    pos = property(_get_center, _set_center)

    # Scatter widget don't have write attribute on x/y
    def _get_x(self):
        return self.center[0]
    x = property(_get_x)
    def _get_y(self):
        return self.center[1]
    y = property(_get_y)


    def _get_rotation(self):
        # v1 = vetor from (0,0) to (0,10)
        # v2 = vector from center to center + (0,10) (in widget space)
        v1 = Vector(0,10)
        v2 = Vector(*self.to_parent(*self.pos)) - self.to_parent(self.x, self.y+10)
        angle =  v1.angle(v2)
        #0 is special case, angle is returned as 180, but vectros point in opposite directions
        if angle == 180.0 and v1.normalize()[1] != v2.normalize()[1]:
            return 0
        return angle
    def _set_rotation(self, rotation):
        angle_change = rotation - self.rotation
        print "new rotation: XXXXXX", self.rotation, rotation, angle_change
        trans = translation_matrix( (self.width / 2, self.height / 2, 0) )
        trans = numpy.dot(trans,rotation_matrix( angle_change, (0, 0, 1)))
        trans = numpy.dot(trans,translation_matrix( (-self.width / 2, -self.height / 2, 0) ))
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
        self.apply_transform(scale_matrix(rescale))
        #self.transform_mat = numpy.dot(trans, self.transform)
    scale = property(_get_scale, _set_scale,
                     doc='''Get/set the scaling of the object''')
    _scale = property(_get_scale, _set_scale,
                     doc='''Get/set the scaling of the object''')


    def to_parent(self, x, y, **k):
        p = numpy.dot(self.transform, (x,y,0,1))
        return p[0:2]

    def to_local(self, x, y, **k):
        p = numpy.dot(self.transform_inv, (x,y,0,1))
        return p[0:2]


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
        for t in self.touches:
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
            self._prior_transform = numpy.dot(self._prior_transform,trans)
        else:
            self._prior_transform = numpy.dot(trans, self._prior_transform)
        self.update_matrices()

    def update_matrices(self):
        #compute the OpenGL matrix
        trans = numpy.dot( self._current_transform, self._prior_transform)
        if not is_same_transform(trans, self.transform):
            self.transform = trans
            self.transform_inv = inverse_matrix(self.transform)
            self._transform_gl = self.transform.T.tolist() #for openGL
            self.dispatch_event('on_transform')

    def update_transformation(self):
        #in teh case of one touch, we really just have to translate
        if len(self.touches) == 1:
            dx = self.touches[0].x - self.touches[0].userdata['transform_origin'][0]
            dy = self.touches[0].y - self.touches[0].userdata['transform_origin'][1]
            self._current_transform = translation_matrix((dx,dy,0))
            self.update_matrices()
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

        #old coordinates
        x1 = self.touches[0].userdata['transform_origin'][0]
        y1 = self.touches[0].userdata['transform_origin'][1]
        x2 = self.touches[1].userdata['transform_origin'][0]
        y2 = self.touches[1].userdata['transform_origin'][1]

        #new coordinates
        v = (self.touches[0].x, self.touches[0].y,
             self.touches[1].x, self.touches[1].y )

        #transformation matrix, use 64bit precision
        T = numpy.array(
                ((x1,  y1, 1.0, 0.0),
                 (y1, -x1, 0.0, 1.0),
                 (x2,  y2, 1.0, 0.0),
                 (y2, -x2, 0.0, 1.0)), dtype=numpy.float64 )

        #compute the conformal parameters
        x = numpy.dot(inverse_matrix(T), v)

        a  = x[0]
        b  = x[1]
        tx = x[2] * self.do_translation_x
        ty = x[3] * self.do_translation_y

        angle = atan(b/a)
        scale = a/cos(angle)

        #concatenate transformations based on whther tehy are tunred on/off
        trans = translation_matrix( (tx, ty, 0) )
        if self.do_scale:
            trans = numpy.dot( trans, scale_matrix(scale))
        if self.do_rotation:
            trans = numpy.dot(trans, rotation_matrix( -angle, (0, 0, 1)))

        #update tranformations
        self._current_transform = trans
        self.update_matrices()

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
        self.touches.append(touch)
        self.reset_transformation_origin()
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
        if touch in self.touches and touch.grab_current == self:
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
        if touch in self.touches and touch.grab_state:
            touch.ungrab(self)
            self.touches.remove(touch)
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



class MTScatterWidget(MTScatter):
    pass


"""
class MTScatterWidget(MTWidget):
    '''MTScatterWidget is a scatter widget based on MTWidget.
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
        kwargs.setdefault('auto_bring_to_front', True)
        kwargs.setdefault('scale_min', 0.01)
        kwargs.setdefault('scale_max', None)

        super(MTScatterWidget, self).__init__(**kwargs)

        self.register_event_type('on_transform')

        self.auto_bring_to_front = kwargs.get('auto_bring_to_front')
        self.scale_min      = kwargs.get('scale_min')
        self.scale_max      = kwargs.get('scale_max')
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

        self.touches        = {}
        self._scale         = 1.
        self._rotation      = 0.
        self._transform_mat  = (GLfloat * 16)()
        if kwargs.get('translation')[0] != 0 or kwargs.get('translation')[1] != 0:
            self.init_transform(kwargs.get('rotation'), kwargs.get('scale'), kwargs.get('translation'))
        else:
            self.init_transform(kwargs.get('rotation'), kwargs.get('scale'), super(MTScatterWidget, self).pos)

    def _get_transform_mat(self):
        return self._transform_mat
    def _set_transform_mat(self, x):
        self._transform_mat = x
    transform_mat = property(
        _get_transform_mat,
        _set_transform_mat,
        doc='Get/Set transformation matrix (numpy matrix)')

    def on_transform(self, *largs):
        pass

    def init_transform(self, angle, scale, trans, point=(0, 0)):
        '''Initialize transformation matrix with new parameters.

        :Parameters:
            `angle` : float
                Initial rotation angle
            `scale` : float
                Initial scaling
            `trans` : Vector
                Initial translation vector
            `point` : Vector, default to (0, 0)
                Initial point to apply transformation
        '''
        if scale < self.scale_min:
            scale = self.scale_min
        if self.scale_max is not None and scale > self.scale_max:
            scale = self.scale_max
        self._scale = scale
        self._rotation = angle
        with gx_matrix_identity:
            glTranslatef(trans[0], trans[1], 0)
            glTranslatef(point[0], point[1], 0)
            glScalef(scale, scale, 1)
            glRotatef(angle,0,0,1)
            glTranslatef(-point[0], -point[1], 0)
            self.transform_mat = glGetFloatv(GL_MODELVIEW_MATRIX)

    def draw(self):
        set_color(*self.style['bg-color'])
        drawCSSRectangle((0,0), (self.width, self.height), style=self.style)

    def on_draw(self):
        if not self.visible:
            return
        with gx_matrix:
            glMultMatrixf(self.transform_mat)
            super(MTScatterWidget, self).on_draw()

    def to_parent(self, x, y):
        point = matrix_mult(self.transform_mat, (x, y, 0, 1))
        return (point.x, point.y)

    def to_local(self, x, y):
        point = matrix_inv_mult(self.transform_mat, (x, y, 0, 1))
        return (point.x, point.y)

    def collide_point(self, x, y):
        if not self.visible:
            return False
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

    def apply_angle_scale_trans(self, angle, scale, trans, point=Vector(0, 0)):
        '''Update matrix transformation by adding new angle, scale and translate.

        :Parameters:
            `angle` : float
                Rotation angle to add
            `scale` : float
                Scaling value to add
            `trans` : Vector
                Vector translation to add
            `point` : Vector, default to (0, 0)
                Point to apply transformation
        '''
        old_scale = self.scale
        self._scale *= scale
        if self._scale < self.scale_min or \
           self.scale_max is not None and self._scale > self.scale_max:
            self._scale = old_scale
            scale = 1
        self._rotation = (self._rotation + angle) % 360
        with gx_matrix_identity:
            if self.do_translation:
                glTranslatef(trans.x * self.do_translation_x, trans.y * self.do_translation_y, 0)
            glTranslatef(point.x, point.y, 0)
            if self.do_scale:
                glScalef(scale, scale, 1)
            if self.do_rotation:
                glRotatef(angle, 0, 0, 1)
            glTranslatef(-point.x, -point.y,0)
            glMultMatrixf(self.transform_mat)
            self.transform_mat = glGetFloatv(GL_MODELVIEW_MATRIX)

        self.dispatch_event('on_transform', angle, scale, trans, point)

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
        curr_center = self.center
        if curr_center[0] == center[0] and curr_center[1] == center[1]:
            return
        p1_start = Vector(self._get_x(),self._get_y())
        p1_now   = Vector(*center)
        trans = p1_now - p1_start
        self.apply_angle_scale_trans(0, 1.0, trans, Vector(*center))
        center = self.to_local(*self.to_parent(0, 0))
        if self._pos[0] == center[0] and self._pos[1] == center[1]:
            return
        self._pos = center
        if do_event:
            self.dispatch_event('on_move', *self.pos)
    center = property(_get_center, _set_center)
    pos = property(_get_center, _set_center)

    # Scatter widget don't have write attribute on x/y
    def _get_x(self):
        return self.center[0]
    x = property(_get_x)
    def _get_y(self):
        return self.center[1]
    y = property(_get_y)

    @deprecated
    def get_scale_factor(self, use_gl=False):
        '''Return the current scale factor.
        By default, the calculated scale is returned. You can set use_gl to
        calculate scale factor with opengl operation. Precision is not the
        same between them.

        Exemple for a scale factor ::

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

        # grab touch to not loose it
        touch.grab(self)

        # bring to front the widget is asked
        if self.auto_bring_to_front:
            self.bring_to_front()

        self.touches[touch.uid] = Vector(x, y)
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
        if touch.uid in self.touches and touch.grab_current == self:

            # check if we got multiple touch, if current touch
            # have kinetic activated, and they are other touch
            if 'kinetic' in touch.profile and touch.mode == 'spinning' \
                and len(self.touches) > 1 and self.find_second_touch(touch.uid):

                # suppress the touch
                touch.ungrab(self)
                del self.touches[touch.uid]

                return True

            # apply the rotate/zoom/move
            self.rotate_zoom_move(touch.uid, x, y)

            # dispatch move event
            #self._set_center(self.to_parent(0, 0), do_event=False)
            center = self.to_local(*self.to_parent(0, 0))
            if self._pos[0] == center[0] and self._pos[1] == center[1]:
                return
            self._pos = center
            self.dispatch_event('on_move', *self._pos)
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
        if touch.uid in self.touches and touch.grab_state:
            touch.ungrab(self)
            del self.touches[touch.uid]

        # stop porpagating if its within our bounds
        if self.collide_point(x, y):
            return True

    def _get_rotation(self):
        return self._rotation
    def _set_rotation(self, rotation):
        rotation = (rotation - self._rotation) % 360
        self.apply_angle_scale_trans(rotation, 1., Vector(0, 0), Vector(*self.pos))
    rotation = property(_get_rotation, _set_rotation,
                        doc='''Get/set the rotation of the object (in degree)''')

    def _get_scale(self):
        return self._scale
    def _set_scale(self, scale):
        if self._scale == 0:
            self._scale = 1
        scale = scale / self._scale
        self.apply_angle_scale_trans(0, scale, Vector(0, 0), Vector(*self.pos))
    scale = property(_get_scale, _set_scale,
                     doc='''Get/set the scaling of the object''')

    def _get_state(self):
        return serialize_numpy(self.transform_mat)
    def _set_state(self, state):
        self.transform_mat = deserialize_numpy(state)
        p1_trans = matrix_mult(self.transform_mat, (1,1,0,1))
        p2_trans = matrix_mult(self.transform_mat, (2,1,0,1))
        self._scale = p1_trans.distance(p2_trans)
    state = property(
        lambda self: self._get_state(),
        lambda self, x: self._set_state(x),
        doc='Save/restore the state of matrix widget (require numpy)'
    )
"""


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
