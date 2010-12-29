'''
Kinetic List: Custom list with kinetic interaction
'''

__all__ = (
    'MTKineticList', 'MTKineticObject',
    'MTKineticItem', 'MTKineticImage'
)

import pymt
from pymt.config import pymt_config
from pymt.utils import boundary
from pymt.graphx import set_color, drawRectangle, drawCSSRectangle
from pymt.base import getFrameDt
from pymt.utils import SafeList
from pymt.ui.widgets.stencilcontainer import MTStencilContainer
from pymt.ui.widgets.widget import MTWidget
from pymt.ui.widgets.button import MTButton, MTToggleButton, MTImageButton
from pymt.ui.animation import Animation
from pymt.core.text import Label

class MTKineticList(MTStencilContainer):
    '''This is a kinetic container widget, that allows you to make
    a kinetic list scrolling in either direction.

    Some parameters are customizable in global configuration ::

        [widgets]
        list_friction = 10
        list_trigger_distance = 5

    :Parameters:
        `align` : string, default to 'center'
            Alignement of widget inside the row (or col). Can be
            one of 'center', 'left', 'right'
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
        `trigger_distance` : int, default to 3
            Maximum trigger distance to dispatch event on children
            (this mean if you move too much, trigger will not happen.)

    :Styles:
        `bg-color` : color
             Background color of the widget
        `scrollbar-size` : int
            Size of scrollbar in pixel (use 0 to disable it.)
        `scrollbar-color` : color
            Color of scrollbar
        `scrollbar-margin` : int int int int
            Margin top/right/bottom/left of scrollbar (left are not used.)

    :Events:
        `on_delete` (child)
            Fired when an item gets deleted.
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('padding_x', 4)
        kwargs.setdefault('padding_y', 4)
        kwargs.setdefault('w_limit', 1)
        kwargs.setdefault('h_limit', 0)
        kwargs.setdefault('do_x', False)
        kwargs.setdefault('do_y', True)
        kwargs.setdefault('title', 'No title')
        kwargs.setdefault('deletable', True)
        kwargs.setdefault('searchable', True)
        kwargs.setdefault('align', 'center')

        super(MTKineticList, self).__init__(**kwargs)

        self.register_event_type('on_delete')

        self._a_sinput_out  = None
        self._a_sinput_in   = None
        self.title          = Label('')
        self.sb             = None
        self.sinput         = None

        self.do_x       = kwargs.get('do_x')
        self.do_y       = kwargs.get('do_y')
        self.titletext  = kwargs.get('title')
        self.deletable  = kwargs.get('deletable')
        self.searchable = kwargs.get('searchable')
        self.padding_x  = kwargs.get('padding_x')
        self.padding_y  = kwargs.get('padding_y')
        self.w_limit    = kwargs.get('w_limit')
        self.h_limit    = kwargs.get('h_limit')
        self.align      = kwargs.get('align')
        self.trigger_distance = kwargs.get('trigger_distance',
            pymt_config.getint('widgets', 'list_trigger_distance'))
        self.friction = kwargs.get('friction',
            pymt_config.getint('widgets', 'list_friction'))

        if self.w_limit and self.h_limit:
            raise Exception('You cannot limit both axes')
        elif not(self.w_limit or self.h_limit):
            raise Exception('You must limit at least one axis')

        # How far to offset tself.deletable and he axes(used for scrolling/panning)
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
        self._last_content_size = 0
        self._scrollbar_index = 0
        self._scrollbar_size = 0

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
                label=self.titletext)
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
            self.widgets.insert(0, self.sinput)

            # Animations to hide and show the search text input box
            self._a_sinput_in = Animation(y=self.y + self.height - 40 -
                                         self.sinput.size[1], duration=0.5,
                                         f='ease_out_cubic')
            self._a_sinput_out = Animation(y=self.y + self.height -
                                          self.sinput.size[1], duration=0.5,
                                         f='ease_out_cubic')

    def on_delete(self, child):
        pass

    def clear(self):
        self.children = SafeList()
        self.pchildren = SafeList()
        self.xoffset = self.yoffset = 0

    def add_widget(self, widget, **kwargs):
        super(MTKineticList, self).add_widget(widget, **kwargs)
        self.pchildren.append(widget)

    def remove_widget(self, widget):
        super(MTKineticList, self).remove_widget(widget)
        if widget in self.pchildren:
            self.pchildren.remove(widget)
        self.dispatch_event('on_delete', widget)

    def toggle_delete(self, touch):
        '''Toggles the delete buttons on items
        Attached to the on_press handler of the delete button(self.db)
        '''
        if self.db.state == 'down':
            for child in self.children[:]:
                child.show_delete()
        else:
            for child in self.children[:]:
                child.hide_delete()

    def toggle_search(self, touch):
        '''Toggles the search area
        Attached to the on_press handler of self.sb(the green search button)
        '''
        if self.sb.state == 'down':
            self._a_sinput_in.animate(self.sinput)
        else:
            try:
                self.sinput.hide_keyboard()
            except:
                # There isn't a keyboard, so it throws a ValueError
                pass
            self.sinput.label = ''
            self._a_sinput_out.animate(self.sinput)

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
        result = self.filter(pattern, attr)
        self.children.clear()
        for item in result:
            self.children.append(item)

    def endsearch(self):
        '''Resets the children set to the full set'''
        self.children.clear()
        for item in self.pchildren:
            self.children.append(item)

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
                total += (item.height + self.padding_y)

        return total

    def goto_head(self):
        if not self.h_limit:
            self.yoffset = -self._get_total_width(self.children, 'height')/self.w_limit + self.size[1] - 100
        else:
            self.xoffset = self._get_total_width(self.children, 'width')/self.h_limit + self.size[0] - 100

    def do_layout(self):
        '''Apply layout to all the items'''

        t = index = 0

        # adapt value for direction
        w2          = self.width / 2.
        h2          = self.height / 2.
        inverse     = 0
        limit       = self.w_limit
        width_attr  = 'width'
        height_attr = 'height'
        xoffset     = self.xoffset
        sx          = self.x
        y           = self.y + self.yoffset
        padding_x   = self.padding_x
        padding_y   = self.padding_y

        # inverse
        if not self.w_limit:
            inverse     = 1
            limit       = self.h_limit
            width_attr  = 'height'
            height_attr = 'width'
            xoffset     = self.yoffset
            y           = self.x + self.xoffset
            padding_x   = self.padding_y
            padding_y   = self.padding_x
            w2, h2      = h2, w2
            sx          = self.y

        # calculate size of actual content
        size = 0
        for i in xrange(len(self.children)):
            if i % limit == 0:
                maxrange = min(i + limit, len(self.children))
                childrens = [self.children[z] for z in range(i, maxrange)]
                h = max((c.__getattribute__(height_attr) for c in childrens))
                size += h + padding_y
        self._last_content_size = size

        # add little padding for good looking.
        y += padding_y
        ny = y

        # recalculate position for each children
        for child in self.children[:]:

            # each row, calculate the height, advance y and reset x
            if index % limit == 0:

                # set y axis to the previous calculated position
                y = ny

                # get children in the row
                maxrange = min(t + limit, len(self.children))
                childrens = [self.children[z] for z in range(t, maxrange)]

                # take the largest height in the current row
                if len(childrens):
                    h = max((c.__getattribute__(height_attr) for c in childrens))
                else:
                    h = 0

                # prepare the y axis for next loop
                ny = y + h + padding_y

                # reset x for this row.
                if self.align == 'center':
                    x = sx + w2 + xoffset - \
                        (self._get_total_width(childrens, width_attr) / 2.)
                elif self.align == 'left':
                    x = 0
                elif self.align == 'right':
                    x = getattr(self, width_attr) - getattr(child, width_attr) - xoffset
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
        for w in reversed(self.widgets[:]):
            if w.on_touch_down(touch):
                return True

        # initiate kinetic movement.
        self.vx = self.vy = 0
        self.touch[touch.id] = {
            'ox': touch.x,
            'oy': touch.y,
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
            for w in reversed(self.widgets[:]):
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
        self.ensure_bounding()

    def on_touch_up(self, touch):
        # accept only grabbed touch by us
        if touch.grab_current != self:
            return

        # it's an up, ungrab us !
        touch.ungrab(self)

        if touch.id not in self.touch:
            for w in reversed(self.widgets[:]):
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
        for child in reversed(self.children[:]):
            must_break = child.dispatch_event('on_touch_down', touch)
            old_grab_current = touch.grab_current
            touch.grab_current = child
            child.dispatch_event('on_touch_up', touch)
            touch.grab_current = old_grab_current
            if must_break:
                break
        return True

    def ensure_bounding(self):
        size = float(self._last_content_size)
        if size <= 0:
            return

        self._scrollbar_size = 1
        self._scrollbar_index = 0

        if self.do_y:
            if size < self.height:
                self.yoffset = 0
            else:
                self.yoffset = boundary(self.yoffset, -size + self.height, 0)
                self._scrollbar_size = self.height / size
                self._scrollbar_index = -self.yoffset / size
        elif self.do_x:
            if size < self.width:
                self.xoffset = 0
            else:
                self.xoffset = boundary(self.xoffset, -size + self.width, 0)
                self._scrollbar_size = self.width / size
                self._scrollbar_index = -self.xoffset / size

    def process_kinetic(self):
        '''Apply kinetic movement to all the items'''
        dt = getFrameDt()
        self.vx /= 1 + (self.friction * dt)
        self.vy /= 1 + (self.friction * dt)

        self.xoffset += self.vx * self.do_x
        self.yoffset += self.vy * self.do_y

        self.ensure_bounding()

    def draw(self):
        # background
        set_color(*self.style.get('bg-color'))
        drawCSSRectangle(pos=self.pos, size=self.size, style=self.style)

        # draw children
        self.stencil_push()
        for w in self.children[:]:
            # internal update of children
            w.update()
            # optimization to draw only viewed children
            if self.do_y and (w.y + w.height < self.y or w.y > self.y + self.height):
                continue
            if self.do_x and (w.x + w.width < self.x or w.x > self.x + self.width):
                continue
            w.on_draw()
        self.stencil_pop()

        # draw widgets
        for w in self.widgets:
            w.dispatch_event('on_draw')
        # title bar
        if self.titletext is not None:
            set_color(*self.style.get('title-color'))
            w = 0
            if self.searchable:
                x = 80
                w += 80
            else:
                x = 0
            if self.deletable:
                w += 80
            drawCSSRectangle(pos=(self.x + x, self.height + self.y - 40),
                             size=(self.width - w, 40), prefix='title',
                             style=self.style)
            self.title.x = self.width/2 + self.x
            self.title.y = self.height - 20 + self.y
            self.title.draw()


        # scrollbar
        sb_size = self.style.get('scrollbar-size')
        if sb_size > 0:
            mtop, mright, mbottom, mleft = self.style.get('scrollbar-margin')
            if self.do_y:
                pos = [self.x + self.width - mright - sb_size, self.y + mbottom]
                size = [sb_size, self.height - mbottom - mtop]
                pos[1] += size[1] * self._scrollbar_index
                size[1] = size[1] * self._scrollbar_size
            elif self.do_x:
                pos = [self.x + mleft, self.y + self.height - mtop - sb_size]
                size = [self.width - mleft - mright, sb_size]
                pos[0] += size[0] * self._scrollbar_index
                size[0] = size[0] * self._scrollbar_size
            set_color(*self.style.get('scrollbar-color'))
            drawRectangle(pos=pos, size=size)

    def on_draw(self):
        if not self.visible:
            return
        self.do_layout()
        self.process_kinetic()
        self.draw()


class MTKineticObject(MTWidget):
    def __init__(self, **kwargs):
        '''Kinetic object, the base object for every child in kineticlist.

        :Parameters:
            `deletable`: bool, default to True
                Indicate if object can be deleted or not
        '''
        kwargs.setdefault('deletable', True)
        super(MTKineticObject, self).__init__(**kwargs)
        self.deletable = kwargs.get('deletable')
        self.register_event_type('on_animation_complete')
        self.push_handlers(on_animation_complete=self.on_animation_complete)

        # List of attributes that can be searched
        self.attr_search = ['label']

        # In case the widget has to move itself
        # while still having kinetic movement applied
        self.xoffset = self.yoffset = 0

        # The position values that the kinetic container edits.
        # We do this so we can break free and move ourself it necessary
        self.kx = self.ky = 0

        self.db_alpha = 0.0

        # Set to true if you want to break free from
        # the grasp of a kinetic widget
        self.free = False

        # Delete Button
        if self.deletable:
            self.db = MTButton(label='',
                size=(40, 40),
                pos=(self.x + self.width-40, self.y + self.height-40),
                style={'bg-color':(1, 0, 0, 0)}, visible=False)
            self.db.push_handlers(on_press=self._delete_callback)
            self.add_widget(self.db)

            self.a_delete = Animation(width=0, height=0,
                                      xoffset=self.kx + self.width/2,
                                      yoffset=self.ky + self.height/2,
                                      duration=0.5,
                                      f='ease_in_cubic')

        self.a_show = Animation(db_alpha=.5, duration=0.25)
        self.a_hide = Animation(db_alpha=0.0, duration=0.25)

    def show_delete(self):
        if not self.deletable:
            return
        self.db.show()
        self.a_show.animate(self)

    def hide_delete(self):
        if not self.deletable:
            return
        self.a_hide.animate(self)

    def on_animation_complete(self, anim):
        if anim == self.a_hide:
            self.db.hide()
        elif anim == self.a_delete:
            try:
                self.parent.remove_widget(self)
            except:
                pass

    def update(self):
        if not self.free:
            self.pos = self.kx + self.xoffset, self.ky + self.yoffset
        if self.deletable:
            self.db.pos = (self.x + self.width-40, self.y + self.height-40)
            self.db.style['bg-color'] = (1, 0, 0, self.db_alpha)

    def on_press(self, touch):
        if self.db.visible and self.db.on_touch_down(touch):
            return True

    def _delete_callback(self, touch):
        # So it doesn't poke out at the end(we aren't scaling it)
        self.db.hide()
        self.a_delete.animate(self)


class MTKineticItem(MTButton, MTKineticObject):
    '''The MTKineticItem is a MTKineticObject ready to be included in a MTKineticList.
    MTKineticItem have the behavior of the MTButton.

    By default, on_press event is not fired only if the button is deletable and
    visible.
    '''
    def on_press(self, touch):
        if self.deletable and self.db.visible and self.db.on_touch_down(touch):
            return True


class MTKineticImage(MTImageButton, MTKineticObject):
    '''The MTKineticImage is a MTKineticObject ready to be included in a MTKineticList.
    MTKineticImage have the behavior of the MTImageButton.

    By default, on_press event is not fired only if the button is deletable and
    visible.
    '''
    def on_press(self, touch):
        if self.deletable and self.db.visible and self.db.on_touch_down(touch):
            return True

