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
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('rotation', 0.0)
        kwargs.setdefault('translation', (0,0))
        kwargs.setdefault('scale', 1.0)
        kwargs.setdefault('do_scale', True)
        kwargs.setdefault('do_rotation', True)
        kwargs.setdefault('do_translation', True)


        super(MTScatterWidget, self).__init__(**kwargs)

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

        #For flipping animations#
        self.zangle = 0

        #Which side is currently showing
        self.side = 'front'

        #Holds children for both sides
        self.children_front = []
        self.children_back = []

        self.children = self.children_front

        self.anim = Animation(self, 'flip', 'zangle', 180, 1, 10, func=AnimationAlpha.ramp)


        self.touches        = {}
        self.transform_mat  = (GLfloat * 16)()
        if kwargs.get('translation')[0] != 0 or kwargs.get('translation')[1] != 0:
            self.init_transform(kwargs.get('translation'), kwargs.get('rotation'), kwargs.get('scale'))
        else:
            self.init_transform(self.pos, kwargs.get('rotation'), kwargs.get('scale'))

    def add_widget(self, w, side='front', front=True):
        '''Override this, because a side needs to be specififed'''
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
            #Add to both
            self.add_widget(w, side='front', front=front)
            self.add_widget(w, side='back', front=front)

        try:
            w.parent = self
        except:
            pass

    def init_transform(self, pos, angle, scale):
        with gx_matrix_identity:
            glTranslated(pos[0], pos[1], 0)
            glScalef(scale, scale, 1)
            glRotated(angle,0,0,1)
            glGetFloatv(GL_MODELVIEW_MATRIX, self.transform_mat)

    def draw(self):
        set_color(*self.color)
        drawRectangle((0,0), (self.width, self.height))

    def flip_children(self):
        '''Flips the children
        this has to be called exactly half way through the animation
        so it looks like there are actually two sides'''
        if self.side == 'front':
            #Flip to back
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

    def to_parent(self, x,y):
        self.new_point = matrix_mult(self.transform_mat, (x,y,0,1))
        return (self.new_point.x, self.new_point.y)

    def to_local(self,x,y):
        self.new_point = matrix_inv_mult(self.transform_mat, (x,y,0,1))
        return (self.new_point.x, self.new_point.y)

    def collide_point(self, x,y):
        local_coords = self.to_local(x,y)
        if local_coords[0] > 0 and local_coords[0] < self.width \
           and local_coords[1] > 0 and local_coords[1] < self.height:
            return True
        else:
            return False

    def find_second_touch(self, touchID):
        for tID in self.touches.keys():
            x,y = self.touches[tID].x, self.touches[tID].y
            if self.collide_point(x,y) and tID!=touchID:
                return tID
        return None


    def apply_angle_scale_trans(self, angle, scale, trans, point):
        with gx_matrix_identity:
            if self.do_translation:
                glTranslated(trans.x * self.do_translation_x, trans.y * self.do_translation_y, 0)
            glTranslated(point.x, point.y,0)
            if self.do_scale:
                glScaled(scale, scale,1)
            if self.do_rotation:
                glRotated(angle,0,0,1)
            glTranslated(-point.x, -point.y,0)
            glMultMatrixf(self.transform_mat)
            glGetFloatv(GL_MODELVIEW_MATRIX, self.transform_mat)

    def rotate_zoom_move(self, touchID, x, y):
        # some default values, in case we dont calculate them,
        # they still need to be defined for applying the openGL transformations
        intersect = Vector(0,0)
        trans = Vector(0,0)
        rotation = 0
        scale = 1

        # we definitly have one point
        p1_start = Vector(*self.touches[touchID])
        p1_now   = Vector(x,y)

        # if we have a second point, do the scale/rotate/move thing
        second_touch = self.find_second_touch(touchID)
        if second_touch:
            p2_start = Vector(*self.touches[second_touch])
            p2_now   = Vector(*self.touches[second_touch])

            # find intersection between lines...the point around which to rotate
            intersect = Vector.line_intersection(p1_start,  p2_start,p1_now, p2_now)
            if not intersect:
                intersect = Vector(0,0)

            # compute scale factor
            old_dist = p1_start.distance(p2_start)
            new_dist = p1_now.distance(p2_now)
            scale = new_dist/old_dist

            # compute rotation angle
            old_line = p1_start - p2_start
            new_line = p1_now - p2_now
            rotation = -1.0 * old_line.angle(new_line)

        else:
            # just comnpute a translation component if we only have one point
            trans = p1_now - p1_start

        # apply to our transformation matrix
        self.apply_angle_scale_trans(rotation, scale, trans, intersect)

        # save new position of the current touch
        self.touches[touchID] = Vector(x,y)

    def get_scale_factor(self):
        p1_trans = matrix_mult(self.transform_mat, (1,1,0,1))
        p2_trans = matrix_mult(self.transform_mat, (2,1,0,1))
        dist_trans = p1_trans.distance(p2_trans)
        return dist_trans

    def on_touch_down(self, touches, touchID, x,y):
        # if the touch isnt on teh widget we do nothing
        if not self.collide_point(x,y):
            return False

        # let the child widgets handle the event if they want
        lx,ly = self.to_local(x,y)
        if super(MTScatterWidget, self).on_touch_down(touches, touchID, lx, ly):
            return True

        # if teh children didnt handle it, we bring to front & keep track of touches for rotate/scale/zoom action
        self.bring_to_front()
        self.touches[touchID] = Vector(x,y)
        return True

    def on_touch_move(self, touches, touchID, x, y):

        # if the touch isnt on teh widget we do nothing
        if not (self.collide_point(x, y) or touchID in self.touches):
            return False

        #let the child widgets handle the event if they want
        lx, ly = self.to_local(x, y)
        if MTWidget.on_touch_move(self, touches, touchID, lx, ly):
            return True

        #rotate/scale/translate
        if touchID in self.touches:
            self.rotate_zoom_move(touchID, x, y)
            self.dispatch_event('on_resize', int(self.width*self.get_scale_factor()), int(self.height*self.get_scale_factor()))
            self.dispatch_event('on_move', self.x, self.y)
            return True

        #stop porpagation if its within our bounds
        if self.collide_point(x,y):
            return True

    def on_touch_up(self, touches, touchID, x,y):
        #if the touch isnt on the widget we do nothing
        lx,ly = self.to_local(x,y)
        MTWidget.on_touch_up(self, touches, touchID, lx, ly)

        #remove it from our saved touches
        if self.touches.has_key(touchID):
            del self.touches[touchID]

        #stop porpagating if its within our bounds
        if self.collide_point(x,y):
            return True


class MTScatterPlane(MTScatterWidget):
    '''A Plane that transforms for zoom/rotate/pan.
         if none of the childwidgets handles the input (the background is touched), all of tehm are transformed together'''
    def find_second_touch(self, touchID):
        for tID in self.touches.keys():
            if  tID!=touchID:
                return tID
        return None

    def draw(self):
        pass

    def on_touch_down(self, touches, touchID, x,y):
        lx,ly = self.to_local(x,y)
        if super(MTScatterWidget, self).on_touch_down(touches, touchID, lx, ly):
            return True

        self.bring_to_front()
        self.touches[touchID] = Vector(x,y)
        return True

    def on_touch_move(self, touches, touchID, x,y):
        if touchID in self.touches:
            self.rotate_zoom_move(touchID, x, y)
            self.dispatch_event('on_resize', int(self.width*self.get_scale_factor()), int(self.height*self.get_scale_factor()))
            self.dispatch_event('on_move', self.x, self.y)
            return True
        lx,ly = self.to_local(x,y)
        if MTWidget.on_touch_move(self, touches, touchID, lx, ly):
            return True


    def on_touch_up(self, touches, touchID, x,y):
        lx,ly = self.to_local(x,y)
        MTWidget.on_touch_up(self, touches, touchID, lx, ly)
        if self.touches.has_key(touchID):
            del self.touches[touchID]
            return True


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
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('filename', None)
        if kwargs.get('filename') is None:
            raise Exception('No filename given to MTSvg')
        super(MTScatterSvg, self).__init__(**kwargs)
        self.squirt = MTSvg(filename=kwargs.get('filename'))
        self.size = (self.squirt.svg.width, self.squirt.svg.height)

    def draw(self):
        self.squirt.draw()

MTWidgetFactory.register('MTScatterImage', MTScatterImage)
MTWidgetFactory.register('MTScatterPlane', MTScatterPlane)
MTWidgetFactory.register('MTScatterSvg', MTScatterSvg)
MTWidgetFactory.register('MTScatterWidget', MTScatterWidget)

