'''
Geometric: module provide some class to handle 3D Mesh.
'''
__all__ = ['Material', 'MaterialGroup', 'Mesh']

import os
import warnings
from OpenGL.GL import *

class Material(object):
    '''
    Material class to handle attribute like light (ambient, diffuse, specular,
    emmission, shininess), opacity, texture...
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

    def apply(self, face=OpenGL.GL.GL_FRONT_AND_BACK):
        '''Apply the material on current context'''
        if self.texture:
            self.texture.enable()
            self.texture.bind()
            glEnable(GL_COLOR_MATERIAL)

        glMaterialfv(face, GL_DIFFUSE, self.diffuse + [self.opacity])
        glMaterialfv(face, GL_AMBIENT, self.ambient + [self.opacity])
        glMaterialfv(face, GL_SPECULAR, self.specular + [self.opacity])
        glMaterialfv(face, GL_EMISSION, self.emission + [self.opacity])
        glMaterialf(face, GL_SHININESS, self.shininess)
        glColorMaterial(face, GL_AMBIENT_AND_DIFFUSE)

    def unapply(self):
        if self.texture:
            self.texture.disable()
            glDisable(GL_COLOR_MATERIAL)

class MaterialGroup(object):
    '''
    Groups of material
    '''
    def __init__(self, material):
        self.material = material

        # Interleaved array of floats in GL_T2F_N3F_V3F format
        self.vertices = []
        self.array = None

class Mesh(object):
    '''
    Class to store a mesh in T2F_N3F_V3F format.
    '''
    def __init__(self, name):
        self.name = name
        self.groups = []

        # Display list, created only if compile() is called, but used
        # automatically by draw()
        self.list = None

    def draw(self):
        '''Draw the mesh on screen (using display list if compiled)'''
        if self.list:
            glCallList(self.list)
            return

        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        glPushAttrib(GL_CURRENT_BIT | GL_ENABLE_BIT | GL_LIGHTING_BIT)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        for group in self.groups:
            if group.material:
                group.material.apply()
            if group.array is None:
                if group.material and group.material.texture:
                    # We do that because we don't known if the texture
                    # is a NV|ARB_RECTANGLE. If yes, texture coordinate
                    # must be in 0-size, instead of 0-1.
                    group.vertices[0::8] = map(
                        lambda x: x * group.material.texture.width,
                        group.vertices[0::8]
                    )
                    group.vertices[1::8] = map(
                        lambda x: x * group.material.texture.height,
                        group.vertices[1::8]
                    )
                group.array = (GLfloat * len(group.vertices))(*group.vertices)
                group.triangles = len(group.vertices) / 8
            glInterleavedArrays(GL_T2F_N3F_V3F, 0, group.array)
            glDrawArrays(GL_TRIANGLES, 0, group.triangles)
            if group.material:
                group.material.unapply()
        glPopAttrib()
        glPopClientAttrib()

    def compile(self):
        '''Compile the mesh in display list'''
        if self.list:
            return
        list = glGenLists(1)
        glNewList(list, GL_COMPILE)
        self.draw()
        glEndList()
        self.list = list

