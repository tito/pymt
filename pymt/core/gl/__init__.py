'''
GL: Select which library will be used for providing OpenGL support
'''

# Right now, only PyOpenGL
from pymt.logger import Logger
from OpenGL.GL import *
from OpenGL.GLU import *

version = glGetString(GL_VERSION)
Logger.info('GL: OpenGL version <%s>' % str(version))
