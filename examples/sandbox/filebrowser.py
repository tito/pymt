from __future__ import with_statement
import os
import pymt
from pymt import *
from pyglet.gl import *
import os, sys, random
from pyglet.text import Label

icons_filetype_dir = os.path.join(pymt_data_dir, 'icons', 'filetype')

class FileTypeFactory:
    '''
    FileType Factory: Maintains a Dictionary of all filetypes and its icons.
    '''
    __filetypes__ = {}
    @staticmethod
    def register(types,iconpath):
        '''If a user wants to register a new file type or replace a existing icon,
        he can use register method as follows ::

            FileTypeFactory.register(['type1','type2'],"path_to_icon")
        '''
        for type in types:
            FileTypeFactory.__filetypes__[type] = iconpath

    @staticmethod
    def list():
        '''Return all the filetypes availables'''
        return FileTypeFactory.__filetypes__

    @staticmethod
    def get(type):
        '''Return an image for the current type. If type is not found, this
        will return the image for 'unknown' type.'''
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

class MTFileBrowserToggle(MTToggleButton):
    def __init__(self, **kwargs):
        kwargs.setdefault('label', '')
        kwargs.setdefault('cls', 'popup-button')
        super(MTFileBrowserToggle, self).__init__(**kwargs)
        img = pyglet.image.load(os.path.join(pymt.pymt_data_dir, 'icons', kwargs.get('icon')))
        self.sprite = pyglet.sprite.Sprite(img)

    def draw(self):
        super(MTFileBrowserToggle, self).draw()
        self.sprite.x = self.x + (self.width - self.sprite.width) / 2.
        self.sprite.y = self.y + (self.height - self.sprite.height) / 2.
        self.sprite.draw()


class MTFileBrowser(MTPopup):
    '''This Widget provides a filebrowser interface to access the files in your system.
    you can select multiple files at a time and process them together.

    :Parameters:
        `title` : str, default to 'Open a file'
            The title for what reason the filebrowser will be used
        `submit_label` : str, default to 'Open'
            Label for the Submit button, Default set to Open
        `size` : list, default to (350, 300)
            Window size of the browser and its container

    :Events:
        `on_select`
            This event is generated whenever the user press submit button.
            A list of files selected are also passed as a parameter to this function
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('submit_label', 'Open')
        kwargs.setdefault('title', 'Open a file')
        kwargs.setdefault('size', (350, 300))
        super(MTFileBrowser, self).__init__(**kwargs)
        self.sep = os.path.join("%","%")

        self._path = '(invalid path)'
        self.kbsize = self.width, self.height

        # Title
        self.w_path = MTLabel(label=self.path, autoheight=True, size=(self.width, 30), color=(.7, .7, .7, .5))
        self.add_widget(self.w_path)

        # File listing
        self.kb = MTKineticList(w_limit=4, deletable=False, searchable=False,size=self.kbsize, title=None)
        self.add_widget(self.kb, True)

        # Show hidden files
        self.w_hiddenfile = MTFileBrowserToggle(icon='filebrowser-hidden.png', size=(40, 40))
        self.w_hiddenfile.push_handlers(on_press=curry(self._toggle_hidden, self.w_hiddenfile))
        self.l_buttons.add_widget(self.w_hiddenfile, True)
        self.show_hidden = False

        self.register_event_type('on_select')
        self.selected_files = []

        # Update listing the first call
        self.path = '.'

    def _toggle_hidden(self, btn, *largs):
        if btn.get_state() == 'down':
            self.show_hidden = True
            self.update_listing()
        else:
            self.show_hidden = False
            self.update_listing()

    def _get_path(self):
        return self._path
    def _set_path(self, value):
        if value == self._path:
            return
        value = os.path.abspath(value)
        if not os.path.exists(value):
            return
        if len(value) > int(self.size[0]/8) :
            folders = value.split(os.path.sep)
            temp_label = ""
            i = -1
            max_len = int(self.size[0]/8)-8
            while(len(temp_label)< max_len):
                temp_label = folders[i]+os.path.sep+temp_label
                i -= 1
            self.w_path.label = ".."+os.path.sep+temp_label
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
            if not self.show_hidden:
                if name != '..' and name[0] == '.':
                    continue
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
FileTypeFactory.register(['jpg','jpeg'],os.path.join(icons_filetype_dir, 'image-jpeg.png'))
FileTypeFactory.register(['svg'],os.path.join(icons_filetype_dir, 'image-svg.png'))
FileTypeFactory.register(['png'],os.path.join(icons_filetype_dir, 'image-png.png'))
FileTypeFactory.register(['bmp'],os.path.join(icons_filetype_dir, 'image-bmp.png'))
FileTypeFactory.register(['mpg','mpeg','avi','mkv','flv'],os.path.join(icons_filetype_dir, 'video.png'))
FileTypeFactory.register(['folder'],os.path.join(icons_filetype_dir, 'folder.png'))
FileTypeFactory.register(['unknown'],os.path.join(icons_filetype_dir, 'unknown.png'))


if __name__ == '__main__':
    m = MTWindow()
    fb = MTFileBrowser()
    m.add_widget(fb)
    @fb.event
    def on_select(list):
        print list
    runTouchApp()
