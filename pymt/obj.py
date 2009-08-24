'''
Obj: handle 3D mesh
'''
__all__ = ['OBJ']

import os

from . import pymt_logger
from pyglet import image
from geometric import Material, MaterialGroup, Mesh

class OBJ:
    '''3D object representation.

    :Parameters:
        `filename` : string
            Filename of object
        `fd` : Fd object, default to None
            Use fd instead of filename if possible
        `path` : string, default to None
            Use custom path for material
    '''
    def __init__(self, filename, fd=None, path=None):
        self.materials  = {}
        self.meshes     = {}     # Name mapping
        self.mesh_list  = []     # Also includes anonymous meshes

        if fd is None:
            fd = open(filename, 'r')

        if path is None:
            path = os.path.dirname(filename)
            self.path = path

        mesh = None
        group = None
        material = None

        vertices = [[0., 0., 0.]]
        normals = [[0., 0., 0.]]
        tex_coords = [[0., 0.]]

        for line in fd:
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
                    pymt_logger.warning('Unknown material: %s' % values[1])
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
                v1      = None
                vlast   = None
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
        fd = self.open_material_file(filename)

        for line in fd:
            if line.startswith('#'):
                continue
            values = line.split()
            if not values:
                continue

            if values[0] == 'newmtl':
                material = Material(values[1])
                self.materials[material.name] = material
            elif material is None:
                pymt_logger.warning('Expected "newmtl" in %s' % filename)
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
                        material.texture = image.load(values[1]).texture
                    except Exception:
                        pymt_logger.exception('Could not load texture')
            except Exception:
                pymt_logger.exception('Parse error in %s.' % filename)
        fd.close()

    def draw(self):
        '''Draw the object on screen'''
        for mesh in self.mesh_list:
            mesh.draw()

