# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Flicker Favorites Viewer'
PLUGIN_AUTHOR = 'Sharath Patali'
PLUGIN_DESCRIPTION = 'This application download pictures asynchrnously and displaces them as a MT Image'

from pymt import *
from urllib import urlopen
from FlickrClient import *
import random

loader = Loader(loading_image='loading.gif')

class FlickrPhoto(MTScatterImage):
    def __init__(self, img_src, pos=(0,0), size=(200,200),rotation=45):
        self.image  = loader.sprite(img_src)
        self.aspectRatio = float(self.image.height)/float(self.image.width)
        super(MTScatterImage, self).__init__(pos=pos, size=(size[0],size[0]*self.aspectRatio))
        self.rotation = rotation
        
    def draw(self):
        self.update_ratio()
        glPushMatrix()
        enable_blending()
        glColor4f(0.9,0.9,0.9,1)
        drawRectangle((-6,-6),(self.width+12,self.width*self.aspectRatio+12))
        glScaled(float(self.width)/float(self.image.width), float(self.width*self.aspectRatio)/float(self.image.height), 1.0)
        self.image.draw()
        glPopMatrix()
   
    def update_ratio(self):
        ratio = float(self.image.height)/float(self.image.width)
        if ratio != self.aspectRatio:
            self.aspectRatio = ratio
            self.size = (self.width, self.width * ratio)

class flickrEngine(MTWidget):
    def __init__(self, pos=(0,0), size=(100,100), **kargs):
        MTWidget.__init__(self, pos=pos, size=size)
        self.USER_ID = '23307960@N04' # SET THE FLICKR USER ID HERE TO FETCH THE FAVORITES
        self.client = FlickrClient(API_KEY)
        self.photos = self.client.flickr_favorites_getPublicList(user_id=self.USER_ID)
        self.num_of_photos = len(self.photos)
        self.generatePhotos()
   
    def generatePhotos(self):
        for photo in self.photos:
            self.farm_id = photo('farm')
            self.server_id = photo('server')
            self.photo_id = photo('id')
            self.secret = photo('secret')
            self.url = "http://farm"+self.farm_id+".static.flickr.com/"+self.server_id+"/"+self.photo_id+"_"+self.secret+".jpg"
            x = int(random.uniform(200, w.width-200))
            y = int(random.uniform(100, w.height-100))
            rot = random.uniform(0, 360)
            self.pic = FlickrPhoto(img_src=self.url,pos=(x,y),rotation=rot)
            self.add_widget(self.pic)
            
            
if __name__ == '__main__':
    w = MTWindow()
    w.set_fullscreen()
    flickme = flickrEngine()
    w.add_widget(flickme)
    runTouchApp()