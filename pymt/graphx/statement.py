'''
Statements: OpenGL statement for the "with" keyword

Save and restore the matrix ::

    with gx_matrix:
        glTranslatef(55, 34, 0)
        # draw stuff
    # here, the matrix will be restored as previous state

Modify a display list (compiled OpenGL operations) ::

    dl = GlDisplayList()
    with dl:
        # draw stuff
    # here you can call the display list
    dl.draw()

Bind a texture and draw with OpenGL ::

    with DO(gx_texture(my_texture), gx_begin(GL_TRIANGLE_FAN)):
        # call multiple time glVertex2f()

Save and restore the color after drawing ::

    set_color(1, 0, 0) # color is red.
    with gx_color(0, 1, 0):
        # here the color is green
        # draw stuff
        pass
    # here the color is restored back to red
'''

__all__ = (
    # class for with statement
    'DO',
    'GlDisplayList', 'GlBlending',
    'GlMatrix', 'GlEnable', 'GlBegin',
    'GlAttrib', 'GlColor', 'GlTexture',
    # aliases
    'gx_blending', 'gx_alphablending',
    'gx_matrix', 'gx_matrix_identity',
    'gx_enable', 'gx_begin',
    'gx_attrib', 'gx_color',
    'gx_texture', 'gx_blending_replace'
)

import pymt
from OpenGL.GL import GL_COMPILE, GL_COMPILE_AND_EXECUTE, \
        GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_BLEND, GL_MODELVIEW, \
        GL_COLOR_BUFFER_BIT, GL_ENABLE_BIT, GL_TEXTURE_2D, GL_DST_COLOR, \
        GL_ONE, GL_ZERO, \
        glEnable, glDisable, glGenLists, glNewList, glEndList, glCallList, \
        glBlendFunc, glMatrixMode, glPushMatrix, glLoadIdentity, glPopAttrib, \
        glPushMatrix, glPopAttrib, glColor3f, glColor4f, glBindTexture, \
        glPopMatrix, glBegin, glEnd, glPushAttrib

gl_displaylist_generate = False
class GlDisplayList:
    '''Abstraction to opengl display-list usage. Here is an example of usage
    ::

        dl = GlDisplayList()
        with dl:
            # do draw function, like drawLabel etc...
        dl.draw()


    :Parameters:
        `mode` : str, default to 'compile'
            If mode is 'execute', the code in with will be also compiled + executed.
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('mode', 'compile')
        self.dl = glGenLists(1)
        self.compiled = False
        self.do_compile = True
        self.mode = GL_COMPILE
        if 'execute' in kwargs.get('mode'):
            self.mode = GL_COMPILE_AND_EXECUTE

    def __enter__(self):
        self.start()

    def __exit__(self, extype, value, traceback):
        self.stop()

    def start(self):
        '''Start recording GL operation'''
        global gl_displaylist_generate
        if gl_displaylist_generate:
            self.do_compile = False
        else:
            gl_displaylist_generate = True
            self.do_compile = True
            glNewList(self.dl, self.mode)

    def stop(self):
        '''Stop recording GL operation'''
        global gl_displaylist_generate
        if self.do_compile:
            glEndList()
            self.compiled = True
            gl_displaylist_generate = False

    def clear(self):
        '''Clear compiled flag'''
        self.compiled = False

    def is_compiled(self):
        '''Return compiled flag'''
        return self.compiled

    def draw(self):
        '''Call the list only if it's compiled'''
        if not self.compiled:
            return
        glCallList(self.dl)

class DO:
    '''A way to do multiple action in with statement
    ::

        with DO(stmt1, stmt2):
            print 'something'

    '''
    def __init__(self, *args):
        self.args = args

    def __enter__(self):
        for item in self.args:
            item.__enter__()

    def __exit__(self, extype, value, traceback):
        for item in reversed(self.args):
            item.__exit__(extype, value, traceback)


class GlBlending:
    '''Abstraction to use blending ! Don't use directly this class.
    We've got an alias you can use ::

        with gx_blending:
            # do draw function
    '''
    def __init__(self, sfactor=GL_SRC_ALPHA, dfactor=GL_ONE_MINUS_SRC_ALPHA):
        self.sfactor = sfactor
        self.dfactor = dfactor

    def __enter__(self):
        glEnable(GL_BLEND)
        glBlendFunc(self.sfactor, self.dfactor)

    def __exit__(self, extype, value, traceback):
        glDisable(GL_BLEND)

class GlMatrix:
    '''Statement of glPushMatrix/glPopMatrix, designed to be use with
    "with" keyword.

    Alias: gx_matrix, gx_matrix_identity ::

        with gx_matrix:
            # do draw function

        with gx_matrix_identity:
            # do draw function
    '''
    def __init__(self, matrixmode=GL_MODELVIEW, do_loadidentity=False):
        self.do_loadidentity = do_loadidentity
        self.matrixmode = matrixmode

    def __enter__(self):
        glMatrixMode(self.matrixmode)
        glPushMatrix()
        if self.do_loadidentity:
            glLoadIdentity()

    def __exit__(self, extype, value, traceback):
        glMatrixMode(self.matrixmode)
        glPopMatrix()

class GlEnable:
    '''Statement of glEnable/glDisable, designed to be use with "with" keyword.

    Alias: gx_enable.
    '''
    def __init__(self, flag):
        self.flag = flag

    def __enter__(self):
        glEnable(self.flag)

    def __exit__(self, extype, value, traceback):
        glDisable(self.flag)

gx_enable = GlEnable

class GlBegin:
    '''Statement of glBegin/glEnd, designed to be use with "with" keyword

    Alias: gx_begin.
    '''
    def __init__(self, flag):
        self.flag = flag

    def __enter__(self):
        glBegin(self.flag)

    def __exit__(self, extype, value, traceback):
        glEnd()

class GlAttrib:
    '''Statement of glPushAttrib/glPopAttrib, designed to be use with
    "with" keyword

    Alias: gx_attrib.
    '''
    def __init__(self, flag):
        self.flag = flag

    def __enter__(self):
        glPushAttrib(self.flag)

    def __exit__(self, extype, value, traceback):
        glPopAttrib()

class GlColor:
    '''Statement of glPushAttrib/glPopAttrib on COLOR BUFFER + color,
    designed to be use with "with" keyword

    Alias: gx_color.
    '''
    def __init__(self, r, g, b, a=None):
        if a is None:
            self.color = (r, g, b)
        else:
            self.color = (r, g, b, a)

    def __enter__(self):
        glPushAttrib(GL_COLOR_BUFFER_BIT)
        if len(self.color) == 3:
            glColor3f(*self.color)
        else:
            glColor4f(*self.color)

    def __exit__(self, extype, value, traceback):
        glPopAttrib()

class GlTexture:
    '''Statement of setting a texture

    Alias: gx_texture.
    '''
    def __init__(self, texture):
        self.texture = texture

    def __enter__(self):
        self.bind()

    def __exit__(self, extype, value, traceback):
        self.release()

    def bind(self):
        '''Bind the texture on the current context / texture unit'''
        target = self.get_target()
        glPushAttrib(GL_ENABLE_BIT)
        glEnable(target)
        glBindTexture(target, self.get_id())

    def release(self):
        '''Release the current attribute from the binded texture'''
        glPopAttrib()

    def get_id(self):
        '''Return the GL id of texture'''
        if isinstance(self.texture, pymt.TextureRegion):
            return self.texture.owner.id
        elif isinstance(self.texture, pymt.Texture):
            return self.texture.id
        else:
            return self.texture

    def get_target(self):
        '''Get the GL target of the texture'''
        if isinstance(self.texture, pymt.TextureRegion):
            return self.texture.owner.target
        elif isinstance(self.texture, pymt.Texture):
            return self.texture.target
        else:
            return GL_TEXTURE_2D

#
# Aliases
#

#: Alias to GlBlending(sfactor=GL_DST_COLOR, dfactor=GL_ONE_MINUS_SRC_ALPHA)
gx_alphablending = GlBlending(sfactor=GL_DST_COLOR,
                              dfactor=GL_ONE_MINUS_SRC_ALPHA)
#: Repalce the content with the source content
gx_blending_replace = GlBlending(sfactor=GL_ONE, dfactor=GL_ZERO)
#: Alias to GlAttrib
gx_attrib = GlAttrib
#: Alias to GlBegin
gx_begin = GlBegin
#: Alias to GlBlending()
gx_blending = GlBlending()
#: Alias to GlColor
gx_color = GlColor
#: Alias to GlMatrix()
gx_matrix = GlMatrix()
#: Alias to GlMatrix(do_loadidentity=True)
gx_matrix_identity = GlMatrix(do_loadidentity=True)
#: Alias to GlTexture
gx_texture = GlTexture

