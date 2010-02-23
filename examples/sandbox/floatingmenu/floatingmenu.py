IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Floating Menu Demo'
PLUGIN_AUTHOR = 'Riley Dutton'
PLUGIN_EMAIL = 'riley@newspringmedia.com'
PLUGIN_DESCRIPTION = 'A fun explosions game, with modes for both whack a mole and chain reaction fun!'

from pymt import *
from pyglet.media import *
from OpenGL.GL import *
import random
import rabbyt.collisions

def pymt_plugin_activate(root, ctx):
    ctx.PA = PlayArea(size=(root.width, root.height))
    getClock().schedule_interval(showfps, 5.0)
    root.add_widget(ctx.PA)


def pymt_plugin_deactivate(root, ctx):
   root.remove_widget(ctx.PA)

if __name__ == '__main__':
    w = MTWindow(color=(0,0,0,1))
    #w.set_fullscreen()
    #print gl_info.get_version()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
