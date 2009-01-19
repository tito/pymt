from pymt import *
import math
import sys
import subprocess

p = MTPlugins(plugin_paths=['../'])
p.search_plugins()

class MTBubbleWidget(MTWidget):
    def __init__(self, parent=None, pos=(0,0), color=(0.6,0.6,0.6,1.0), **kargs):
        self.x, self.y = pos
        self.color  = color
        MTWidget.__init__(self,parent, **kargs)

        self._scale  = 1
        self._icon   = None
        self._iconname = ''
        self._opacity = 0
        self.radius = 45

        self.label_obj          = Label(font_name='Lucida', font_size=10, color=(10,10,10,150))
        self.label_obj.anchor_x = 'center'
        self.label_obj.anchor_y = 'center'
        self.label              = 'No label'

        # prepare animations
        self.anim_length = 10
        self.anim_precision = 1
        self.add_animation('show', 'scale', 1, self.anim_precision,
                           self.anim_length, func=AnimationAlpha.bubble)
        self.add_animation('show', 'opacity', 255, self.anim_precision, self.anim_length)
        self.add_animation('hide', 'scale', 0, self.anim_precision,
                           self.anim_length, func=AnimationAlpha.bubble)
        self.add_animation('hide', 'opacity', 0, self.anim_precision, self.anim_length)

    def draw(self):
        if not self.visible:
            return
        glColor4f(.1, .1, .1, self.opacity / 255)
        drawCircle((self.x+1, self.y-1), self.radius * self.scale)
        glColor4d(1, 1, 1, self.opacity / 255)
        drawCircle((self.x, self.y), self.radius * self.scale)
        if self.icon:
            self.icon.x = self.x - self.icon.width / 2
            self.icon.y = self.y - self.icon.height / 2
            self.icon.draw()
        self.label_obj.x, self.label_obj.y = self.x, self.y - self.radius
        drawRoundedRectangle(
            (self.label_obj.x - (self.label_obj.content_width+5) / 2+1,
             self.label_obj.y - self.label_obj.content_height / 2-3),
            (self.label_obj.content_width+5, self.label_obj.content_height),
            color=(.1,.1,.1,self._opacity))
        drawRoundedRectangle(
            (self.label_obj.x - (self.label_obj.content_width+5) / 2,
             self.label_obj.y - self.label_obj.content_height / 2-2),
            (self.label_obj.content_width+5, self.label_obj.content_height),
            color=(1,1,1,self._opacity))
        self.label_obj.draw()

    def collide_point(self, x, y):
        return Vector.distance(Vector(x, y), Vector(self.x, self.y)) < self.radius

    def on_animation_complete(self, anim):
        if anim.label == 'hide':
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
        self._scale = scale
        if self.icon:
            self.icon.scale = scale
    def _get_scale(self):
        return self._scale
    scale = property(_get_scale, _set_scale)

    def _set_opacity(self, opacity):
        self._opacity = opacity
        if self.icon:
            self.icon.opacity = opacity
    def _get_opacity(self):
        return self._opacity
    opacity = property(_get_opacity, _set_opacity)

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

    def __init__(self, parent=None, pos=(0,0), size=30, color=(1,1,1,1)):
        MTBubbleWidget.__init__(self,
            parent=parent, pos=pos, color=color)
        self.pos = pos
        self.visible_children   = False
        self.move_track         = None
        self.move_action        = False
        self.action             = None
        self.margin             = 15

    def add_widget(self, child):
        child.visible = False
        MTBubbleWidget.add_widget(self, child)

    def draw(self):
        if self.visible:
            MTBubbleWidget.draw(self)
        for c in self.children:
            if c.visible:
                c.dispatch_event('on_draw')

    def on_touch_down(self, touches, touchID, x, y):
        if self.visible and self.collide_point(x, y) and self.move_track is None:
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

        if self.visible and self.collide_point(x, y):
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
            x = self.x + math.sin(start + i * math.pi * 2 / max) * \
                    (self.radius * 2 + self.margin)
            y = self.y + math.cos(start + i * math.pi * 2 / max) * \
                    (self.radius * 2 + self.margin)
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


class MTInnerWindowContainer(MTRectangularWidget):
    def __init__(self, **kargs):
        MTRectangularWidget.__init__(self, **kargs)
        self.m_viewport = (GLint * 4)()

    def on_draw(self):
        if not self.visible:
            return

        # save viewport
        glGetIntegerv(GL_VIEWPORT, self.m_viewport)

        # save matrix
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()

        # initialize viewport for children
        glViewport(self.x, self.y, self.width, self.height)

        # initialize matrix for children
        glMatrixMode(GL_PROJECTION)
        glOrtho(0, self.width, 0, self.height, -1, 1)
        #        glTranslatef(self.pos[0], self.pos[1], 0)

        # draw children
        for c in self.children:
            c.dispatch_event('on_draw')

        # restore main matrix
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

        # restore main viewport
        glViewport(*self.m_viewport)

    def transpose_xy(self, x, y):
        #x = (x - self.x) * self.m_viewport[2] / self.width
        #y = (y - self.y) * self.m_viewport[3] / self.height
        x = (x - self.x)
        y = (y - self.y)
        return (x, y)

    def on_touch_down(self, touches, touchID, x, y):
        x, y = self.to_local(x, y)
        return MTRectangularWidget.on_touch_down(self,
            touches, touchID, x, y)

    def on_touch_move(self, touches, touchID, x, y):
        x, y = self.to_local(x, y)
        return MTRectangularWidget.on_touch_move(self,
            touches, touchID, x, y)

    def on_touch_up(self, touches, touchID, x, y):
        x, y = self.to_local(x, y)
        return MTRectangularWidget.on_touch_up(self,
            touches, touchID, x, y)

    def get_size(self):
        return self.size


class MTInnerWindowOld(MTDragableWidget):
    def __init__(self, parent=None, pos=(0,0), size=(100,100),
                 title='Plugin window', **kargs):
        MTDragableWidget.__init__(self, parent=parent, pos=pos, size=size, **kargs)
        self.container = MTInnerWindowContainer()
        MTDragableWidget.add_widget(self, self.container)

        # set margins
        self.style_title_height = 24
        self.style_border_width = 2

        # load wm icons
        self.is_fullscreen = False
        self.wm_close = MTImageButton('wm/close.png')
        self.wm_fullscreen = MTImageButton('wm/fullscreen.png')
        self.wm_window = MTImageButton('wm/window.png')

        # force event propagation
        self.pos                = pos
        self.size               = size
        self.label_obj          = Label(font_name='Monospace', font_size=10,
                                        color=(255,255,255,255))
        self.label_obj.text     = title


    def add_widget(self, w):
        self.container.add_widget(w)

    def remove_widget(self, w):
        self.container.remove_widget(w)

    def close(self):
        self.parent.remove_widget(self)

    def set_fullscreen(self, fullscreen=True):
        if fullscreen:
            self.is_fullscreen = True
            self.initial_size = self.size
            self.initial_pos = self.pos

            w = self
            while not isinstance(w, MTWindow):
                w = w.parent
            self.pos = (0, 0)
            self.size = (w.width, w.height)
        else:
            self.is_fullscreen = False
            self.size = self.initial_size
            self.pos = self.initial_pos

    def draw(self):
        self.label_obj.x, self.label_obj.y = (self.pos[0] + 10, self.pos[1] +
                                              self.height -
                                              self.label_obj.content_height)
        drawRoundedRectangle(self.pos, self.size, color=(0.466, 0.501, 0.549, .8))
        self.label_obj.draw()

    def draw_icons(self):
        self.wm_close.draw()
        if self.is_fullscreen:
            self.wm_window.draw()
        else:
            self.wm_fullscreen.draw()

    def on_draw(self):
        self.draw()
        for w in self.children:
            w.dispatch_event('on_draw')
        self.draw_icons()

    def update_icons_pos(self):
        self.wm_close.x = self.pos[0] + self.width - self.wm_close.width + 10
        self.wm_close.y = self.pos[1] + self.height - self.wm_close.height / 2 - self.style_title_height / 2
        self.wm_fullscreen.x = self.wm_close.x - self.wm_fullscreen.width
        self.wm_fullscreen.y = self.wm_close.y
        self.wm_window.x = self.wm_close.x - self.wm_fullscreen.width
        self.wm_window.y = self.wm_close.y

    def on_resize(self, w, h):
        self.container.size = (w - 2 * self.style_border_width, h - self.style_title_height)
        self.update_icons_pos()
        self.container.dispatch_event('on_resize', w, h)

    def on_move(self, x, y):
        self.container.pos = (x + self.style_border_width, y +
                              self.style_border_width)
        self.update_icons_pos()

    def on_touch_down(self, touches, touchID, x, y):
        if self.container.collide_point(x, y):
            self.container.dispatch_event('on_touch_down', touches, touchID, x, y)
        else:
            self.bring_to_front()
            MTDragableWidget.on_touch_down(self, touches, touchID, x, y)
        return True

    def on_touch_move(self, touches, touchID, x, y):
        if MTDragableWidget.on_touch_move(self, touches, touchID, x, y):
            return True
        if self.container.collide_point(x, y):
            self.container.dispatch_event('on_touch_move', touches, touchID, x, y)
        return True

    def on_touch_up(self, touches, touchID, x, y):
        if self.wm_close.collide_point(x, y):
            self.close()
            return True

        if self.is_fullscreen:
            if self.wm_window.collide_point(x, y):
                self.set_fullscreen(False)
                return True
        else:
            if self.wm_fullscreen.collide_point(x, y):
                self.set_fullscreen(True)
                return True

        if MTDragableWidget.on_touch_up(self, touches, touchID, x, y):
            return True
        if self.container.collide_point(x, y):
            self.container.dispatch_event('on_touch_up', touches, touchID, x, y)
        return True


class MTInnerWindow(MTScatterWidget):
    def __init__(self, parent=None, pos=(0,0), size=(100,100),title='Plugin window', **kargs):
        MTScatterWidget.__init__(self, pos=pos, size=size, **kargs)
        self.padding = 15
        self.container = MTRectangularWidget(parent=self,
            pos=(self.padding,self.padding),size=(size[0]-self.padding*2,size[1]-self.padding*2))
        self.fbo = Fbo(size=(size[0]-self.padding*2,size[1]-self.padding*2))
        self.needs_fbo_resize = False


    def on_draw(self):
        self.fbo.bind()
        glClearColor(1,0,0,1)
        glClear(GL_COLOR_BUFFER_BIT)
        glPushMatrix()
        glTranslated(-self.padding, -self.padding, 0)
        self.container.on_draw()
        glPopMatrix()
        self.fbo.release()

        MTScatterWidget.on_draw(self)

    def draw(self):
        glPushMatrix()
        glScaled(self.width*0.01, self.height*0.01, 1.0)
        glColor3d(0.7,0.7,0.9)
        drawRoundedRectangle(pos=(0,0), size=(100,100))
        glPopMatrix()

        glPushMatrix()
        glTranslated(self.padding, self.padding, 0)
        glScaled(self.width-self.padding*2, self.height-self.padding*2, 1.0)
        drawTexturedRectangle(self.fbo.texture)
        glPopMatrix()

    def transposeTouch(self, x,y):
        lx,ly = self.to_local(x,y)
        lx = (lx)*self.zoom
        ly = (ly)*self.zoom
        return (lx,ly)


    def on_touch_down(self, touches, touchID, x, y):
        lx,ly = self.transposeTouch(x,y)
        if self.container.collide_point(lx, ly):
            self.container.dispatch_event('on_touch_down', touches, touchID, lx, ly)
        else:
            self.bring_to_front()
            MTScatterWidget.on_touch_down(self, touches, touchID, x, y)
        return True

    def on_touch_move(self, touches, touchID, x, y):
        lx,ly = self.transposeTouch(x,y)
        self.moveData = (lx,ly)
        if MTScatterWidget.on_touch_move(self, touches, touchID, x, y):
            return True
        elif self.container.collide_point(lx, ly):
            self.container.dispatch_event('on_touch_move', touches, touchID, lx, ly)
        return True

    def on_touch_up(self, touches, touchID, x, y):
        lx,ly = self.transposeTouch(x,y)
        if self.container.collide_point(lx, ly):
            if self.container.dispatch_event('on_touch_up', touches, touchID, lx, ly):
                return True

        MTScatterWidget.on_touch_up(self, touches, touchID, x, y)

        w,h = int(self.width*self.zoom)-self.padding*2, int(self.height*self.zoom)-self.padding*2
        self.container.size = (w,h)
        del self.fbo
        print 'Recreate FBO !'
        self.fbo = Fbo(size=(w,h))
        return True





xmlmenu = """<?xml version="1.0"?>
<MTMenuNode label="'Home'" icon="'home'" pos="(200,200)">

    <MTMenuNode label="'Games'" icon="'applications-games'">

        <MTMenuNode label="'Color Picker'" icon="'gtk-color-picker'"
        action="'menu_action_game_paint'"/>

        <MTMenuNode label="'Particles'" icon="'gtk-color-picker'"
        action="'menu_action_game_particles'"/>

        <MTMenuNode label="'Pictures'" icon="'images'"
        action="'menu_action_game_pictures'"/>

        <MTMenuNode label="'Untangle'" icon="'images'"
        action="'menu_action_game_untangle'"/>



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

def launch_plugin(node, plugin_name):
    global p
    plugin = p.get_plugin(plugin_name)
    info = p.get_infos(plugin)

    w = node
    while not isinstance(w, MTWindow):
        w = w.parent

    mw = MTInnerWindow(pos=(10,10), size=(300,320), title=info['title'])
    w.add_widget(mw)

    p.activate(plugin, mw.container)

def menu_action_quit(node):
    sys.exit(0)

def menu_action_volume(node):
    if node._iconname == 'audio-volume-high':
        node.icon = 'audio-volume-muted'
    else:
        node.icon = 'audio-volume-high'
    return False

def menu_action_game_paint(node):
    launch_plugin(node, 'paint')

def menu_action_game_particles(node):
    launch_plugin(node, 'particles')

def menu_action_game_pictures(node):
    launch_plugin(node, 'pictures')

def menu_action_game_untangle(node):
    launch_plugin(node, 'untangle')


if __name__ == '__main__':

    MTWidgetFactory.register('MTMenuNode', MTMenuNode)

    w = MTWindow(color=(0.16,0.223,0.313,1.0))
    w.set_fullscreen()
    menu = XMLWidget(xml=xmlmenu)
    w.add_widget(menu)
    w.add_widget(MTDisplay())
    runTouchApp()

