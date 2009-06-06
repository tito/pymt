'''
Fbo: abstraction to use hardware/software FrameBuffer object
'''

from __future__ import with_statement

__all__ = [
    'Fbo', 'HardwareFbo', 'SoftwareFbo'
]

from pyglet import *
from pyglet.gl import *
from pyglet.image import Texture, TextureRegion
from paint import *
from ..logger import pymt_logger

class AbstractFbo(object):
    '''Abstraction of Framebuffer implementation.
    It's a framebuffer you can use to draw temporary things,
    and use it as a texture.

    .. note::
        You cannot use this class, use Fbo alias.

    .. warning::
        Depend of implementation, texture can be a TextureRegion, or a long.

    :Parameters:
        `size` : tuple, default to (1024, 1024)
            Size of FBO
        `push_viewport` : bool, default to False
            Indicate if viewport must be pushed
        `with_depthbuffer` : bool, default to True
            Indicate if depthbuffer must be applied
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('size', (1024, 1024))
        kwargs.setdefault('push_viewport', False)
        kwargs.setdefault('with_depthbuffer', True)
        self.size               = kwargs.get('size')
        self.with_depthbuffer   = kwargs.get('with_depthbuffer')
        self.push_viewport      = kwargs.get('push_viewport')

        # create texture
        self.texture            = Texture.create(self.size[0], self.size[1])

        # get real size (can be the same)
        if isinstance(self.texture, TextureRegion):
            self.realsize = self.texture.owner.width, self.texture.owner.height
        elif isinstance(self.texture, Texture):
            self.realsize = self.texture.width, self.texture.height
        else:
            raise 'Unknown type(self.texture). Please send a bug report on pymt dev.'

    def bind(self):
        pass

    def release(self):
        pass

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

    def __init__(self, **kwargs):
        super(HardwareFbo, self).__init__(**kwargs)
        self.framebuffer    = c_uint(0)
        self.depthbuffer    = c_uint(0)

        glGenFramebuffersEXT(1, byref(self.framebuffer))
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, self.framebuffer)
        if self.framebuffer.value == 0:
            raise 'Failed to initialize framebuffer'

        if self.with_depthbuffer:
            glGenRenderbuffersEXT(1, byref(self.depthbuffer));
            glBindRenderbufferEXT(GL_RENDERBUFFER_EXT, self.depthbuffer)
            glRenderbufferStorageEXT(GL_RENDERBUFFER_EXT, GL_DEPTH_COMPONENT,
                                     self.realsize[0], self.realsize[1])
            glFramebufferRenderbufferEXT(GL_FRAMEBUFFER_EXT, GL_DEPTH_ATTACHMENT_EXT, GL_RENDERBUFFER_EXT, self.depthbuffer)

        set_texture(self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.realsize[0], self.realsize[1],
                0, GL_RGB, GL_UNSIGNED_BYTE, 0)
        glFramebufferTexture2DEXT(GL_FRAMEBUFFER_EXT, GL_COLOR_ATTACHMENT0_EXT,
                GL_TEXTURE_2D, get_texture_id(self.texture), 0)
        glBindRenderbufferEXT(GL_RENDERBUFFER_EXT, 0)
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0)

        status = glCheckFramebufferStatusEXT(GL_FRAMEBUFFER_EXT);
        if status != GL_FRAMEBUFFER_COMPLETE_EXT:
            pymt_logger.error('error in framebuffer activation')

    def __del__(self):
        glDeleteFramebuffersEXT(1, byref(self.framebuffer))
        if self.with_depthbuffer:
            glDeleteRenderbuffersEXT(1, byref(self.depthbuffer))

    def bind(self):
        Fbo.fbo_stack.append(self.framebuffer)
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, self.framebuffer)
        if self.push_viewport:
            glPushAttrib(GL_VIEWPORT_BIT)
            glViewport(0, 0, self.size[0], self.size[1])

    def release(self):
        if self.push_viewport:
            glPopAttrib()
        Fbo.fbo_stack.pop()
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, Fbo.fbo_stack[-1])


class SoftwareFbo(AbstractFbo):
    '''OpenGL Framebuffer, software implementation.

    .. warning::
        Poor performance, but you can use it in hardware don't support real
        Fbo extensions...

    '''
    def __init__(self, **kwargs):
        super(SoftwareFbo, self).__init__(**kwargs)
        self.oldtexture = pyglet.image.get_buffer_manager().get_color_buffer().get_texture()

        # Hack to initialize a empty buffer.
        self.bind()
        self.release()


    def bind(self):

        # Save current buffer
        buffer = pyglet.image.get_buffer_manager().get_color_buffer()
        set_texture(self.oldtexture, target=GL_TEXTURE_2D)
        buffer.blit_to_texture(GL_TEXTURE_2D, 0, 0, 0, 0)

        # Push current attrib
        glPushAttrib(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_TEST | GL_STENCIL_BUFFER_BIT)
        glClearColor(0,0,0,0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDisable(GL_STENCIL_TEST)

        # Save viewport if asked
        if self.push_viewport:
            glPushAttrib(GL_VIEWPORT_BIT)
            glViewport(0, 0, self.size[0], self.size[1])

        # Draw old Framebuffer
        set_color(1,1,1)
        drawTexturedRectangle(self.texture, size=self.size)

    def release(self):
        # Restore viewport
        if self.push_viewport:
            glPopAttrib()

        # Copy current buffer into fbo texture
        set_texture(self.texture, target=GL_TEXTURE_2D);
        buffer = pyglet.image.get_buffer_manager().get_color_buffer()
        glReadBuffer(buffer.gl_buffer)
        glCopyTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, 0, 0, self.size[0], self.size[1])

        # Restore old buffer
        glPushMatrix()
        glLoadIdentity()
        set_color(1,1,1)
        drawTexturedRectangle(self.oldtexture, size=(self.oldtexture.width,
                                                     self.oldtexture.height))
        glPopMatrix()

        glPopAttrib()


if os.path.basename(sys.argv[0]).startswith('sphinx'):
    # Bad hack for sphinx
    # He don't like when Fbo is announced in __all__,
    # and not defined in source
    Fbo = HardwareFbo
else:
    from .. import pymt_config
    # Check if Fbo is supported by gl
    if not 'GL_EXT_framebuffer_object' in gl_info.get_extensions():
        pymt_config.set('graphics', 'fbo', 'software')

    if not os.path.basename(sys.argv[0]).startswith('sphinx'):
        # decide what to use
        if pymt_config.get('graphics', 'fbo') == 'hardware':
            pymt_logger.debug('Fbo will use hardware Framebuffer')
            Fbo = HardwareFbo
        else:
            pymt_logger.debug('Fbo will use software Framebuffer')
            Fbo = SoftwareFbo
