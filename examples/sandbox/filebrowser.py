from __future__ import with_statement
import os
from pymt import *
from pyglet.gl import *
import os, sys, random
from pyglet.text import Label

icons_filetype_dir = os.path.join(pymt_data_dir, 'icons', 'filetype')

class KineticBrowseLayout(MTKineticList):
    def __init__(self, **kwargs):
        super(KineticBrowseLayout, self).__init__(**kwargs)

    def draw(self):
        set_color(*self.style['bg-color'])
        drawRectangle(self.pos, self.size)  #background
        super(MTKineticList, self).on_draw()
        for w in self.widgets:
            w.on_draw()

class MTFileEntry(MTButton, MTKineticObject):
    def __init__(self, **kwargs):
        kwargs.setdefault('scale', 1.0)
        super(MTFileEntry, self).__init__(**kwargs)
        self.filename   = kwargs.get('filename')
        self.browser    = kwargs.get('browser')
        self.label_txt = kwargs.get('label')
        self.type_image = None
        if os.path.isdir(self.filename):
            self.type_image = os.path.join(icons_filetype_dir, 'folder.png')
        else:
            ext = self.label_txt.split('.')[-1]
            if ext in ['jpg', 'jpeg']:
                self.type_image = os.path.join(icons_filetype_dir, 'image-jpeg.png')
            elif ext in ['svg']:
                self.type_image = os.path.join(icons_filetype_dir, 'image-svg.png')
            elif ext in ['png']:
                self.type_image = os.path.join(icons_filetype_dir, 'image-png.png')
            elif ext in ['bmp']:
                self.type_image = os.path.join(icons_filetype_dir, 'image-bmp.png')
            elif ext in ['gif']:
                self.type_image = os.path.join(icons_filetype_dir, 'image-gif.png')
            elif ext in ['mpg', 'mpeg', 'avi', 'mkv', 'flv']:
                self.type_image = os.path.join(icons_filetype_dir, 'video.png')
            else:
                self.type_image = os.path.join(icons_filetype_dir, 'unknown.png')
        self.size           = (80, 80)
        img            = pyglet.image.load(self.type_image)
        self.image     = pyglet.sprite.Sprite(img)
        self.image.x        = self.x
        self.image.y        = self.y
        self.scale          = kwargs.get('scale')
        self.image.scale    = self.scale
        self.labelWX = MTLabel(label=str(self.label_txt)[:10],anchor_x="center",anchor_y="center",halign="center")
        self.add_widget(self.labelWX)
        self.selected = False

    def draw(self):
        if self.selected:
            set_color(1.0,0.39,0.0)
            drawCSSRectangle(size=self.size,style={'border-radius': 8,'border-radius-precision': .1},pos=self.pos)
        else:
            set_color(0,0,0,0)
            drawCSSRectangle(size=self.size,style={'border-radius': 8,'border-radius-precision': .1},pos=self.pos)
        self.image.x        = self.x+int(self.image.width/2)-5
        self.image.y        = self.y+int(self.image.height/2)-5
        self.image.scale    = self.scale
        self.image.draw()
        self.labelWX.pos = (int(self.x+35),int(self.y+10))

    def on_press(self, touch):
        if not self.selected:
            if not os.path.isdir(self.filename):
                self.selected = True
                self.parent.parent.add_to_list(self.filename)
        else:
            if not os.path.isdir(self.filename):
                self.selected = False
                self.parent.parent.remove_from_list(self.filename)
        if touch:
            if os.path.isdir(self.filename):
                self.browser.set_path(self.filename)
            else:
                self.parent.parent.dispatch_event('on_select',self.filename)

#Class Definations for the buttons inside layerlist
button_css = '''
.simple {
	draw-alpha-background: 1;
	draw-border: 1;
	draw-slider-alpha-background: 1;
	draw-slider-border: 1;
	draw-text-shadow: 1;
}

.colored {
	bg-color: #ff5c00;
	border-radius: 8;
	border-radius-precision: .1;
	font-size: 10;
	slider-border-radius-precision: .1;
	slider-border-radius: 20;
}

'''
css_add_sheet(button_css)

class MTFileBrowser(MTPopup):
    def __init__(self, **kwargs):
        kwargs.setdefault('submit_label', 'Open')
        kwargs.setdefault('title', 'Open a file')
        kwargs.setdefault('size', (350, 300))
        super(MTFileBrowser, self).__init__(**kwargs)

        self.dl = GlDisplayList()
        self._path = '.'
        self.kbsize = self.width, self.height

        # Title
        self.w_path = MTLabel(label=self.path, autoheight=True, size=(self.width, 30), color=(.7, .7, .7, .5))
        self.add_widget(self.w_path)

        # File listing
        self.kb = KineticBrowseLayout(w_limit=4, deletable=False, searchable=False,size=self.kbsize)
        self.add_widget(self.kb, True)

        self.register_event_type('on_select')
        self.selected_files = []

        '''
        self.action_button = MTButton(label=self.type,pos=(10,5),cls=('simple'),size=(50,30))
        self.add_widget(self.action_button)

        @self.action_button.event
        def on_press(*largs):
            self.dispatch_event('on_select',self.selected_files)
            self.hide()
            self.selected_files = []
            for child in self.kb.pchildren:
                child.selected = False

        self.input = MTFormInput(font_size=16,pos=(self.action_button.width+20,5))
        self.input.height = 30
        self.add_widget(self.input)
        '''

    def _get_path(self):
        return self._path
    def _set_path(self, value):
        if value == self._path:
            return
        if not os.path.exists(value):
            return
        self.w_path.label = value
        self._path = value
    path = property(_get_path, _set_path)

    def update_listing(self):
        self.path = os.path.abspath(self.path)
        for name in os.listdir(self.path):
            filename = os.path.join(self.path, name)
            self.kb.add(MTFileEntry(label=name,filename=filename, browser=self))
        self.kb.add(MTFileEntry(label='..',filename=os.path.join(self.path, '../'), browser=self))

    def set_path(self, path):
        self.path = path
        self.remove_widget(self.kb)
        self.kb = None
        self.kb = KineticBrowseLayout(w_limit=4, deletable=False, searchable=False,size=self.kbsize)
        self.add_widget(self.kb)
        self.dl.clear()

    def on_draw(self):
        if not self.dl.is_compiled():
            with DO(self.dl):
                self.update_listing()
        self.dl.draw()
        super(MTFileBrowser, self).on_draw()

    def add_to_list(self,filename):
        self.selected_files.append(filename)

    def remove_from_list(self,filename):
        self.selected_files.remove(filename)

    def on_select(self,filelist):
        pass

if __name__ == '__main__':
    m = MTWindow()
    m.add_widget(MTFileBrowser())
    runTouchApp()
