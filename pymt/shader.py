import ctypes as c
from pyglet import *

class ShaderException(Exception):
    pass

class Shader(object):

    def __init__(self, vertex_source=None, fragment_source=None):
        self.program = gl.glCreateProgram()
        
        if vertex_source:
            self.vertex_shader = self.create_shader(vertex_source,gl.GL_VERTEX_SHADER)
            gl.glAttachShader(self.program, self.vertex_shader)
        
        if fragment_source:
            self.fragment_shader = self.create_shader(fragment_source,gl.GL_FRAGMENT_SHADER)
            gl.glAttachShader(self.program, self.fragment_shader)
            
        gl.glLinkProgram(self.program)
        message = self.get_program_log(self.program)
        if message:
            raise ShaderException(message)

    def create_shader(self, source, shadertype):
        sbuffer = c.create_string_buffer(source)
        pointer = c.cast(c.pointer(c.pointer(sbuffer)),
                c.POINTER(c.POINTER(c.c_char)))
        nulll = c.POINTER(c.c_long)()
        shader = gl.glCreateShader(shadertype)
        gl.glShaderSource(shader, 1, pointer, None)
        gl.glCompileShader(shader)
        message = self.get_shader_log(shader)
        if message:
            raise ShaderException(message)
        return shader

    def set_uniform_f(self, name, value):
        location = gl.glGetUniformLocation(self.program, name)
        gl.glUniform1f(location, value)

    def __setitem__(self, name, value):
        """pass a variable to the shader"""
        if isinstance(value, float):
            self.set_uniform_f(name, value)
        else:
            raise TypeError("Only floats are supported so far")

    def use(self):
        gl.glUseProgram(self.program)

    def stop(self):
        gl.glUseProgram(0)

    def get_shader_log(self, shader):
        return self.get_log(shader, gl.glGetShaderInfoLog)

    def get_program_log(self, shader):
        return self.get_log(shader, gl.glGetProgramInfoLog)

    def get_log(self, obj, func):
        log_buffer = c.create_string_buffer(4096)
        buffer_pointer = c.cast(c.pointer(log_buffer), c.POINTER(c.c_char))
        written = c.c_int()
        func(obj, 4096, c.pointer(written), buffer_pointer)
        return log_buffer.value