from __future__ import with_statement
import os
from pymt import *
from pyglet.gl import *
import os, sys, random
from pyglet.text import Label

icons_filetype_dir = os.path.join(pymt_data_dir, 'icons', 'filetype')

class FileTypeFactory:
    __filetypes__ = {}
    @staticmethod
    def register(items):
        for item in items:
            FileTypeFactory.__filetypes__[item[0]] = item[1]

    @staticmethod
    def list():
        return FileTypeFactory.__filetypes__

    @staticmethod
    def get(type):
        if type in FileTypeFactory.__filetypes__:
            return FileTypeFactory.__filetypes__[type]
        else:
            return FileTypeFactory.__filetypes__['unknown']

class MTFileEntry(MTButton, MTKineticObject):
    def __init__(self, **kwargs):
        kwargs.setdefault('scale', 1.0)
        super(MTFileEntry, self).__init__(**kwargs)
        self.filename   = kwargs.get('filename')
        self.browser    = kwargs.get('browser')
        self.label_txt = kwargs.get('label')
        self.type_image = None
        if os.path.isdir(self.filename):
            self.type_image = FileTypeFactory.get("folder")
        else:
            ext = self.label_txt.split('.')[-1]
            self.type_image = FileTypeFactory.get(ext)
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
                self.browser.add_to_list(self.filename)
        else:
            if not os.path.isdir(self.filename):
                self.selected = False
                self.browser.remove_from_list(self.filename)
        if touch:
            if os.path.isdir(self.filename):
                self.browser.path = self.filename
            if touch.is_double_tap:
                self.browser.dispatch_event('on_select',self.filename)

class MTFileBrowser(MTPopup):
    def __init__(self, **kwargs):
        kwargs.setdefault('submit_label', 'Open')
        kwargs.setdefault('title', 'Open a file')
        kwargs.setdefault('size', (350, 300))
        super(MTFileBrowser, self).__init__(**kwargs)

        self._path = '(invalid path)'
        self.kbsize = self.width, self.height

        # Title
        self.w_path = MTLabel(label=self.path, autoheight=True, size=(self.width, 30), color=(.7, .7, .7, .5))
        self.add_widget(self.w_path)

        # File listing
        self.kb = MTKineticList(w_limit=4, deletable=False, searchable=False,size=self.kbsize, title=None)
        self.add_widget(self.kb, True)

        self.register_event_type('on_select')
        self.selected_files = []

        # Update listing the first call
        self.path = '.'

    def _get_path(self):
        return self._path
    def _set_path(self, value):
        if value == self._path:
            return
        value = os.path.abspath(value)
        if not os.path.exists(value):
            return
        if len(value) > 39:
            self.w_path.label = ".."+value[len(value)-40:]
        else:
            self.w_path.label = value
        self._path = value
        self.update_listing()
    path = property(_get_path, _set_path)

    def update_listing(self):
        self.kb.clear()

        # add each file from directory
        for name in os.listdir(self.path):
            filename = os.path.join(self.path, name)
            self.kb.add_widget(MTFileEntry(
                label=name, filename=filename,
                browser=self
            ))

        # add always "to parent"
        self.kb.add_widget(MTFileEntry(
            label='..', filename=os.path.join(self.path, '../'),
            browser=self
        ))

    def add_to_list(self,filename):
        self.selected_files.append(filename)

    def remove_from_list(self,filename):
        self.selected_files.remove(filename)

    def on_submit(self):
        self.dispatch_event('on_select',self.selected_files)
        self.close()

    def on_select(self,filelist):
        pass

# Register Default File types with their icons
FileTypeFactory.register([['jpg',os.path.join(icons_filetype_dir, 'image-jpeg.png')],
                          ['jpeg',os.path.join(icons_filetype_dir, 'image-jpeg.png')],
                          ['svg',os.path.join(icons_filetype_dir, 'image-svg.png')],
                          ['png',os.path.join(icons_filetype_dir, 'image-png.png')],
                          ['bmp',os.path.join(icons_filetype_dir, 'image-bmp.png')],
                          ['mpg',os.path.join(icons_filetype_dir, 'video.png')],
                          ['mpeg',os.path.join(icons_filetype_dir, 'video.png')],
                          ['avi',os.path.join(icons_filetype_dir, 'video.png')],
                          ['mkv',os.path.join(icons_filetype_dir, 'video.png')],
                          ['flv',os.path.join(icons_filetype_dir, 'video.png')],
                          ['folder',os.path.join(icons_filetype_dir, 'folder.png')],
                          ['unknown',os.path.join(icons_filetype_dir, 'unknown.png')]
                         ])
        
        
if __name__ == '__main__':
    m = MTWindow()
    fb = MTFileBrowser()
    m.add_widget(fb)
    @fb.event
    def on_select(list):
        print list
    runTouchApp()
