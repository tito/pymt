'''
Single Desktop User

A very simple desktop, made to be used by one user only.
Feature coverflow widget, xml widget and css styling.

Mathieu
'''

from os.path import join, dirname, exists
from pymt import *

current_dir = dirname(__file__)

class DesktopClose(MTButton):
    def __init__(self, **kwargs):
        super(DesktopClose, self).__init__(**kwargs)
        self.radius = kwargs['radius']

    def draw_background(self):
        if self.state == 'down':
            set_color(.8, .0, .0, .8)
        else:
            set_color(.0, .0, .0, .8)
        drawCircle(pos=self.pos, radius=self.radius)
        set_color(.7, .7, .7, .8)
        drawCircle(pos=self.pos, radius=self.radius, linewidth=1.5)

    def collide_point(self, x, y):
        return Vector(self.pos).distance((x, y)) <= self.radius

class Desktop(MTBoxLayout):
    layout_def = '''
    <MTBoxLayout orientation='"vertical"' cls='"desktop-background"'>
        <MTCoverFlow size_hint='(1, .7)' cls='"desktop-coverflow"'
            thumbnail_size='(256, 256)' cover_distance='150' id='"coverflow"'/>
        <MTAnchorLayout size_hint='(1, .3)'>
            <MTBoxLayout cls='"form"' padding='20' orientation='"vertical"'>
                <MTLabel id='"title"' label='"Unknown Title"' autosize='True'
                    cls='"desktop-title"' anchor_x='"center"'/>
                <MTLabel id='"author"' label='"Unknown Author"' autosize='True'
                    cls='"desktop-author"' anchor_x='"center"'/>
                <MTLabel id='"description"' label='"Unknown Description"' autosize='True'
                    cls='"desktop-description"' anchor_x='"center"'/>
            </MTBoxLayout>
        </MTAnchorLayout>
    </MTBoxLayout>
    '''

    def __init__(self, **kwargs):
        super(Desktop, self).__init__(**kwargs)
        self.xml = xml = XMLWidget(xml=Desktop.layout_def)
        self.xml.autoconnect(self)
        self.add_widget(self.xml.root)
        self.coverflow = xml.getById('coverflow')
        self.title = xml.getById('title')
        self.author = xml.getById('author')
        self.description = xml.getById('description')
        self.populate()

    def populate(self):
        # search plugins
        self.plugins = plugins = MTPlugins(plugin_paths=[
            join(current_dir, '..', 'apps'),
            join(current_dir, '..', 'games')
        ])
        plugins.search_plugins()

        # populate the coverflow with plugin list
        first_entry = None
        for key in plugins.list():
            plugin = plugins.get_plugin(key)
            infos = plugins.get_infos(plugin)

            icon = None
            for icon_filename in ('icon-large.png', 'icon-large.jpg',
                                  infos['icon'], 'icon.png'):
                icon = join(infos['path'], icon_filename)
                if exists(icon):
                    break
                icon = None

            # no icon ?
            if icon is None:
                print 'No icon found for', infos['title']
                continue

            # create an image button for every plugin
            button = MTImageButton(filename=icon)
            if first_entry is None:
                first_entry = button
            button.infos = infos
            button.plugin = plugin
            self.coverflow.add_widget(button)

        # display first entry
        if first_entry:
            self.show_plugin(first_entry)

    def on_coverflow_change(self, widget):
        '''Called when the coverflow widget is changed
        '''
        self.show_plugin(widget)

    def on_coverflow_select(self, widget):
        '''Called when the coverflow widget have a selection
        '''
        plugin = widget.plugin
        win = self.parent
        self.plugins.activate(plugin, self.parent)
        for pos in ((0, 0), (win.width, 0)):
            close_button = DesktopClose(radius=75, pos=pos)
            close_button.connect('on_release', curry(
                self.on_plugin_close, self.parent, plugin))
            self.parent.add_widget(close_button)
        self.parent.remove_widget(self)

    def on_plugin_close(self, win, plugin, *largs):
        '''Called when the close button is hitted
        '''
        self.plugins.deactivate(plugin, win)
        win.children.clear()
        win.add_widget(self)

    def show_plugin(self, widget):
        '''Show information about a plugin in the container
        '''
        self.title.label = widget.infos['title']
        self.author.label = widget.infos['author']
        self.description.label = widget.infos['description']

if __name__ == '__main__':
    # manual add cause of font path
    with open(join(current_dir, 'data', 'desktop-single.css')) as fd:
        css_data = fd.read() % dict(fontpath=join(current_dir, 'data', ''))
    css_add_sheet(css_data)
    runTouchApp(Desktop())
