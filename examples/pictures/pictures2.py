from __future__ import with_statement

# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Pictures'
PLUGIN_AUTHOR = 'Thomas Hansen & Sharath'
PLUGIN_DESCRIPTION = 'Demonstration of MTScatterWidget object'

from pymt import *
from pyglet.gl import *
import os
import random
import math



loader = Loader(loading_image='fitts.png')

class MTScatteredObj(MTScatterWidget):
    """MTScatteredObj is a zoomable Image widget with a possibility of providing rotation during spawning"""
    def __init__(self, img_src, pos=(0,0), size=(100,100), rotation=45):
        global loader
        self.image  = loader.sprite(img_src)
        self.aspectRatio = float(self.image.height)/float(self.image.width)
        MTScatterWidget.__init__(self, pos=pos, size=(size[0],size[0]*self.aspectRatio), rotation=rotation)
        self.pos = self.x - int(self.x/4), self.y - int(self.y/4)


    def draw(self):
        self.update_ratio()
        with DO(gx_matrix, gx_blending):
            glColor4f(0.9,0.9,0.9,1)
            drawRectangle((-6,-6),(self.width+12,self.width*self.aspectRatio+12))
            glScaled(float(self.width)/float(self.image.width), float(self.width*self.aspectRatio)/float(self.image.height), 1.0)
            self.image.draw()

    def update_ratio(self):
        ratio = float(self.image.height)/float(self.image.width)
        if ratio != self.aspectRatio:
            self.aspectRatio = ratio
            self.size = (self.width, self.width * ratio)



class ShadowSurface(MTWidget):
    def __init__(self, pos=(0,0), size=(100,100), bg_image='../pictures/back.jpg', **kargs):
        MTWidget.__init__(self, pos=pos, size=size)

        self.bg_image = pyglet.sprite.Sprite(pyglet.image.load(bg_image))
        self.bg_image.scale = float(self.width)/self.bg_image.width


        self.fbo = Fbo(self.size)
        self.fbo2 = Fbo(self.size) #a second one to blur the texture of teh first one

        #A shader that will draw every pixel that is drawn by OpenGL calls as black..no matter what
        shadow_shader_src = """
        void main(){
           gl_FragColor = vec4(0.0,0.0,0.0,1.0);
        }
        """
        self.shadow_shader = Shader(fragment_source=shadow_shader_src)


        #a gaussian blur filter, blurs either horizontally or vertically, depending on what direction variable is set to
        # so to achieve a full blur yu need two passes...this is more effective though because blurring on one axis only
        # only requires n (kernel size) texture lookups and multiplication...so total 2n for two passes
        # if we did it in one pass we would need n^2 lookups and multiplictions...funky how math works like that sometimes
        blur_shader_src = """
        uniform sampler2D   tex;
        uniform float direction;
        uniform float kernel_size;
        uniform float size_x ;
        uniform float size_y ;
        void main (void) {
            float rho = 10.0;
            vec2 dir = direction < 0.5 ? vec2(1.0,0.0) : vec2(0.0,1.0);

            float dx = 1.0 / size_x;
            float dy = 1.0 / size_y;

            vec2  st = gl_TexCoord [0].st;

            vec4    color = vec4 (0.0, 0.0, 0.0, 0.0);
            float   weight = 0.0;
            for (float i = -1.0*kernel_size ; i <= kernel_size ; i+=1.0) {
                float fac = exp (-(i * i) / (2.0 * rho * rho));
                weight += fac;
                color += texture2D (tex, st + vec2 (dx*i, dy*i) * dir) * fac;
            }
            gl_FragColor =  color / weight;
        }
        """
        self.blur_shader = Shader(fragment_source=blur_shader_src)



    #this function draws the shadows of child widgets into the framebuffer texture
    def drawShadowsToTexture(self):
        self.fbo.bind()              #bind the fbo...all openGl drawing calls now go into the fbo texture instead of teh screen
        glClearColor(1,1,1,1)    #set clear color
        glClear(GL_COLOR_BUFFER_BIT) #clear the color of the fbo texture
        #self.bg_image.draw()
        self.drawing_shadows = True #this is used in draw, while we are drawing shadows, we dont want to draw ourselves...but MTWidget.on_draw(self) will draw this and child widgets
        self.shadow_shader.use()    #use the shaodw shader...it just draws all teh child widgets as completly black
        MTWidget.on_draw(self)      #this will draw the child widgets
        self.shadow_shader.stop()   #disable shadow shader
        self.drawing_shadows = False

        self.fbo.release()

        self.blurShadowTexture()
        self.blurShadowTexture()

    #this function blurrs the shadow texture..first horizontally by drawing it into fbo2 using gaussioan shader with direction=0
    # then vertically by drawing the result from fbo2 into fbo1 using gaussian shader with dir=1..the end result is a nice
    # smooth shaodw in fbo1
    def blurShadowTexture(self):
        #horizontal pass
        self.fbo2.bind()
        self.blur_shader.use()
        self.blur_shader['size_x'] = float(self.width)
        self.blur_shader['size_y'] = float(self.height)
        self.blur_shader['kernel_size'] = 3.0
        self.blur_shader['direction'] = 0.0
        drawTexturedRectangle(self.fbo.texture, (0,0),(self.width,self.height))
        self.blur_shader.stop()
        self.fbo2.release()

        #vertical pass..this time draw back into first fbo, blurring teh one we just wrote the horizontal blur to
        self.fbo.bind()
        self.blur_shader.use()
        self.blur_shader['size_x'] = float(self.width)
        self.blur_shader['size_y'] = float(self.height)
        self.blur_shader['kernel_size'] = 3.0
        self.blur_shader['direction'] = 1.0
        drawTexturedRectangle(self.fbo2.texture, (0,0),(self.width,self.height))
        self.blur_shader.stop()
        self.fbo.release()


    #first we draw teh shadows into the texture..then we draw that texture and teh child widgets
    def on_draw(self):
        self.drawShadowsToTexture()
        MTWidget.on_draw(self)

    def draw(self):
        #if we are drawing the shadows into the fbo...dont draw the widget itself, otherwise there would be one giat shadow over everything
        if  self.drawing_shadows:
            return
        glColor4f(1,1,1,1)
        drawTexturedRectangle(self.fbo.texture, (0,0),(self.width,self.height))



def pymt_plugin_activate(w, ctx):
    ctx.c = ShadowSurface(size=w.size)
    for i in range (5):
        img_src = '../pictures/images/pic'+str(i+1)+'.jpg'
        teta = float((360/5)*i*(math.pi/180))
        x = int((w.width/2)+ (200*math.cos(teta)))
        y = int((w.height/2)+ (200*math.sin(teta)))
        size = 300
        rot = (360/5)*i
        b = MTScatteredObj(img_src, (x,y),(size,size), rot)
        ctx.c.add_widget(b)
    ctx.c._set_pos((int(w.width/2),int(w.height/2)))
    w.add_widget(ctx.c)

def pymt_plugin_deactivate(w, ctx):
    w.remove_widget(ctx.c)

if __name__ == '__main__':
    w = MTWindow()
    ctx = MTContext()
    print gl_info.get_extensions()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
