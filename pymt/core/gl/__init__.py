'''
GL: Select which library will be used for providing OpenGL support
'''

# Right now, only PyOpenGL
from pymt.config import pymt_config
from pymt.logger import Logger
import OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *

version = glGetString(GL_VERSION)
Logger.info('GL: OpenGL version <%s>' % str(version))

# Disable pyOpenGL auto GL Error Check?
gl_check = pymt_config.get('pymt', 'gl_error_check')
if gl_check.lower() in ['0', 'false', 'no']:
    import OpenGL
    OpenGL.ERROR_CHECKING = False

