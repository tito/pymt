from __future__ import with_statement
from pymt import *
import os, sys, random

class MTFileEntry(MTButton):
    def __init__(self, filename, browser, **kwargs):
        self.filename   = filename
        self.browser    = browser
        if not kwargs.has_key('label'):
            kwargs.setdefault('label', os.path.basename(self.filename))
        super(MTFileEntry, self).__init__(**kwargs)
        #self.size = (self.width, self.label_obj.content_height)
        self.size = (self.label_obj.content_width, self.label_obj.content_height)

    def on_press(self, touchID, x, y):
        if os.path.isdir(self.filename):
            self.browser.set_path(self.filename)
        else:
            self.browser.toggle(self.filename)


class MTFileBrowser(MTScatterWidget):
    def __init__(self, **kwargs):
        super(MTFileBrowser, self).__init__(do_scale=False, **kwargs)
        self.dl = GlDisplayList()
        self.draw_children = False
        self.path = '.'
        self.layout = HVLayout(alignment='vertical', invert_y=True, padding=30,
                               uniform_width=True)
        self.add_widget(self.layout)
        self.widgets = {}

    def set_path(self, path):
        self.path = path
        self.dl.clear()

    def toggle(self, filename):
        w = self.get_parent_window()

        # if file is already open, close it
        if self.widgets.has_key(filename):
            w.remove_widget(self.widgets[filename])
            del self.widgets[filename]
            return

        # open file
        ext = filename.split('.')[-1]
        pos = (int(random.uniform(0, w.width)), int(random.uniform(0, w.height)))
        item = None
        if ext in ['jpg', 'jpeg', 'png']:
            item = MTScatterImage(pos=pos, filename=filename)
        elif ext in ['svg']:
            item = MTScatterSvg(pos=pos, filename=filename)
        elif ext in ['mpg', 'mpeg', 'avi', 'mkv', 'flv']:
            item = MTVideo(pos=pos, video=filename)
        if item:
            w.add_widget(item)
            self.widgets[filename] = item

    def update_listing(self):
        self.layout.children = []
        self.path = os.path.abspath(self.path)
        for name in os.listdir(self.path):
            filename = os.path.join(self.path, name)
            self.layout.add_widget(MTFileEntry(filename=filename, browser=self))
        self.layout.add_widget(MTFileEntry(filename=os.path.join(self.path, '../'), label='..', browser=self))
        self.size = (self.layout.content_width, self.layout.content_height)

    def draw(self):
        if not self.dl.is_compiled():
            self.update_listing()
            with DO(self.dl, gx_blending):
                set_color(.2, .2, .2, .6)
                drawRectangle((0,0), self.size)
                for w in self.children:
                    w.dispatch_event('on_draw')
        self.dl.draw()


def pymt_plugin_activate(root, ctx):
    ctx.filebrowser = MTFileBrowser()
    root.add_widget(ctx.filebrowser)

def pymt_plugin_deactivate(root, ctx):
    root.remove_widget(ctx.filebrowser)

if __name__ == '__main__':
    w = MTWindow()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
