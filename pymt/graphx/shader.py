'''
Shader: abstract compilation and usage
'''

__all__ = ('ShaderException', 'Shader')

from pymt.logger import pymt_logger
#from ctypes import *
from OpenGL.GL import GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, \
        glCreateProgram, glGetUniformLocation, glUniform1i, \
        glUniform1f, glLinkProgram, glCreateShader, glUseProgram, \
        glAttachShader, glCompileShader, glShaderSource, \
        glGetProgramInfoLog, glGetShaderInfoLog


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
            self.vertex_shader = self.create_shader(
                vertex_source, GL_VERTEX_SHADER)
            glAttachShader(self.program, self.vertex_shader)

        if fragment_source:
            self.fragment_shader = self.create_shader(
                fragment_source, GL_FRAGMENT_SHADER)
            glAttachShader(self.program, self.fragment_shader)

        glLinkProgram(self.program)
        message = self.get_program_log(self.program)
        if message:
            pymt_logger.debug('Shader: shader program message: %s' % message)

    def create_shader(self, source, shadertype):
        shader = glCreateShader(shadertype)
        # PyOpenGL bug ? He's waiting for a list of string, not a string
        # on some card, it failed :)
        if isinstance(source, basestring):
            source = [source]
        glShaderSource(shader, source)
        glCompileShader(shader)
        message = self.get_shader_log(shader)
        if message:
            pymt_logger.debug('Shader: shader message: %s' % message)
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
            raise TypeError('Only single floats and ints are supported so far')

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

