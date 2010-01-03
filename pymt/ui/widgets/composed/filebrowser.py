'''
File browser: a filebrowser view + a popup file browser
'''

import os
import re
import pymt
from ....utils import is_color_transparent, curry
from ....graphx import drawCSSRectangle, set_color
from ...factory import MTWidgetFactory
from ..label import MTLabel
from ..button import MTToggleButton
from kineticlist import MTKineticList, MTKineticItem
from popup import MTPopup

__all__ = ['MTFileBrowser', 'MTFileBrowserView', 'MTFileEntryView',
        'MTFileListEntryView', 'MTFileIconEntryView']

# Search icons in data/icons/filetype
icons_filetype_dir = os.path.join(pymt.pymt_data_dir, 'icons', 'filetype')

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

class MTFileEntryView(MTKineticItem):
    '''Base view class for every file entry'''
    def __init__(self, **kwargs):
        super(MTFileEntryView, self).__init__(**kwargs)
        self.type_image = None
        self.filename   = kwargs.get('filename')
        self.browser    = kwargs.get('browser')
        self.label_txt  = kwargs.get('label')

        self.get_image_for_filename()

    def get_image_for_filename(self):
        '''Return image for current filename'''
        if os.path.isdir(self.filename):
            self.type_image = FileTypeFactory.get('folder')
        else:
            ext = self.label_txt.split('.')[-1]
            self.type_image = FileTypeFactory.get(ext)

    def striptext(self, text, number=10):
        '''Strip a text to `number` characters, without space/tab'''
        return str(text)[:number].strip("\t ")

    def draw(self):
        if self.selected:
            color = self.style['item-selected']
        else:
            color = self.style['bg-color']
        if not is_color_transparent(color):
            set_color(*color)
            drawCSSRectangle(pos=self.pos, size=self.size, style=self.style)


class MTFileListEntryView(MTFileEntryView):
    '''A list-view for file entries'''
    def __init__(self, **kwargs):
        super(MTFileListEntryView, self).__init__(**kwargs)
        self.height         = 25
        self.image          = pymt.Image(self.type_image, scale=0.5)
        self.labelWX        = MTLabel(label=self.striptext(self.label_txt, 50),
                anchor_x='left', anchor_y='center', halign='center')
        self.add_widget(self.labelWX)
        self.selected       = False
        self.browser.w_limit    = 1

    def draw(self):
        self.labelWX.pos    = self.x + self.image.width + 3, self.y + int(self.height / 2.)
        super(MTFileListEntryView, self).draw()
        self.image.pos = self.pos
        self.image.draw()


class MTFileIconEntryView(MTFileEntryView):
    '''An icon-view for file entries'''
    def __init__(self, **kwargs):
        super(MTFileIconEntryView, self).__init__(**kwargs)
        self.size           = (80, 80)
        self.image          = pymt.Image(self.type_image)
        self.labelWX        = MTLabel(label=self.striptext(self.label_txt, 10),
                anchor_x='center', anchor_y='center', halign='center')
        self.add_widget(self.labelWX)
        self.selected       = False
        self.browser.w_limit= 4

    def draw(self):
        self.labelWX.pos    = int(self.x + self.width / 2.), int(self.y + 10)
        self.image.x        = self.x + int(self.image.width / 2) - 5
        self.image.y        = self.y + int(self.image.height / 2) - 5

        super(MTFileIconEntryView, self).draw()
        self.image.draw()


class MTFileBrowserView(MTKineticList):
    '''A base view of filebrowser. Can be plugged in any widget.

    :Parameters:
        `path` : str, default to None
            Default path to load
        `show_hidden` : bool, default to False
            Show hidden files
        `view` : class, default to MTFileIconEntryView)
            Class to use for creating a entry view
        `filters` : list, default to []
            List of regex to use for file filtering.
            Directories are not affected by filters.
        `multipleselection` : bool, default to False
            Allow multiple selection of files

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
        kwargs.setdefault('view', MTFileIconEntryView)
        kwargs.setdefault('filters', [])
        kwargs.setdefault('multipleselection', False)

        super(MTFileBrowserView, self).__init__(**kwargs)

        self.register_event_type('on_path_change')

        self.selection = []
        self._path          = '(invalid path)'
        self.show_hidden    = kwargs.get('show_hidden')
        self.path           = kwargs.get('path')
        self.view           = kwargs.get('view')
        self.filters        = kwargs.get('filters')
        self.multipleselection = kwargs.get('multipleselection')

    def update(self):
        '''Update the content of view. You must call this function after
        any change of a property. (except path.)'''
        # remove all actual entries
        self.clear()

        children = []
        listfiles = os.listdir(self.path)
        listfiles.sort()

        # add each file from directory
        # only files are filtred with filters
        for name in reversed(listfiles):
            filename = os.path.join(self.path, name)

            # filter on hidden file if requested
            if not self.show_hidden:
                if name != '..' and name[0] == '.':
                    continue

            if os.path.isdir(filename):
                continue

            # filtering
            if len(self.filters):
                match = False
                for filter in self.filters:
                    if re.match(filter, name):
                        match = True
                if not match:
                    continue

            # add this file as new file.
            children.append(self.view(
                label=name, filename=filename,
                browser=self, size=self.size
            ))

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
            children.append(self.view(
                label=name, filename=filename,
                browser=self, size=self.size
            ))

        # add always "to parent"
        children.append(self.view(
            label='..', filename=os.path.join(self.path, '../'),
            browser=self, size=self.size
        ))


        # attach handlers
        for child in children:
            child.push_handlers(on_press=curry(self._on_file_selected, child))
            self.add_widget(child, front=False)

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

    def _on_file_selected(self, fileview, touch):
        # auto change for directory
        filename = fileview.filename
        if os.path.isdir(filename):
            self.path = filename
            return

        # select file ?
        if not fileview.selected:
            if not self.multipleselection:
                for child in self.children:
                    child.selected = False
            fileview.selected = True
            if filename not in self.selection:
                if not self.multipleselection:
                    self.selection = []
                self.selection.append(filename)
        elif self.multipleselection:
            fileview.selected = False
            if filename in self.selection:
                self.selection.remove(filename)

    def on_path_change(self, path):
        pass


class MTFileBrowserToggle(MTToggleButton):
    '''Internal Button for FileBrowser'''
    def __init__(self, **kwargs):
        kwargs.setdefault('label', '')
        kwargs.setdefault('cls', 'popup-button')
        super(MTFileBrowserToggle, self).__init__(**kwargs)
        self.icon = kwargs.get('icon')

    def _set_icon(self, value):
        self.image = pymt.Image(os.path.join(pymt.pymt_data_dir, 'icons', value))
    icon = property(fset=_set_icon)

    def draw(self):
        super(MTFileBrowserToggle, self).draw()
        self.image.x = self.x + (self.width - self.image.width) / 2.
        self.image.y = self.y + (self.height - self.image.height) / 2.
        self.image.draw()


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
        `filters` : list, default to []
            List of regex to use for file filtering.
            Directories are not affected by filters.
        `multipleselection` : bool, default to False
            Allow multiple selection of files
        `exit_on_submit` : bool, default to True
            Allows to decide whether to close the window or just hide it, on pressing submit button

    :Events:
        `on_select`
            This event is generated whenever the user press submit button.
            A list of files selected are also passed as a parameter to this function
    '''

    def __init__(self, **kwargs):
        kwargs.setdefault('submit_label', 'Open')
        kwargs.setdefault('title', 'Open a file')
        kwargs.setdefault('size', (350, 300))
        kwargs.setdefault('filters', [])
        kwargs.setdefault('multipleselection', False)
        kwargs.setdefault('exit_on_submit', True)

        super(MTFileBrowser, self).__init__(**kwargs)

        self.register_event_type('on_select')
        
        self.exit_on_submit = kwargs.get('exit_on_submit')

        # save size before resizing of Popup Layout
        self.kbsize = self.width, self.height

        # Title
        self.w_path = MTLabel(label='.', autoheight=True, size=(self.width, 30), color=(.7, .7, .7, .5))
        self.add_widget(self.w_path)

        # File View
        self.view = MTFileBrowserView(size=self.kbsize, filters=kwargs.get('filters'),
                multipleselection=kwargs.get('multipleselection'))
        self.view.push_handlers(on_path_change=self._on_path_change)
        self.add_widget(self.view, True)

        # Update listing
        self.view.path = '.'

        # Show hidden files
        self.w_hiddenfile = MTFileBrowserToggle(icon='filebrowser-hidden.png', size=(40, 40))
        self.w_hiddenfile.push_handlers(on_press=curry(self._toggle_hidden, self.w_hiddenfile))
        self.l_buttons.add_widget(self.w_hiddenfile)

        # Select view
        self.w_view = MTFileBrowserToggle(icon='filebrowser-iconview.png', size=(40, 40))
        self.w_view.push_handlers(on_press=curry(self._toggle_view, self.w_view))
        self.l_buttons.add_widget(self.w_view, True)

    def _toggle_hidden(self, btn, *largs):
        if btn.get_state() == 'down':
            self.view.show_hidden = True
        else:
            self.view.show_hidden = False
        self.view.update()

    def _toggle_view(self, btn, *largs):
        if btn.get_state() == 'down':
            btn.icon = 'filebrowser-listview.png'
            self.view.view = MTFileListEntryView
        else:
            btn.icon = 'filebrowser-iconview.png'
            self.view.view = MTFileIconEntryView
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
        self.reset_selection()
        if self.exit_on_submit:
            self.close()
        else:
            self.hide()

    def on_cancel(self):
        self.reset_selection()
        if self.exit_on_submit:
            self.close()
        else:
            self.hide()

    def on_select(self, filelist):
        pass

    def reset_selection(self):
        self.view.selection = []
        self.view.update()

# Register Default File types with their icons
FileTypeFactory.register(['jpg','jpeg'],
    os.path.join(icons_filetype_dir, 'image-jpeg.png'))
FileTypeFactory.register(['svg'],
    os.path.join(icons_filetype_dir, 'image-svg.png'))
FileTypeFactory.register(['png'],
    os.path.join(icons_filetype_dir, 'image-png.png'))
FileTypeFactory.register(['bmp'],
    os.path.join(icons_filetype_dir, 'image-bmp.png'))
FileTypeFactory.register(['mpg','mpeg','avi','mkv','flv'],
    os.path.join(icons_filetype_dir, 'video.png'))
FileTypeFactory.register(['folder'],
    os.path.join(icons_filetype_dir, 'folder.png'))
FileTypeFactory.register(['unknown'],
    os.path.join(icons_filetype_dir, 'unknown.png'))

# Register all bases widgets
MTWidgetFactory.register('MTFileBrowser', MTFileBrowser)
MTWidgetFactory.register('MTFileBrowserView', MTFileBrowserView)
