from pymt import *
import math
import sys

class MTBubbleWidget(MTWidget):
    def __init__(self, parent=None, pos=(0,0), color=(0.6,0.6,0.6,1.0), **kargs):
        self.x, self.y = pos
        self.color  = color
        img         = pyglet.image.load('menu-bubble.png')
        self.image  = pyglet.sprite.Sprite(img)
        assert self.image.width == self.image.height
        MTWidget.__init__(self,parent, **kargs)

        self._icon   = None
        self._iconname = ''

        # prepare animations
        self.anim_length = 10
        self.anim_precision = 1
        self.add_animation('show', 'scale', 1, self.anim_precision,
                           self.anim_length, func=AnimationAlpha.bubble)
        self.add_animation('show', 'opacity', 255, self.anim_precision, self.anim_length)
        self.add_animation('hide', 'scale', 0, self.anim_precision,
                           self.anim_length, func=AnimationAlpha.bubble)
        self.add_animation('hide', 'opacity', 0, self.anim_precision, self.anim_length)
        self.add_animation('show_all', 'scale', 1, self.anim_precision, self.anim_length, func=AnimationAlpha.ramp)
        self.add_animation('show_all', 'opacity', 255, self.anim_precision, self.anim_length)
        self.add_animation('hide_all', 'scale', 0, self.anim_precision, self.anim_length, func=AnimationAlpha.ramp)
        self.add_animation('hide_all', 'opacity', 0, self.anim_precision, self.anim_length)

    def draw(self):
        if not self.visible:
            return
        self.image.x = self.x - self.image.width / 2
        self.image.y = self.y - self.image.height / 2
        self.image.draw()
        if self.icon:
            self.icon.x = self.x - self.icon.width / 2
            self.icon.y = self.y - self.icon.height / 2
            self.icon.draw()

    def collidePoint(self, x, y):
        return Vector.distance(Vector(x, y), Vector(self.x, self.y)) < self.image.width / 2

    def show_all(self):
        MTWidget.show(self)
        self.start_animations('show_all')

    def hide_all(self):
        self.start_animations('hide_all')

    def on_animation_complete(self, anim):
        if anim.label == 'hide_all':
            MTWidget.hide(self)
        elif anim.label == 'hide':
            self.visible = False

    def show(self):
        self.visible = True
        self.opacity = 0
        self.scale = 0
        self.start_animations('show')

    def hide(self):
        self.opacity = 255
        self.scale = 1
        self.start_animations('hide')

    def _set_pos(self, pos):
        self.x, self.y = pos
    def _get_pos(self):
        return (self.x, self.y)
    pos = property(_get_pos, _set_pos)

    def _set_scale(self, scale):
        self.image.scale = scale
        if self.icon:
            self.icon.scale = scale
    def _get_scale(self):
        return self.image.scale
    scale = property(_get_scale, _set_scale)

    def _set_opacity(self, opacity):
        self.image.opacity = opacity
        if self.icon:
            self.icon.opacity = opacity
    def _get_opacity(self):
        return self.image.opacity
    opacity = property(_get_opacity, _set_opacity)

    def _set_width(self, width):
        self.image.width = width
    def _get_width(self):
        return self.image.width
    width = property(_get_width, _set_width)

    def _set_icon(self, icon):
        if icon is None:
            self._icon = None
            self._iconname = ''
        else:
            self._iconname = icon
            img = pyglet.image.load('icons/%s.png' % icon)
            self._icon = pyglet.sprite.Sprite(img)
    def _get_icon(self):
        return self._icon
    icon = property(_get_icon, _set_icon)

class MTMenuNode(MTBubbleWidget):
    STATE_ = 1

    def __init__(self, parent=None, pos=(0,0), size=30, color=(1,1,1,1)):
        MTBubbleWidget.__init__(self,
            parent=parent, pos=pos, color=color)
        self.pos = pos
        self.visible_children   = False
        self.move_track         = None
        self.move_action        = False
        self.action             = None
        self.label_obj          = Label(font_size=10, )
        self.label_obj.anchor_x = 'center'
        self.label_obj.anchor_y = 'center'
        self.label              = 'No label'

    def add_widget(self, child):
        child.visible = False
        MTBubbleWidget.add_widget(self, child)

    def draw(self):
        if self.visible:
            MTBubbleWidget.draw(self)
            self.label_obj.x, self.label_obj.y = self.x, self.y - self.width / 2
            #self.label_obj.draw()
        for c in self.children:
            if c.visible:
                c.dispatch_event('on_draw')

    def on_touch_down(self, touches, touchID, x, y):
        if self.visible and self.collidePoint(x, y) and self.move_track is None:
            self.move_track = touchID
            self.move_action = False

    def on_touch_move(self, touches, touchID, x, y):
        if self.move_track != touchID:
            return
        if self.pos == (x, y):
            return
        self.pos = (x, y)
        self.original_pos = self.pos
        self.parent_pos((x, y))
        self.move_action = True

    def on_touch_up(self, touches, touchID, x, y):
        if self.move_track == touchID:
            self.move_track = None
            if self.move_action:
                return

        if self.visible_children:
            for c in self.children:
                if c.on_touch_up(touches, touchID, x, y):
                    return True

        if self.visible and self.collidePoint(x, y):
            if self.action:
                if globals()[self.action](self) != False:
                    self.close_all()
            elif self.visible_children:
                self.parent_unselect()
                self.close_children()
            else:
                self.parent_select()
                self.open_children()
            return True

    def parent_pos(self, pos):
        if isinstance(self.parent, MTMenuNode):
            self.parent_pos(pos)
        else:
            self.original_pos = pos
            self.pos = pos

    def close_all(self):
        if isinstance(self.parent, MTMenuNode):
            self.parent.close_all()
        else:
            self.close_children()

    def parent_select(self):
        self.original_pos = self.pos
        if isinstance(self.parent, MTMenuNode):
            self.pos = self.parent.pos
            self.parent.show_only_child(self)

    def parent_unselect(self):
        self.pos = self.original_pos
        if isinstance(self.parent, MTMenuNode):
            self.parent.show_all_childs()

    def show_only_child(self, child):
        for c in self.children:
            if c != child:
                c.hide()

    def show_all_childs(self):
        for c in self.children:
            c.show()

    def update_children_pos(self):
        max = len(self.children)
        i = 0
        start = math.pi / 2 # Orientation
        for c in self.children:
            x = self.x + math.sin(start + i * math.pi * 2 / max) * self.width
            y = self.y + math.cos(start + i * math.pi * 2 / max) * self.width
            c.pos = (x, y)
            i += 1

    def close_children(self):
        self.visible_children = False
        for c in self.children:
            c.hide(with_childs=True)

    def open_children(self):
        self.update_children_pos()
        self.visible_children = True
        for c in self.children:
            c.show()

    def hide(self, with_childs=False):
        MTBubbleWidget.hide(self)
        if with_childs:
            self.close_children()

    def _set_pos(self, pos):
        self.x, self.y = pos
        self.update_children_pos()
    def _get_pos(self):
        return (self.x, self.y)
    pos = property(_get_pos, _set_pos)

    def _get_label(self):
        return self._label
    def _set_label(self, text):
        self._label = str(text)
        self.label_obj.text = self.label
    label = property(_get_label, _set_label)


xmlmenu = """<?xml version="1.0"?>
<MTMenuNode label="'Home'" icon="'home'" pos="(200,200)">
    <MTMenuNode label="'Games'" icon="'applications-games'">
        <MTMenuNode label="'ColorPicker'" icon="'gtk-color-picker'"
        action="'menu_action_game_colorpicker'"/>
    </MTMenuNode>
    <MTMenuNode label="'Multimedia'" icon="'applications-multimedia'"/>
    <MTMenuNode label="'Settings'" icon="'preferences-desktop'">
        <MTMenuNode label="'Sound volume'" icon="'audio-volume-high'"
        action="'menu_action_volume'"/>
    </MTMenuNode>
    <MTMenuNode label="'Quit'" icon="'application-exit'"
    action="'menu_action_quit'"/>
</MTMenuNode>
"""

def menu_action_quit(node):
    sys.exit(0)

def menu_action_volume(node):
    if node._iconname == 'audio-volume-high':
        node.icon = 'audio-volume-muted'
    else:
        node.icon = 'audio-volume-high'
    return False

def menu_action_game_colorpicker(node):
    pass

if __name__ == '__main__':

    MTWidgetFactory.register('MTMenuNode', MTMenuNode)

    w = MTWindow(color=(0.16,0.223,0.313,1.0))
    #w.set_fullscreen()
    menu = XMLWidget(xml=xmlmenu)
    w.add_widget(menu)
    w.add_widget(MTDisplay())
    runTouchApp()

