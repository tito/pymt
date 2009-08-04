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


class MTFileListEntryView(MTKineticItem):
    def __init__(self, **kwargs):
        super(MTFileListEntryView, self).__init__(**kwargs)
        self.filename   = kwargs.get('filename')
        self.browser    = kwargs.get('browser')
        self.label_txt  = kwargs.get('label')
        self.type_image = None
        if os.path.isdir(self.filename):
            self.type_image = FileTypeFactory.get('folder')
        else:
            ext = self.label_txt.split('.')[-1]
            self.type_image = FileTypeFactory.get(ext)
        self.height         = 25
        img                 = pyglet.image.load(self.type_image)
        self.image          = pyglet.sprite.Sprite(img)
        self.scale          = kwargs.get('scale')
        self.labelWX        = MTLabel(label=str(self.label_txt)[:50],
                anchor_x='left', anchor_y='center', halign='center')
        self.add_widget(self.labelWX)
        self.selected       = False
        self.browser.w_limit    = 1

    def draw(self):
        if self.selected:
            set_color(1.0,0.39,0.0)
            drawCSSRectangle(size=self.size,style={'border-radius': 8,'border-radius-precision': .1}, pos=self.pos)
        else:
            set_color(0,0,0,0)
            drawCSSRectangle(size=self.size,style={'border-radius': 8,'border-radius-precision': .1}, pos=self.pos)
        self.image.x        = self.x
        self.image.y        = self.y
        self.image.scale    = .5
        self.image.draw()
        self.labelWX.pos    = self.x + self.image.width + 3, self.y + int(self.height / 2.)

    def on_press(self, touch):
        if not self.selected:
            if not os.path.isdir(self.filename):
                self.selected = True
                if self.filename not in self.browser.selection:
                    self.browser.selection.append(self.filename)
        else:
            if not os.path.isdir(self.filename):
                self.selected = False
                if self.filename in self.browser.selection:
                    self.browser.selection.remove(self.filename)
        if touch:
            if os.path.isdir(self.filename):
                self.browser.path = self.filename
            if touch.is_double_tap:
                self.browser.dispatch_event('on_select', self.filename)


class MTFileEntryView(MTKineticItem):
    def __init__(self, **kwargs):
        kwargs.setdefault('scale', 1.0)
        super(MTFileEntryView, self).__init__(**kwargs)
        self.filename   = kwargs.get('filename')
        self.browser    = kwargs.get('browser')
        self.label_txt  = kwargs.get('label')
        self.type_image = None
        if os.path.isdir(self.filename):
            self.type_image = FileTypeFactory.get('folder')
        else:
            ext = self.label_txt.split('.')[-1]
            self.type_image = FileTypeFactory.get(ext)
        self.size           = (80, 80)
        img                 = pyglet.image.load(self.type_image)
        self.image          = pyglet.sprite.Sprite(img)
        self.image.x        = self.x
        self.image.y        = self.y
        self.scale          = kwargs.get('scale')
        self.image.scale    = self.scale
        self.labelWX        = MTLabel(label=str(self.label_txt)[:10],
                anchor_x='center', anchor_y='center', halign='center')
        self.add_widget(self.labelWX)
        self.selected       = False
        self.browser.w_limit= 4

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
                if self.filename not in self.browser.selection:
                    self.browser.selection.append(self.filename)
        else:
            if not os.path.isdir(self.filename):
                self.selected = False
                if self.filename in self.browser.selection:
                    self.browser.selection.remove(self.filename)
        if touch:
            if os.path.isdir(self.filename):
                self.browser.path = self.filename
            if touch.is_double_tap:
                self.browser.dispatch_event('on_select', self.filename)


class MTFileBrowserView(MTKineticList):
    '''A base view of filebrowser. Can be plugged in any widget.

    :Parameters:
        `path` : str, default to None
            Default path to load
        `show_hidden` : bool, default to False
            Show hidden files
        `entry_view` : class, default to MTFileEntryView)
            Class to use for creating a entry view

    :Events:
        `on_path_change` : (str)
            Fired when path changed
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('w_limit', 4)
        kwargs.setdefault('deletable', False)
        kwargs.setdefault('searchable', False)
        kwargs.setdefault('title', None)
        kwargs.setdefault('path', None)
        kwargs.setdefault('show_hidden', False)
        kwargs.setdefault('entry_view', MTFileEntryView)

        super(MTFileBrowserView, self).__init__(**kwargs)

        self.register_event_type('on_path_change')

        self.selection = []
        self._path          = '(invalid path)'
        self.show_hidden    = kwargs.get('show_hidden')
        self.path           = kwargs.get('path')
        self.entry_view     = kwargs.get('entry_view')

    def update(self):
        '''Update the content of view. You must call this function after
        any change of a property. (except path.)'''
        # remove all actual entries
        self.clear()

        listfiles = os.listdir(self.path)
        listfiles.sort()

        # add each file from directory
        for name in reversed(listfiles):
            filename = os.path.join(self.path, name)

            # filter on hidden file if requested
            if not self.show_hidden:
                if name != '..' and name[0] == '.':
                    continue

            if os.path.isdir(filename):
                continue

            # add this file as new file.
            self.add_widget(self.entry_view(
                label=name, filename=filename,
                browser=self, size=self.size
            ), front=False)

        # second time, do directories
        for name in reversed(listfiles):
            filename = os.path.join(self.path, name)

            # filter on hidden file if requested
            if not self.show_hidden:
                if name != '..' and name[0] == '.':
                    continue

            if not os.path.isdir(filename):
                continue

            # add this file as new file.
            self.add_widget(self.entry_view(
                label=name, filename=filename,
                browser=self, size=self.size
            ), front=False)

        # add always "to parent"
        self.add_widget(self.entry_view(
            label='..', filename=os.path.join(self.path, '../'),
            browser=self, size=self.size
        ), front=False)

    def _get_path(self):
        return self._path
    def _set_path(self, value):
        if value is None:
            return
        if value == self._path:
            return
        # get absolute path
        value = os.path.abspath(value)
        if not os.path.exists(value):
            return
        self._path = value
        # update the view
        self.update()
        # and dispatch the new path
        self.dispatch_event('on_path_change', self._path)
    path = property(_get_path, _set_path, doc='Change current path')

    def on_path_change(self, path):
        pass


class MTFileBrowserToggle(MTToggleButton):
    '''Internal Button for FileBrowser'''
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

        self.register_event_type('on_select')

        # save size before resizing of Popup Layout
        self.kbsize = self.width, self.height

        # Title
        self.w_path = MTLabel(label='.', autoheight=True, size=(self.width, 30), color=(.7, .7, .7, .5))
        self.add_widget(self.w_path)

        # File View
        self.view = MTFileBrowserView(size=self.kbsize)
        self.view.push_handlers(on_path_change=self._on_path_change)
        self.add_widget(self.view, True)

        # Update listing
        self.view.path = '.'

        # Show hidden files
        self.w_hiddenfile = MTFileBrowserToggle(icon='filebrowser-hidden.png', size=(40, 40))
        self.w_hiddenfile.push_handlers(on_press=curry(self._toggle_hidden, self.w_hiddenfile))
        self.l_buttons.add_widget(self.w_hiddenfile, True)

    def _toggle_hidden(self, btn, *largs):
        if btn.get_state() == 'down':
            self.view.show_hidden = True
            self.view.update()
        else:
            self.view.show_hidden = False
            self.view.update()

    def _on_path_change(self, path):
        if len(path) > int(self.size[0]/8) :
            folders = path.split(os.path.sep)
            temp_label = ''
            i = -1
            max_len = int(self.size[0]/8)-8
            while len(temp_label) < max_len:
                temp_label = folders[i] + os.path.sep + temp_label
                i -= 1
            self.w_path.label = '..' + os.path.sep + temp_label
        else:
            self.w_path.label = path

    def on_submit(self):
        self.dispatch_event('on_select', self.view.selection)
        self.close()

    def on_select(self, filelist):
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
