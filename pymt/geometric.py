'''
Geometric module provide some class to handle 3D Mesh.
'''
__all__ = ['Material', 'MaterialGroup', 'Mesh']

import os
import warnings
import pyglet
from pyglet.gl import *

class Material(object):
    '''
    This is the material class
    '''
    diffuse = [.8, .8, .8]
    ambient = [.2, .2, .2]
    specular = [0., 0., 0.]
    emission = [0., 0., 0.]
    shininess = 0.
    opacity = 1.
    texture = None

    def __init__(self, name):
        self.name = name

    def apply(self, face=pyglet.gl.GL_FRONT_AND_BACK):
        if self.texture:
            glEnable(self.texture.target)
            glBindTexture(self.texture.target, self.texture.id)
        else:
            glDisable(GL_TEXTURE_2D)

        glMaterialfv(face, GL_DIFFUSE,
                     (GLfloat * 4)(*(self.diffuse + [self.opacity])))
        glMaterialfv(face, GL_AMBIENT,
                     (GLfloat * 4)(*(self.ambient + [self.opacity])))
        glMaterialfv(face, GL_SPECULAR,
                     (GLfloat * 4)(*(self.specular + [self.opacity])))
        glMaterialfv(face, GL_EMISSION,
                     (GLfloat * 4)(*(self.emission + [self.opacity])))
        glMaterialf(face, GL_SHININESS, self.shininess)

class MaterialGroup(object):
    def __init__(self, material):
        self.material = material

        # Interleaved array of floats in GL_T2F_N3F_V3F format
        self.vertices = []
        self.array = None

class Mesh(object):
    def __init__(self, name):
        self.name = name
        self.groups = []

        # Display list, created only if compile() is called, but used
        # automatically by draw()
        self.list = None

    def draw(self):
        if self.list:
            glCallList(self.list)
            return

        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        glPushAttrib(GL_CURRENT_BIT | GL_ENABLE_BIT | GL_LIGHTING_BIT)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        for group in self.groups:
            if group.array is None:
                group.array = (GLfloat * len(group.vertices))(*group.vertices)
                group.triangles = len(group.vertices) / 8
            glInterleavedArrays(GL_T2F_N3F_V3F, 0, group.array)
            glDrawArrays(GL_TRIANGLES, 0, group.triangles)
        glPopAttrib()
        glPopClientAttrib()

    def compile(self):
        if self.list:
            return
        list = glGenLists(1)
        glNewList(list, GL_COMPILE)
        self.draw()
        glEndList()
        self.list = list

