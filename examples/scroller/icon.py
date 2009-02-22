'''
WORK UNDER PROGRESS
Please do not change anything :)

Thank You.
 Sharath Patali

'''

from pymt import *

class MTicon(MTButton):
    def __init__(self, **kwargs):        
        kwargs.setdefault('scale', 1.0)
        kwargs.setdefault('filename', None)
        if kwargs.get('filename') is None:
            raise Exception('No filename given to MTicon')

        super(MTicon, self).__init__(**kwargs)
        self.fname = kwargs.get('filename')
        img                 = pyglet.image.load(kwargs.get('filename'))
        self.image          = pyglet.sprite.Sprite(img)
        self.image.x        = self.x
        self.image.y        = self.y
        self.scale          = kwargs.get('scale')
        self.image.scale    = self.scale
        self.width,self.height  = (self.image.width, self.image.height)
        self.texture = img.get_texture()

    def draw(self):
        with DO(gx_enable(GL_BLEND),gx_enable(GL_TEXTURE_2D)):
            glColor4f(1, 1, 1, 1)
            drawCover(self.texture.id, pos=(self.x,self.y), size=(self.image.width,self.image.height))
        
        
def drawCover(texture, pos=(0,0), size=(1.0,1.0)):
    with gx_enable(GL_TEXTURE_2D):
        glBindTexture(GL_TEXTURE_2D,texture)
        pos = ( pos[0],pos[1],   pos[0]+size[0],pos[1],   pos[0]+size[0],pos[1]+size[1],  pos[0],pos[1]+size[1] )
        texcoords = (0.0,0.0, 1.0,0.0, 1.0,1.0, 0.0,1.0)
        draw(4, GL_QUADS, ('v2f', pos), ('t2f', texcoords))
        pos2 = ( pos[0],pos[1]-size[1],   pos[0]+size[0],pos[1]-size[1],   pos[0]+size[0],pos[1]+size[1]-size[1],  pos[0],pos[1]+size[1]-size[1] )
        texcoords2 = (0.0,1.0, 1.0,1.0, 1.0,0.0, 0.0,0.0)
        color2 = (0,0,0,0.5, 0,0,0,0.5, 0.65,0.65,0.65,0.5, 0.65,0.65,0.65,0.5 )
        draw(4, GL_QUADS, ('v2f', pos2), ('t2f', texcoords2), ('c4f', color2))           
  


if __name__ == '__main__':
    w = MTWindow(color=(0,0,0,1.0),fullscreen=True)
    w.add_widget(MTicon(filename = "test.jpg",scale=0.5,pos=(w.width/2-128,w.height/2-128)))
    runTouchApp()

