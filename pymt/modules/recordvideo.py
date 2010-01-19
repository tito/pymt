'''
Record the opengl output into a video
'''

import os
if 'PYMT_DOC' not in os.environ:
	import pygame
	import pymt
	from OpenGL.GL import glReadBuffer, glReadPixels, GL_RGB, GL_UNSIGNED_BYTE, GL_FRONT
	from pymt.utils import curry

	dump_prefix    = pymt.pymt_config.get('dump', 'prefix')
	dump_format    = pymt.pymt_config.get('dump', 'format')
	dump_idx       = 0

def window_flip_and_save():
    global dump_idx
    win = pymt.getWindow()
    glReadBuffer(GL_FRONT)
    data = glReadPixels(0, 0, win.width, win.height, GL_RGB, GL_UNSIGNED_BYTE)
    surface = pygame.image.fromstring(str(buffer(data)), win.size, 'RGB', True)
    filename = '%s%05d.%s' % (dump_prefix, dump_idx, dump_format)
    pygame.image.save(surface, filename)
    dump_idx += 1

def start(win, ctx):
    win.push_handlers(on_flip=window_flip_and_save)

def stop(win, ctx):
    win.remove_handlers(on_flip=window_flip_and_save)
