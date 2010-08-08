'''
Fbo: abstraction to use hardware/software FrameBuffer object
'''

__all__ = (
    'Fbo', 'HardwareFbo', 'SoftwareFbo',
    'UnsupportedFboException'
)

import os
import re
import OpenGL
import pymt
from OpenGL.GL import GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, \
        GL_VIEWPORT_BIT, GL_TEXTURE_2D, GL_COLOR_ATTACHMENT0_EXT, \
        GL_RENDERBUFFER_EXT, GL_DEPTH_COMPONENT, GL_DEPTH_ATTACHMENT_EXT, \
        GL_BACK, GL_RGBA, GL_UNSIGNED_BYTE, GL_STENCIL_TEST, \
        GL_STENCIL_BUFFER_BIT, \
        glClear, glClearColor, glPushAttrib, glPopAttrib, \
        glViewport, glReadBuffer, glReadPixels, glCopyTexSubImage2D, \
        glDrawPixels, glDisable
from OpenGL.GL.EXT.framebuffer_object import GL_FRAMEBUFFER_EXT, \
        GL_FRAMEBUFFER_COMPLETE_EXT, GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT_EXT, \
        GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT_EXT, \
        GL_FRAMEBUFFER_UNSUPPORTED_EXT, \
        GL_FRAMEBUFFER_INCOMPLETE_DIMENSIONS_EXT, \
        GL_FRAMEBUFFER_INCOMPLETE_FORMATS_EXT, \
        GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER_EXT, \
        GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER_EXT, \
        glGenFramebuffersEXT, glGenRenderbuffersEXT, \
        glBindFramebufferEXT, glBindRenderbufferEXT, \
        glDeleteRenderbuffersEXT, glDeleteFramebuffersEXT, \
        glCheckFramebufferStatusEXT, glFramebufferRenderbufferEXT, \
        glRenderbufferStorageEXT, glFramebufferTexture2DEXT
from pymt.graphx.colors import set_color
from pymt.graphx.draw import drawTexturedRectangle, set_texture, get_texture_id

# for a specific bug in 3.0.0, about deletion of framebuffer.
OpenGLversion = tuple(int(re.match('^(\d+)', i).groups()[0]) for i in OpenGL.__version__.split('.'))
try:
    import numpy
    have_numpy = True
except ImportError:
    have_numpy = False


class UnsupportedFboException(Exception):
    pass

class AbstractFbo(object):
    '''Abstraction of Framebuffer implementation.
    It's a framebuffer you can use to draw temporary things,
    and use it as a texture.

    .. note::
        You cannot use this class, use Fbo alias.

    .. warning::
        Depend of implementation, texture can be a TextureRegion, or a long.

    :Parameters:
        `clear_color` : tuple, default to (0, 0, 0, 0)
            Color to apply when clearing the texture
        `size` : tuple, default to (1024, 1024)
            Size of FBO
        `push_viewport` : bool, default to False
            Indicate if viewport must be pushed
        `with_depthbuffer` : bool, default to True
            Indicate if depthbuffer must be applied
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('clear_color', (0, 0, 0, 0))
        kwargs.setdefault('size', (1024, 1024))
        kwargs.setdefault('push_viewport', False)
        kwargs.setdefault('with_depthbuffer', True)

        self.clear_color        = kwargs.get('clear_color')
        self.size               = kwargs.get('size')
        self.with_depthbuffer   = kwargs.get('with_depthbuffer')
        self.push_viewport      = kwargs.get('push_viewport')
        self._is_bind           = False

        # create texture
        self.texture            = pymt.Texture.create(self.size[0], self.size[1])

        # get real size (can be the same)
        if isinstance(self.texture, pymt.TextureRegion):
            self.realsize = self.texture.owner.width, self.texture.owner.height
        elif isinstance(self.texture, pymt.Texture):
            self.realsize = self.texture.width, self.texture.height
        else:
            raise 'Unknown type(self.texture). Please send a bug report on pymt dev.'

    def bind(self):
        '''Activate writing on Framebuffer. All next call will be done on it.'''
        self._is_bind = True

    def release(self):
        '''Deactivate writing on Framebuffer. Back to normal mode.'''
        self._is_bind = False

    def clear(self):
        '''Clear framebuffer.

        .. warning::
            Must be called inside bind()/release() of FBO !
        '''
        assert(self._is_bind == True)

        glClearColor(*self.clear_color)
        if self.with_depthbuffer:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        else:
            glClear(GL_COLOR_BUFFER_BIT)

    def __enter__(self):
        self.bind()

    def __exit__(self, type, value, traceback):
        self.release()


class HardwareFbo(AbstractFbo):
    '''OpenGL Framebuffer, hardware implementation.

    .. warning::
        It's not supported by all hardware, use with care !

    '''
    fbo_stack = [0]

    gl_fbo_errors = {
        GL_FRAMEBUFFER_COMPLETE_EXT:
            'Framebuffer complete.',
        GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT_EXT:
            'Framebuffer incomplete: Attachment is NOT complete.',
        GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT_EXT:
            'Framebuffer incomplete: No image is attached to FBO.',
        GL_FRAMEBUFFER_INCOMPLETE_DIMENSIONS_EXT:
            'Framebuffer incomplete: Attached images have different dimensions.',
        GL_FRAMEBUFFER_INCOMPLETE_FORMATS_EXT:
            'Framebuffer incomplete: Color attached images have different internal formats.',
        GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER_EXT:
            'Framebuffer incomplete: Draw buffer.',
        GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER_EXT:
            'Framebuffer incomplete: Read buffer.',
        GL_FRAMEBUFFER_UNSUPPORTED_EXT:
            'Unsupported by FBO implementation.',
    }

    def __init__(self, **kwargs):
        super(HardwareFbo, self).__init__(**kwargs)
        self.framebuffer    = None
        self.depthbuffer    = None

        set_texture(self.texture)

        self.framebuffer = glGenFramebuffersEXT(1)
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, self.framebuffer)
        if self.framebuffer == 0:
            raise 'Failed to initialize framebuffer'

        if self.with_depthbuffer:
            self.depthbuffer = glGenRenderbuffersEXT(1)
            glBindRenderbufferEXT(GL_RENDERBUFFER_EXT, self.depthbuffer)
            glRenderbufferStorageEXT(GL_RENDERBUFFER_EXT, GL_DEPTH_COMPONENT,
                                     self.realsize[0], self.realsize[1])
            glBindRenderbufferEXT(GL_RENDERBUFFER_EXT, 0)
            glFramebufferRenderbufferEXT(GL_FRAMEBUFFER_EXT, GL_DEPTH_ATTACHMENT_EXT,
                                         GL_RENDERBUFFER_EXT, self.depthbuffer)

        glFramebufferTexture2DEXT(GL_FRAMEBUFFER_EXT, GL_COLOR_ATTACHMENT0_EXT,
                GL_TEXTURE_2D, get_texture_id(self.texture), 0)

        # check the fbo status
        status = glCheckFramebufferStatusEXT(GL_FRAMEBUFFER_EXT)
        if status != GL_FRAMEBUFFER_COMPLETE_EXT:
            pymt.pymt_logger.error('Fbo: Error in framebuffer activation')
            pymt.pymt_logger.error('Fbo: Details: HardwareFbo size=%s, realsize=%s, format=GL_RGBA' % (
                str(self.size), str(self.realsize)))
            if status in HardwareFbo.gl_fbo_errors:
                pymt.pymt_logger.error('Fbo: Details: %s (%d)' % (HardwareFbo.gl_fbo_errors[status], status))
            else:
                pymt.pymt_logger.error('Fbo: Details: Unknown error (%d)' % status)

            pymt.pymt_logger.error('Fbo: ')
            pymt.pymt_logger.error('Fbo: You cannot use Hardware FBO.')
            pymt.pymt_logger.error('Fbo: Please change the configuration to use Software FBO.')
            pymt.pymt_logger.error('Fbo: You can use the pymt-config tools, or edit the configuration to set:')
            pymt.pymt_logger.error('Fbo: ')
            pymt.pymt_logger.error('Fbo: [graphics]')
            pymt.pymt_logger.error('Fbo: fbo = software')
            pymt.pymt_logger.error('Fbo: ')

            raise UnsupportedFboException()

        # unbind framebuffer
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0)

    def __del__(self):
        # if application is closed, symbol may be not available anymore
        # so, prevent failure, instead of having an exception !
        if not bool(glDeleteRenderbuffersEXT):
            return
        # XXX deletion of framebuffer failed with PyOpenGL 3.0.0
        # Closed bug : http://sourceforge.net/tracker/index.php?func=detail&aid=2727274&group_id=5988&atid=105988
        # So, we must test the version, and use numpy array instead.
        if OpenGLversion <= (3, 0, 1) and have_numpy:
            glDeleteFramebuffersEXT(1, numpy.array(self.framebuffer))
            if self.with_depthbuffer:
                glDeleteRenderbuffersEXT(1, numpy.array(self.depthbuffer))
        else:
            # XXX Should work, but not tested.
            glDeleteFramebuffersEXT(1, self.framebuffer)
            if self.with_depthbuffer:
                glDeleteRenderbuffersEXT(1, self.depthbuffer)

    def bind(self):
        super(HardwareFbo, self).bind()
        HardwareFbo.fbo_stack.append(self.framebuffer)
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, self.framebuffer)
        if self.push_viewport:
            glPushAttrib(GL_VIEWPORT_BIT)
            glViewport(0, 0, self.size[0], self.size[1])

    def release(self):
        if self.push_viewport:
            glPopAttrib()
        HardwareFbo.fbo_stack.pop()
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, HardwareFbo.fbo_stack[-1])
        super(HardwareFbo, self).release()


class SoftwareFbo(AbstractFbo):
    '''OpenGL Framebuffer, software implementation.

    .. warning::
        Poor performance, but you can use it in hardware don't support real
        Fbo extensions...

    '''
    def __init__(self, **kwargs):
        super(SoftwareFbo, self).__init__(**kwargs)
        self.pixels = None

    def bind(self):
        super(SoftwareFbo, self).bind()

        # Save current buffer
        w = pymt.getWindow()
        glReadBuffer(GL_BACK)
        self.pixels = glReadPixels(0, 0, w.width, w.height, GL_RGBA, GL_UNSIGNED_BYTE)

        # Push current attrib
        glPushAttrib(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_TEST | GL_STENCIL_BUFFER_BIT)
        glDisable(GL_STENCIL_TEST)

        # Save viewport if asked
        if self.push_viewport:
            glPushAttrib(GL_VIEWPORT_BIT)
            glViewport(0, 0, self.size[0], self.size[1])

        # Draw old Framebuffer
        set_color(1, 1, 1)
        drawTexturedRectangle(self.texture, size=self.size)

        # Slower solution, but no alpha problem
        #set_texture(self.texture)
        #pixels = glGetTexImage(self.texture.target, 0, GL_RGBA, GL_UNSIGNED_BYTE)
        #glDrawPixels(self.realsize[0], self.realsize[1], GL_RGBA, GL_UNSIGNED_BYTE, pixels)

    def release(self):
        # Restore viewport
        if self.push_viewport:
            glPopAttrib()

        # Copy current buffer into fbo texture
        set_texture(self.texture, target=GL_TEXTURE_2D)
        glReadBuffer(GL_BACK)
        glCopyTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, 0, 0, self.size[0], self.size[1])

        # Restore old buffer
        w = pymt.getWindow()
        glDrawPixels(w.width, w.height, GL_RGBA, GL_UNSIGNED_BYTE, self.pixels)

        glPopAttrib()

        super(SoftwareFbo, self).release()

class AutoselectFbo(object):
    fbo_class = None
    def __new__(cls, *largs, **kwargs):
        return AutoselectFbo.fbo_class(*largs, **kwargs)

#: Fbo wrapper to the best FBO available on system
Fbo = AutoselectFbo

if 'PYMT_DOC' not in os.environ:

    def __pymt_configure_fbo():

        from pymt import pymt_config

        # decide what to use
        fbo_config = pymt_config.get('graphics', 'fbo')

        if fbo_config == 'force-hardware':
            pymt.pymt_logger.debug('Fbo: Forcing hardware Framebuffer')
            AutoselectFbo.fbo_class = HardwareFbo
        elif fbo_config == 'hardware' and bool(glGenFramebuffersEXT):
            pymt.pymt_logger.debug('Fbo: Use hardware Framebuffer')
            AutoselectFbo.fbo_class = HardwareFbo
        elif fbo_config == 'software':
            pymt.pymt_logger.debug('Fbo: Use software Framebuffer')
            AutoselectFbo.fbo_class = SoftwareFbo
        else:
            pymt_config.set('graphics', 'fbo', 'software')
            pymt.pymt_logger.debug('Fbo: Falling back to software Framebuffer!!')
            AutoselectFbo.fbo_class = SoftwareFbo

    from pymt import pymt_register_post_configuration
    pymt_register_post_configuration(__pymt_configure_fbo)
