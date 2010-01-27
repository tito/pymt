'''
Shader: abstract compilation and usage
'''

__all__ = ['ShaderException', 'Shader']

import pymt
from ctypes import *
from OpenGL.GL import *
from OpenGL.GLU import *

# FIXME Remove that when the bug will be fixed on PyOpenGL
# The default wrapper in PyOpenGL is bugged on ATI card
# It's a open bug.
# http://sourceforge.net/tracker/?func=detail&atid=105988&aid=2935298&group_id=5988

glShaderSourceFIX = platform.createBaseFunction(
	'glShaderSource', dll=platform.GL,
	resultType=None,
	argTypes=(constants.GLhandle, constants.GLsizei, ctypes.POINTER(ctypes.c_char_p), arrays.GLintArray,),
	doc = 'glShaderSource( GLhandle(shaderObj), str( string) ) -> None',
	argNames = ('shaderObj', 'count', 'string', 'length',),
)


class ShaderException(Exception):
    '''Exception launched by shader in error case'''
    pass

class Shader(object):
    '''Create a vertex or fragment shader

    :Parameters:
        `vertex_source` : string, default to None
            Source code for vertex shader
        `fragment_source` : string, default to None
            Source code for fragment shader
    '''
    def __init__(self, vertex_source=None, fragment_source=None):
        self.program = glCreateProgram()

        if vertex_source:
            self.vertex_shader = self.create_shader(vertex_source, GL_VERTEX_SHADER)
            glAttachShader(self.program, self.vertex_shader)

        if fragment_source:
            self.fragment_shader = self.create_shader(fragment_source, GL_FRAGMENT_SHADER)
            glAttachShader(self.program, self.fragment_shader)

        glLinkProgram(self.program)
        message = self.get_program_log(self.program)
        if message:
            pymt.pymt_logger.debug('Shader: shader program message: %s' % message)

    def create_shader(self, source, shadertype):
        shader = glCreateShader(shadertype)

        # FIXME Use the generic wrapper of glShaderSource
        try:
            # use fixed version on ATI and anywhere it works
            char_source = c_char_p(source)
            length = c_int(-1)
            glShaderSourceFIX(shader, 1, byref(char_source), byref(length))
        except:
            # the created function does not work on e.g.
            # Intel GMA 4500MHD...so use built in there
            glShaderSource(shader,source)

        glCompileShader(shader)
        message = self.get_shader_log(shader)
        if message:
            pymt.pymt_logger.debug('Shader: shader message: %s' % message)
        return shader

    def set_uniform_f(self, name, value):
        location = glGetUniformLocation(self.program, name)
        glUniform1f(location, value)

    def set_uniform_i(self, name, value):
        location = glGetUniformLocation(self.program, name)
        glUniform1i(location, value)

    def __setitem__(self, name, value):
        """pass a variable to the shader"""
        if isinstance(value, float):
            self.set_uniform_f(name, value)
        elif isinstance(value, int):
            self.set_uniform_i(name, value)
        else:
            raise TypeError("Only single floats and ints are supported so far")

    def use(self):
        '''Use the shader'''
        glUseProgram(self.program)

    def stop(self):
        '''Stop using the shader'''
        glUseProgram(0)

    def get_shader_log(self, shader):
        '''Return the shader log'''
        return self.get_log(shader, glGetShaderInfoLog)

    def get_program_log(self, shader):
        '''Return the program log'''
        return self.get_log(shader, glGetProgramInfoLog)

    def get_log(self, obj, func):
        value = func(obj)
        return value

