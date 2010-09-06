'''
File browser: a filebrowser view + a popup file browser
'''

__all__ = (
    'MTFileBrowser', 'MTFileBrowserView',
    'MTFileEntryView', 'MTFileListEntryView',
    'MTFileIconEntryView'
)

import os
import re
import pymt
from pymt.utils import curry
from pymt.loader import Loader
from pymt.graphx import drawCSSRectangle, set_color, drawLabel, getLabel
from pymt.ui.factory import MTWidgetFactory
from pymt.ui.widgets.label import MTLabel
from pymt.ui.widgets.button import MTToggleButton
from pymt.ui.widgets.composed.kineticlist import MTKineticList, MTKineticItem
from pymt.ui.widgets.composed.popup import MTPopup

# Search icons in data/icons/filetype
icons_filetype_dir = os.path.join(pymt.pymt_data_dir, 'icons', 'filetype')

class FileTypeFactory:
    '''
    FileType Factory: Maintains a Dictionary of all filetypes and its icons.
    '''

    __filetypes__ = {}

    @staticmethod
    def register(types, iconpath):
        '''If a user wants to register a new file type or replace a existing
        icon, he can use register method as follows ::

            FileTypeFactory.register(['type1','type2'],"path_to_icon")
        '''
        for ftype in types:
            FileTypeFactory.__filetypes__[ftype] = iconpath

    @staticmethod
    def list():
        '''Return all the filetypes availables'''
        return FileTypeFactory.__filetypes__

    @staticmethod
    def get(ftype):
        '''Return an image for the current type. If type is not found, this
        will return the image for 'unknown' type.'''
        if ftype in FileTypeFactory.__filetypes__:
            return FileTypeFactory.__filetypes__[ftype]
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
        self.selected   = False

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


class MTFileListEntryView(MTFileEntryView):
    '''A list-view for file entries'''
    def __init__(self, **kwargs):
        super(MTFileListEntryView, self).__init__(**kwargs)
        self.height         = 25
        self.image          = Loader.image(self.type_image)
        self.image.scale    = 0.5
        if self.browser._w_limit is None:
            self.browser.w_limit    = 1
        self.font_size = self.style['font-size']

    def draw(self):
        pos = self.image.width, self.y
        # Max number of chars for this entry's label
        max_chars = 20
        # Simple trick to get the maximum label width for the current font size
        self.width = getLabel('W'*max_chars, font_size=self.font_size).width
        if self.selected:
            selected_color = self.style.get('selected-color', (0.4,) * 4)
            set_color(*selected_color)
            drawCSSRectangle(pos=(0, self.y), size=self.size, style=self.style)
        drawLabel(label=self.striptext(self.label_txt, max_chars),
                  pos=pos, anchor_x='left', anchor_y='bottom',
                  font_size=self.style.get('font-size'),
                  color=self.style.get('color'))
        self.image.pos = (0, self.y)
        self.image.draw()


class MTFileIconEntryView(MTFileEntryView):
    '''An icon-view for file entries'''
    def __init__(self, **kwargs):
        super(MTFileIconEntryView, self).__init__(**kwargs)
        self.size           = (80, 80)
        self.image          = Loader.image(self.type_image)
        if self.browser._w_limit is None:
            self.browser.w_limit = 4

    def draw(self):
        if self.selected:
            selected_color = self.style.get('selected-color', (0.4,) * 4)
            set_color(*selected_color)
            drawCSSRectangle(pos=self.pos, size=self.size, style=self.style)
        pos = int(self.x + self.width / 2.), int(self.y + 10)
        drawLabel(label=self.striptext(self.label_txt, 10), pos=pos)
        self.image.x        = self.x + int(self.image.width / 2) - 5
        self.image.y        = self.y + int(self.image.height / 2) - 5
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
        `invert_order` : bool, default to False
            Indicates whether the order the files are displayed in should be reversed

    :Events:
        `on_path_change` : (str)
            Fired when path changed
        `on_selection_change` : list of str
            Fired when selection change
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('deletable', False)
        kwargs.setdefault('searchable', False)
        kwargs.setdefault('title', None)
        kwargs.setdefault('path', None)
        kwargs.setdefault('show_hidden', False)
        kwargs.setdefault('view', MTFileIconEntryView)
        kwargs.setdefault('filters', [])
        kwargs.setdefault('multipleselection', False)

        self._w_limit = kwargs.get('w_limit', None)

        super(MTFileBrowserView, self).__init__(**kwargs)

        self.register_event_type('on_path_change')
        self.register_event_type('on_selection_change')

        self._selection     = []
        self._path          = '(invalid path)'
        self.show_hidden    = kwargs.get('show_hidden')
        self.view           = kwargs.get('view')
        self.filters        = kwargs.get('filters')
        self.multipleselection = kwargs.get('multipleselection')
        self.invert_order = kwargs.get('invert_order', False)

        # only at the end, set path to the user path
        self.path           = kwargs.get('path')

    def update(self):
        '''Update the content of view. You must call this function after
        any change of a property. (except path.)'''
        # remove all actual entries
        self.clear()
        self.selection = []

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
                for regex in self.filters:
                    if re.match(regex, name):
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
            self.add_widget(child, front=self.invert_order)

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
        if os.path.isdir(filename) and touch.is_double_tap:
            # Enter that directory
            self.path = filename
            # Forget about any selection we did before
            self.selection = []
            return

        # select file ?
        selection = self.selection[:]
        if not fileview.selected:
            if not self.multipleselection:
                for child in self.children:
                    child.selected = False
            fileview.selected = True
            if filename not in selection:
                if not self.multipleselection:
                    selection = []
                selection.append(filename)
        elif self.multipleselection:
            fileview.selected = False
            if filename in selection:
                selection.remove(filename)
        self.selection = selection

    def _get_selection(self):
        return self._selection
    def _set_selection(self, x):
        if x == self._selection:
            return
        self._selection = x
        self.dispatch_event('on_selection_change', self._selection)
    selection = property(
        _get_selection, _set_selection,
        doc='Get selected filenames')


    def on_selection_change(self, filelist):
        pass

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
        self.image = pymt.Image(os.path.join(
            pymt.pymt_data_dir, 'icons', value))
    icon = property(fset=_set_icon)

    def draw(self):
        super(MTFileBrowserToggle, self).draw()
        self.image.x = self.x + (self.width - self.image.width) / 2.
        self.image.y = self.y + (self.height - self.image.height) / 2.
        self.image.draw()


class MTFileBrowser(MTPopup):
    '''This Widget provides a filebrowser interface to access the files in your
    system. You can select multiple files at a time and process them together.

    :Parameters:
        `title` : str, default to 'Open a file'
            The title for what reason the filebrowser will be used
        `size` : list, default to (350, 300)
            Window size of the browser and its container
        `filters` : list, default to []
            List of regex to use for file filtering.
            Directories are not affected by filters.
        `multipleselection` : bool, default to False
            Allow multiple selection of files
        `view` : reference to subclass of MTFileEntryView
            Indicates the default view that is used to display icons and filenames
        `invert_order` : bool, default to False
            Indicates whether the order the files are displayed in should be reversed

    :Events:
        `on_select`
            This event is generated whenever the user press submit button.
            A list of files selected are also passed as a parameter to this function
    '''

    def __init__(self, **kwargs):
        kwargs.setdefault('title', 'Open a file')
        kwargs.setdefault('label_submit', 'Open')
        kwargs.setdefault('size', (350, 500))
        kwargs.setdefault('filters', [])
        kwargs.setdefault('multipleselection', False)
        kwargs.setdefault('view', MTFileIconEntryView)
        kwargs.setdefault('invert_order', False)
        kwargs.setdefault('show_toggles', True)
        super(MTFileBrowser, self).__init__(**kwargs)

        self.register_event_type('on_select')

        # Title
        self.w_path = MTLabel(label='.', autoheight=True, size=(self.width, 30),
                              color=(.7, .7, .7, .5))
        #self.add_widget(self.w_path)

        # File View
        self.view = MTFileBrowserView(size_hint=(1, 1), filters=kwargs.get('filters'),
                multipleselection=kwargs.get('multipleselection'), view=kwargs.get('view'),
                invert_order=kwargs.get('invert_order'))
        self.view.push_handlers(on_path_change=self._on_path_change)
        self.add_widget(self.view, True)

        # Update listing
        self.view.path = '.'

        # Show hidden files
        if kwargs['show_toggles']:
            self.w_hiddenfile = MTFileBrowserToggle(icon='filebrowser-hidden.png', size=(40, 40))
            self.w_hiddenfile.push_handlers(on_press=curry(self._toggle_hidden, self.w_hiddenfile))
            self.l_buttons.add_widget(self.w_hiddenfile)

            # Select view
            self.w_view = MTFileBrowserToggle(icon='filebrowser-iconview.png', size=(40, 40))
            self.w_view.push_handlers(on_press=curry(self._toggle_view, self.w_view))
            self.l_buttons.add_widget(self.w_view, True)

    def _toggle_hidden(self, btn, *largs):
        if btn.state == 'down':
            self.view.show_hidden = True
        else:
            self.view.show_hidden = False
        self.view.update()

    def _toggle_view(self, btn, *largs):
        if self.view.view is MTFileIconEntryView:
            btn.icon = 'filebrowser-iconview.png'
            self.view.view = MTFileListEntryView
        else:
            btn.icon = 'filebrowser-listview.png'
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
FileTypeFactory.register(['jpg', 'jpeg'],
    os.path.join(icons_filetype_dir, 'image-jpeg.png'))
FileTypeFactory.register(['svg'],
    os.path.join(icons_filetype_dir, 'image-svg.png'))
FileTypeFactory.register(['png'],
    os.path.join(icons_filetype_dir, 'image-png.png'))
FileTypeFactory.register(['bmp'],
    os.path.join(icons_filetype_dir, 'image-bmp.png'))
FileTypeFactory.register(['mpg', 'mpeg', 'avi', 'mkv', 'flv'],
    os.path.join(icons_filetype_dir, 'video.png'))
FileTypeFactory.register(['folder'],
    os.path.join(icons_filetype_dir, 'folder.png'))
FileTypeFactory.register(['unknown'],
    os.path.join(icons_filetype_dir, 'unknown.png'))

# Register all bases widgets
MTWidgetFactory.register('MTFileBrowser', MTFileBrowser)
MTWidgetFactory.register('MTFileBrowserView', MTFileBrowserView)
