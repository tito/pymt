from pymt import *
from mutagen.id3 import ID3
from cStringIO import StringIO
#A random list of stuff that was in my head at the time
list = ['Hello', 'World', 'Foo', 'bar', 'biz', 'Emacs!', 'Python!', 'PyMT!', 'Lambda!', 'IRC!', '#pymt', 'Freenode.net!', 'xmonad!']

class fileList(MTKineticScrollText):
    def __init__(self, **kwargs):
        global list
        kwargs.setdefault('pos', (0,0))
        kwargs.setdefault('size', (200,400))
        kwargs.setdefault('items', list)
        super(fileList, self).__init__(**kwargs)                

    def on_item_select(self,v):
        print v      
       
class MusicPlayer(MTScatterWidget):
    def __init__(self, **kwargs):
        kwargs.setdefault('scale', 1.0)
        super(MusicPlayer, self).__init__(**kwargs)  
        mms = fileList()
        mms.push_handlers('on_item_select', mms.on_item_select)
        self.add_widget(mms)
        
    """def draw(self):
        pass"""

        
if __name__ == '__main__':
    w = MTWindow(color=(0,0,0,1.0), fullscreen=True)
    w.add_widget(MusicPlayer(size=(210,410)))
    runTouchApp()