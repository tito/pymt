'''
Kinetic List: Custom list with kinetic interaction
'''

__all__ = ['MTKineticList', 'MTKineticObject', 'MTKineticItem', 'MTKineticImage']

import pymt
from pyglet.gl import *
from pyglet.text import Label
from ....graphx import set_color, drawRectangle
from ....graphx import drawCSSRectangle
from ...factory import MTWidgetFactory
from ....vector import Vector
from ....mtpyglet import getFrameDt
from ..stencilcontainer import MTStencilContainer
from ..widget import MTWidget
from ..button import MTButton, MTToggleButton, MTImageButton
from ...animation import Animation, AnimationAlpha

class MTKineticList(MTStencilContainer):
    '''This is a kinetic container widget, that allows you to make
    a kinetic list scrolling in either direction.

    :Parameters:
        `friction` : float, defaults to 10
            The Pseudo-friction of the pseudo-kinetic scrolling.
            Formula for friction is ::
                acceleration = 1 + friction * frame_delta_time
        `padding_x` : int, defaults to 4
            The spacing between scrolling items on the x axis
        `padding_y` : int, defaults to 4
            The spacing between scrolling items on the y axis
        `w_limit` : int, defaults to 1
            The limit of items that will appear horizontally.
            When this is set to a non-zero value the width(in
            terms of items in the kinetic list) will be w_limit,
            and the height will continually expand.
        `h_limit` : int, defaults to 0
            Exect opposite of w_limit.  If I didn't make either
            this or w_limit clear go bug xelapond
        `do_x` : bool, defaults to False
            Enable scrolling on the X axis
        `do_y` : bool, defaults to True
            Enable scrolling on the Y axis
        `title` : string, defaults to <Title Goes Here>
            Sets the title of the widget, which appears in 20
            point font at the top
        `deletable` : bool, defaults to True
            When enabled it allows you to delete children by
            entering delete mode(red button in upper left)
        `searchable` : bool, defaults to True
            When enabled it allows you to enter search mode
            and filter items
        `trigger_distance` : int, default to 8
            Maximum trigger distance to dispatch event on children
            (this mean if you move too much, trigger will not happen.)

    :Styles:
        `bg-color` : color
             Background color of the widget

    :Events:
        `on_press` (child, callback)
            Fired when a specific item has been tapped and moved
            less then forty pixels(so we know they tapped it, didn't
            try and scroll).  It sends the item tapped, and the return
            item(if none was defined it sends None)
        `on_delete` (child, callback)
            Fired when an item gets deleted.  Passes that item and the
            return item(None if not provided).
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('friction', 10)
        kwargs.setdefault('padding_x', 4)
        kwargs.setdefault('padding_y', 4)
        kwargs.setdefault('w_limit', 1)
        kwargs.setdefault('h_limit', 0)
        kwargs.setdefault('do_x', False)
        kwargs.setdefault('do_y', True)
        kwargs.setdefault('title', 'No title')
        kwargs.setdefault('deletable', True)
        kwargs.setdefault('searchable', True)
        kwargs.setdefault('trigger_distance', 8)

        super(MTKineticList, self).__init__(**kwargs)
        self.register_event_type('on_press')
        self.register_event_type('on_delete')

        self.do_x       = kwargs.get('do_x')
        self.do_y       = kwargs.get('do_y')
        self.titletext  = kwargs.get('title')
        self.deletable  = kwargs.get('deletable')
        self.searchable = kwargs.get('searchable')
        self.friction   = kwargs.get('friction')
        self.padding_x  = kwargs.get('padding_x')
        self.padding_y  = kwargs.get('padding_y')
        self.w_limit    = kwargs.get('w_limit')
        self.h_limit    = kwargs.get('h_limit')
        self.trigger_distance = kwargs.get('trigger_distance')

        if self.w_limit and self.h_limit:
            raise Exception('You cannot limit both axes')
        elif not(self.w_limit or self.h_limit):
            raise Exception('You must limit at least one axis')

        # How far to offset the axes(used for scrolling/panning)
        self.xoffset = 0
        self.yoffset = 0
        # X and Y translation vectors for the kinetic movement
        self.vx = 0
        self.vy = 0
        # List of all children, whatever will be the search
        self.pchildren = []
        # For extra blob stats
        self.touch = {}
        # Holds widgets not a part of the scrolling(search button, etc)
        self.widgets = []
        self.content_size = Vector(0, 0)

        # create the UI part.
        self._create_ui()

    def _create_ui(self):
        # Title Text
        if self.titletext is not None:
            self.title = Label(
                font_size=18,
                bold=True,
                anchor_x='center',
                anchor_y='center',
                text=self.titletext)
            self.title.x = self.width/2 + self.x
            self.title.y = self.height - 20 + self.y

        # Delete Button
        if self.deletable:
            self.db = MTToggleButton(
                label='X',
                pos=(self.x + self.width - 80, self.y + self.height - 40),
                size=(80, 40),
                cls='kineticlist-delete')
            self.db.push_handlers(on_press=self.toggle_delete)
            self.widgets.append(self.db)

        # Search Button and Input Text Area
        if self.searchable:
            self.sb = MTToggleButton(
                label='S',  #Button
                pos=(self.x, self.y + self.width - 40),
                size=(80, 40),
                cls='kineticlist-search')

            self.sb.push_handlers(on_press=self.toggle_search)
            self.sb.parent = self
            self.widgets.append(self.sb)

            self.sinput = pymt.MTTextInput(pos=
                (self.x, self.y + self.height - 40), size=(80, 40),
                style={'font-size': 20})
            self.sinput.parent = self
            self.sinput.push_handlers(on_text_change=self.apply_filter)
            self.widgets.append(self.sinput)

            # Animations to hide and show the search text input box
            self.a_sinput_in = Animation(self.sinput, 'Move In',
                'y', self.y + self.height - 40 - self.sinput.size[1], 1, 10)
            self.a_sinput_out = Animation(self.sinput, 'Move Out',
                'y', self.y + self.height - self.sinput.size[1], 1, 10)

    def on_press(self, child, callback):
        if callback is not None:
            callback('press', child)

    def on_delete(self, child, callback):
        if callback is not None:
            callback('delete', child)

    def clear(self):
        self.children = []
        self.pchildren = []
        self.xoffset = self.yoffset = 0

    def add_widget(self, widget):
        super(MTKineticList, self).add_widget(widget)
        self.pchildren.append(widget)

    def remove_widget(self, widget):
        super(MTKineticList, self).remove_widget(widget)
        if widget in self.pchildren:
            self.pchildren.remove(widget)

    def toggle_delete(self, touch):
        '''Toggles the delete buttons on items
        Attached to the on_press handler of the delete button(self.db)
        '''
        for child in self.children:
            if self.db.get_state() == 'down':
                child.show_delete()
            else:
                child.hide_delete()

    def toggle_search(self, touch):
        '''Toggles the search area
        Attached to the on_press handler of self.sb(the green search button)
        '''
        if self.sb.get_state() == 'down':
            self.a_sinput_in.reset()
            self.a_sinput_in.start()
        else:
            try:
                self.sinput.hide_keyboard()
            except:
                #There isn't a keyboard, so it throws a ValueError
                pass
            self.sinput.label = ''
            self.a_sinput_out.reset()
            self.a_sinput_out.start()
            self.endsearch()

    def apply_filter(self, text):
        '''Applies the filter to the current children set'''
        self.search(text, 'label')
        #Move them so you don't have to scroll up to see them
        self.yoffset = self.padding_y
        self.xoffset = self.padding_x

    def filter(self, pattern, attr):
        '''Given an attribute of the children, and a pattern, return
        a list of the children with which pattern is in attr
        '''
        return filter(lambda c: pattern in str(getattr(c, attr)), self.pchildren)

    def search(self, pattern, attr):
        '''Apply a search pattern to the current set of children'''
        self.children = self.filter(pattern, attr)

    def endsearch(self):
        '''Resets the children set to the full set'''
        self.children = self.pchildren

    def _get_total_width(self, items, axis):
        '''Given a list of items and an axis, return the space
        they take up(in pixels)
        '''
        total = 0
        if axis == 'width':
            for item in items:
                total += (item.width + self.padding_x)
        elif axis == 'height':
            for item in items:
                total+= (item.height + self.padding_y)

        return total

    def goto_head(self):
        if not self.h_limit:
            self.yoffset = -self._get_total_width(self.children, 'height')/self.w_limit + self.size[1] - 100
        else:
            self.xoffset = self._get_total_width(self.children, 'width')/self.h_limit + self.size[0] - 100

    def do_layout(self):
        '''Apply layout to all the items'''

        t = index = 0
        self.content_size = Vector(0, 0)

        # adapt value for direction
        w2          = self.width / 2.
        h2          = self.height / 2.
        inverse     = 0
        limit       = self.w_limit
        width_attr  = 'width'
        height_attr = 'height'
        xoffset     = self.xoffset
        yoffset     = self.yoffset
        sx, sy      = self.x, self.y
        y           = self.y + self.yoffset
        padding_x   = self.padding_x
        padding_y   = self.padding_y

        # inverse
        if not self.w_limit:
            inverse     = 1
            limit       = self.h_limit
            width_attr  = 'height'
            height_attr = 'width'
            xoffset      = self.yoffset
            yoffset      = self.xoffset
            y           = self.x + self.xoffset
            padding_x   = self.padding_y
            padding_y   = self.padding_x
            w2, h2      = h2, w2
            sx, sy      = self.y, self.x

        # add little padding for good looking.
        y += padding_y

        # recalculate position for each children
        for child in self.children:

            # each row, calculate the height, advance y and reset x
            if index % limit == 0:

                # get children in the row
                maxrange = min(t + limit, len(self.children))
                childrens = [self.children[z] for z in range(t, maxrange)]

                # take the largest height in the current row
                if len(childrens):
                    h = max((c.__getattribute__(height_attr) for c in childrens))
                else:
                    h = 0

                # in the very first loop, don't add padding.
                if index > 0:
                    y += padding_y + h

                # reset x for this row.
                x = sx + w2 + xoffset - \
                    (self._get_total_width(childrens, width_attr) / 2.)
                t += limit

            # reposition x
            if not inverse:
                child.kx = x + padding_x
                child.ky = y
            else:
                child.ky = x + padding_x
                child.kx = y
            x += child.__getattribute__(width_attr) + padding_x

            # Increment index
            index += 1

    def on_touch_down(self, touch):
        if not self.collide_point(touch.x, touch.y):
            return

        # ok, it's a touch for us. grab it !
        touch.grab(self)

        # first, check if own widget take the touch
        for w in self.widgets:
            if w.on_touch_down(touch):
                return True

        # initiate kinetic movement.
        lx, ly = self.to_local(*touch.pos)
        self.vx = self.vy = 0
        self.touch[touch.id] = {
            'ox': lx,
            'oy': ly,
            'xmot': 0,
            'ymot': 0,
            'travelx' : 0, #How far the blob has traveled total in the x axis
            'travely' : 0, #^
        }
        return True

    def on_touch_move(self, touch):
        # accept only grabbed touch by us
        if touch.grab_current != self:
            return

        # ok, if it's not a kinetic movement,
        # dispatch to children
        if touch.id not in self.touch:
            for w in self.widgets:
                if w.on_touch_move(touch):
                    return True
            return

        # it's a kinetic movement, process it.
        t = self.touch[touch.id]
        t['xmot'] = touch.x - t['ox']
        t['ymot'] = touch.y - t['oy']
        t['ox'] = touch.x
        t['oy'] = touch.y
        t['travelx'] += abs(t['xmot'])
        t['travely'] += abs(t['ymot'])
        self.xoffset += t['xmot'] * self.do_x
        self.yoffset += t['ymot'] * self.do_y

    def on_touch_up(self, touch):
        # accept only grabbed touch by us
        if touch.grab_current != self:
            return

        # it's an up, ungrab us !
        touch.ungrab(self)

        if touch.id not in self.touch:
            for w in self.widgets:
                if w.on_touch_up(touch):
                    return True
            return

        t = self.touch[touch.id]
        self.vx = t['xmot']
        self.vy = t['ymot']

        # check if we can transmit event to children
        if (self.do_x and t['travelx'] > self.trigger_distance) or \
           (self.do_y and t['travely'] > self.trigger_distance):
            return True

        # ok, the trigger distance is enough, we can dispatch event.
        # will not work if children grab the touch in down state :/
        touch.push()
        touch.x, touch.y = self.to_parent(*touch.pos)
        for child in self.children:
            child.dispatch_event('on_touch_down', touch)
            child.dispatch_event('on_touch_up', touch)
        touch.pop()
        return True

    def process_kinetic(self):
        '''Apply kinetic movement to all the items'''
        self.xoffset += self.vx * self.do_x
        self.yoffset += self.vy * self.do_y

        dt = getFrameDt()
        self.vx /= 1 + (self.friction * dt)
        self.vy /= 1 + (self.friction * dt)

    def draw(self):
        # background
        set_color(*self.style.get('bg-color'))
        drawCSSRectangle(pos=self.pos, size=self.size, style=self.style)

        # draw children
        self.stencil_push()
        for w in self.children:
            # internal update of children
            w.update()
            # optimization to draw only viewed children
            if self.do_y and (w.y + w.height < self.y or w.y > self.y + self.height):
                continue
            if self.do_x and (w.x + w.width < self.x or w.x > self.x + self.width):
                continue
            w.on_draw()
        self.stencil_pop()

        # title bar
        if self.titletext is not None:
            set_color(*self.style.get('title-color'))
            drawCSSRectangle(pos=(self.x, self.height + self.y - 40), size=(self.width, 40), prefix='title')
            self.title.draw()

    def on_draw(self):
        self.do_layout()
        self.process_kinetic()
        self.draw()

class MTKineticObject(MTWidget):
    def __init__(self, **kwargs):
        kwargs.setdefault('deletable', True)

        super(MTKineticObject, self).__init__(**kwargs)

        #List of attributes that can be searched
        self.attr_search = ['label']

        self.deletable = kwargs.get('deletable')

        #Delete Button
        self.db = MTButton(label='',
                                      size=(40, 40),
                                      pos=(self.x + self.width-40, self.y + self.height-40),
                                      style={'bg-color':(1, 0, 0, 0)})
        self.db.hide()
        self.db.on_press = self.delete
        self.add_widget(self.db)

        self.xoffset = self.yoffset = 0  #In case the widget has to move itself while still having kinetic movement applied
        self.kx = self.ky = 0  #The position values that the kinetic container edits.  We do this so we can break free and move ourself it necessary

        self.db_alpha = 0
        self.a_show = Animation(self, 'Show Button Alpha', 'db_alpha', .5, 1, 5)
        self.a_hide = Animation(self, 'Hide Button Alpha', 'db_alpha', 0, 1, 5)
        self.a_delete_w = Animation(self, 'Deleting Self W', 'width', 0, 1, 10)
        self.a_delete_h = Animation(self, 'Deleting Self H', 'height', 0, 1, 10)
        self.a_delete_x = Animation(self, 'Deleting Self X', 'xoffset', self.kx + self.width/2, 1, 10)
        self.a_delete_y = Animation(self, 'Deleting Self Y', 'yoffset', self.ky + self.height/2, 1, 10)

        self.free = False #Set to true if you want to break free from the grasp of a kinetic widget

    def show_delete(self):
        self.db.show()
        self.a_show.reset()
        self.a_show.start()

    def hide_delete(self):
        self.a_hide.reset()
        self.a_hide.start()

    def on_animation_complete(self, anim):
        if anim == self.a_hide:
            self.db.hide()
        elif anim == self.a_delete_w:
            '''We don't check Y because then it gets called
            twice and throws an exception because its already
            been deleted, and a try...except... isn't really worth it
            '''
            self.parent.remove_widget(self)

    def update(self):
        if not self.free:
            self.x, self.y = self.kx + self.xoffset, self.ky + self.yoffset
        self.db.pos = (self.x + self.width-40, self.y + self.height-40)
        self.db.style['bg-color'] = (1, 0, 0, self.db_alpha)

    def on_draw(self):
        super(MTKineticObject, self).on_draw()

    def delete(self, touch):
        self.db.hide()  #So it doesn't poke out at the end(we aren't scaling it)
        self.a_delete_x.reset()
        self.a_delete_y.reset()
        self.a_delete_w.reset()
        self.a_delete_h.reset()
        self.a_delete_x.start()
        self.a_delete_y.start()
        self.a_delete_w.start()
        self.a_delete_h.start()

    def on_press(self, touch):
        if self.db.visible and self.db.on_touch_down(touch):
            return True

class MTKineticItem(MTButton, MTKineticObject):
    def on_press(self, touch):
        if self.db.visible and self.db.on_touch_down(touch):
            return True

class MTKineticImage(MTImageButton, MTKineticObject):
    def on_press(self, touch):
        if self.db.visible and self.db.on_touch_down(touch):
            return True

MTWidgetFactory.register('MTKineticObject', MTKineticObject)
MTWidgetFactory.register('MTKineticList', MTKineticList)
MTWidgetFactory.register('MTKineticItem', MTKineticItem)
MTWidgetFactory.register('MTKineticImage', MTKineticImage)
