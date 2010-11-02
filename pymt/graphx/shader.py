'''
Shader: abstract compilation and usage
'''

__all__ = ('ShaderException', 'Shader')

from pymt.logger import pymt_logger
import numpy
import sys
#from ctypes import *
from OpenGL.GL import GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, \
        glCreateProgram, glGetUniformLocation, glUniform1i, \
        glUniform1f, glLinkProgram, glCreateShader, glUseProgram, \
        glAttachShader, glCompileShader, glShaderSource, \
        glGetProgramInfoLog, glGetShaderInfoLog, \
        glUniformMatrix4fv, glUniform1f, glUniform2f, glUniform3f, glUniform4f, \
        glGetAttribLocation
        


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
            pymt_logger.error('Shader: shader program message: %s' % message)
        else:
            pymt_logger.debug('Shader compiled sucessfully')

        self.set_default_attr_locations()


    def create_shader(self, source, shadertype):
        shader = glCreateShader(shadertype)
        # PyOpenGL bug ? He's waiting for a list of string, not a string
        # on some card, it failed :)
        if isinstance(source, basestring):
            source = [source]
        glShaderSource(shader, source)
        glCompileShader(shader)

        return shader



    def __setitem__(self, name, value):
        """pass a variable to the shader"""
        location = glGetUniformLocation(self.program, name)
        
        if type(value) == numpy.ndarray:
            mat_gl = numpy.ascontiguousarray(value.T, dtype='float32').flatten()
            glUniformMatrix4fv(location, 1, False, mat_gl)        
            return
        
        if type(value) == int:
            glUniform1i(location, value)
            return
        
        value = map(float, value)
        if len(value) == 1:
            glUniform1f(location, float(value))
        elif len(value) == 2:
            glUniform2f(location, *value)
        elif len(value) == 3:
            glUniform3f(location, *value)
        elif len(value) == 4:
            glUniform4f(location, *value)
        

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
    
    def set_default_attr_locations(self):
        self.attributes = {}
        self.use()
        for name in ['vPosition', 'vColor', 'vNormal', 'vTexCoords0', 'vTexCoords1', 'vTexCoords2', 'vTexCoords3']:
            self.attributes[name] = glGetAttribLocation(self.program, name)
            #print "attribute %s = %d" % (name, self.attributes[name])
        self.stop()

