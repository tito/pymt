from pymt import *
from pyglet import *
from pyglet.gl import *
from ctypes import byref, c_uint

class Fbo:
    def __init__(self, size=(1024,1024)):
	print "creating fbo"
	self.framebuffer = c_uint(0)
	self.texture = c_uint(0)
	
	glGenFramebuffersEXT(1,byref(self.framebuffer))
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, self.framebuffer)

        glGenTextures (1, byref(self.texture))
	glBindTexture (GL_TEXTURE_2D, self.texture)
	glTexParameteri (GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri (GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
	glTexImage2D (GL_TEXTURE_2D, 0, GL_RGB, size[0], size[1], 0,GL_RGB, GL_UNSIGNED_BYTE, 0)
	glFramebufferTexture2DEXT (GL_FRAMEBUFFER_EXT, GL_COLOR_ATTACHMENT0_EXT, GL_TEXTURE_2D, self.texture, 0)
	glBindRenderbufferEXT (GL_RENDERBUFFER_EXT, 0)
	glBindFramebufferEXT (GL_FRAMEBUFFER_EXT, 0)
                                
	status = glCheckFramebufferStatusEXT (GL_FRAMEBUFFER_EXT);
	if status != GL_FRAMEBUFFER_COMPLETE_EXT:
	    print "Error in framebuffer activation"





class PaintWindow(TouchWindow):
    def __init__(self):
        config = Config(sample_buffers=1, samples=4, depth_size=16, double_buffer=True, vsync=0)
        TouchWindow.__init__(self, config)
	self.fbo = Fbo((self.width, self.height))
        self.touch_positions = {}
	
        
    def on_draw(self):
	glClearColor(0.8,0.8,0.7,1.0)
	self.clear()
	drawTexturedRectangle( self.fbo.texture, size=(self.width, self.height))
            
    def on_touch_down(self, touches, touchID, x, y):
	glBindFramebufferEXT (GL_FRAMEBUFFER_EXT, self.fbo.framebuffer)
	
	glBindFramebufferEXT (GL_FRAMEBUFFER_EXT, 0)
	pass

        
    def on_touch_move(self, touches, touchID, x, y):
	pass

        
    def on_touch_up(self, touches, touchID, x, y):
	pass
        

    
    
w = PaintWindow()
runTouchApp()
