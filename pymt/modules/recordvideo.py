'''
Record the opengl output into a video
'''

import pygame
import pymt
from OpenGL.GL import glReadBuffer, glReadPixels, GL_RGBA, GL_UNSIGNED_BYTE, GL_BACK
from pymt.utils import curry

dump_prefix    = pymt.pymt_config.get('dump', 'prefix')
dump_format    = pymt.pymt_config.get('dump', 'format')
dump_idx       = 0

def window_flip_and_save():
    global dump_idx
    win = pymt.getWindow()
    glReadBuffer(GL_BACK)
    data = glReadPixels(0, 0, win.width, win.height, GL_RGBA, GL_UNSIGNED_BYTE)
    surface = pygame.image.fromstring(str(buffer(data)), win.size, 'RGBA', True)
    filename = '%s%05d.%s' % (dump_prefix, dump_idx, dump_format)
    pygame.image.save(surface, filename)
    dump_idx += 1

def start(win, ctx):
    win.push_handlers(on_flip=window_flip_and_save)

def stop(win, ctx):
    win.remove_handlers(on_flip=window_flip_and_save)
