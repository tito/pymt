'''
Obj: handle 3D mesh
'''
__all__ = ['OBJ']

import os
import warnings
import pymt

from OpenGL.GL import *
from graphx import *
from geometric import *

class OBJ:
    '''3D object representation.

    :Parameters:
        `filename` : string
            Filename of object
        `file` : File object, default to None
            Use file instead of filename if possible
        `path` : string, default to None
            Use custom path for material
        `compat` : bool, default to True
            Set to False if you want to take care yourself of the lights, depth
            test, color...
    '''
    def __init__(self, filename, file=None, path=None, compat=True):
        self.materials = {}
        self.meshes = {}        # Name mapping
        self.mesh_list = []     # Also includes anonymous meshes
        self.compat = compat

        if file is None:
            file = open(filename, 'r')

        if path is None:
            path = os.path.dirname(filename)
            self.path = path

        mesh = None
        group = None
        material = None

        vertices = [[0., 0., 0.]]
        normals = [[0., 0., 0.]]
        tex_coords = [[0., 0.]]

        for line in open(filename, 'r'):
            if line.startswith('#'):
                continue
            values = line.split()
            if not values:
                continue

            if values[0] == 'v':
                vertices.append(map(float, values[1:4]))
            elif values[0] == 'vn':
                normals.append(map(float, values[1:4]))
            elif values[0] == 'vt':
                tex_coords.append(map(float, values[1:3]))
            elif values[0] == 'mtllib':
                self.load_material_library(values[1])
            elif values[0] in ('usemtl', 'usemat'):
                material = self.materials.get(values[1], None)
                if material is None:
                    warnings.warn('Unknown material: %s' % values[1])
                if mesh is not None:
                    group = MaterialGroup(material)
                    mesh.groups.append(group)
            elif values[0] == 'o':
                mesh = Mesh(values[1])
                self.meshes[mesh.name] = mesh
                self.mesh_list.append(mesh)
                group = None
            elif values[0] == 'f':
                if mesh is None:
                    mesh = Mesh('')
                    self.mesh_list.append(mesh)
                if material is None:
                    material = Material('')
                if group is None:
                    group = MaterialGroup(material)
                    mesh.groups.append(group)

                # For fan triangulation, remember first and latest vertices
                v1 = None
                vlast = None
                points = []
                for i, v in enumerate(values[1:]):
                    v_index, t_index, n_index = \
                            (map(int, [j or 0 for j in v.split('/')]) + [0, 0])[:3]
                    if v_index < 0:
                        v_index += len(vertices) - 1
                    if t_index < 0:
                        t_index += len(tex_coords) - 1
                    if n_index < 0:
                        n_index += len(normals) - 1
                    vertex = tex_coords[t_index] + \
                            normals[n_index] + \
                            vertices[v_index]

                    if i >= 3:
                        # Triangulate
                        group.vertices += v1 + vlast
                    group.vertices += vertex

                    if i == 0:
                        v1 = vertex
                    vlast = vertex

    def open_material_file(self, filename):
        '''Override for loading from archive/network etc.'''
        return open(os.path.join(self.path, filename), 'r')

    def load_material_library(self, filename):
        material = None
        file = self.open_material_file(filename)

        for line in file:
            if line.startswith('#'):
                continue
            values = line.split()
            if not values:
                continue

            if values[0] == 'newmtl':
                material = Material(values[1])
                self.materials[material.name] = material
            elif material is None:
                warnings.warn('Expected "newmtl" in %s' % filename)
                continue

            try:
                if values[0] == 'Kd':
                    material.diffuse = map(float, values[1:])
                elif values[0] == 'Ka':
                    material.ambient = map(float, values[1:])
                elif values[0] == 'Ks':
                    material.specular = map(float, values[1:])
                elif values[0] == 'Ke':
                    material.emissive = map(float, values[1:])
                elif values[0] == 'Ns':
                    material.shininess = float(values[1])
                elif values[0] == 'd':
                    material.opacity = float(values[1])
                elif values[0] == 'map_Kd':
                    try:
                        filename = ' '.join(values[1:])
                        material.texture = pymt.Image(filename).texture
                        material.wrap = GL_REPEAT
                    except:
                        warnings.warn('Could not load texture %s' % values[1])
                        raise
            except:
                warnings.warn('Parse error in %s.' % filename)
                raise

    def enter(self):
        if not self.compat:
            return
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0,0,0,1))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (.8,.8,.8,1))
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (.9,.9,.9))
        glLightModelfv(GL_LIGHT_MODEL_LOCAL_VIEWER, 0)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_DEPTH_TEST)
        glColor3f(1, 1, 1)

    def leave(self):
        if not self.compat:
            return
        glDisable(GL_LIGHTING)
        glDisable(GL_LIGHT0)
        glDisable(GL_COLOR_MATERIAL)
        glDisable(GL_DEPTH_TEST)

    def draw(self):
        '''Draw the object on screen'''
        self.enter()
        for mesh in self.mesh_list:
            mesh.draw()
        self.leave()

