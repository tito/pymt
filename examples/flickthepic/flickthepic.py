# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Flickr Viewer'
PLUGIN_AUTHOR = 'Sharath Patali'
PLUGIN_DESCRIPTION = 'This application download pictures asynchrnously and displays them as a MT Image'

from pymt import *
from pyglet.gl import *
from urllib import urlopen
from FlickrClient import *
import random, sys

loader = Loader(loading_image='../flickthepic/loading.gif')

class FlickrPhoto(MTScatterImage):
    '''This class is responsible for displaying the flickr image'''
    def __init__(self, **kwargs):
        kwargs.setdefault('size', (200,200))
        kwargs.setdefault('color', (0.9,0.9,0.9,1))
        super(FlickrPhoto, self).__init__(**kwargs)
        self.aspectRatio = 1.33
        self.update_ratio()
        self.color = kwargs.get('color')

    def draw(self):
        self.update_ratio()
        glColor4f(*self.color)
        drawRectangle((-6,-6),(self.width+12,self.width*self.aspectRatio+12))
        super(FlickrPhoto, self).draw()

    def update_ratio(self):
        ratio = float(self.image.height)/float(self.image.width)
        if ratio != self.aspectRatio:
            self.aspectRatio = ratio
            self.size = (self.width, self.width * ratio)



class flickrEngine(MTWidget):
    '''This is a engine which communicates with the flickr server using flickr api to download the image urls'''
    def __init__(self, **kwargs):
        kwargs.setdefault('search_text', "Dark Knight")
        kwargs.setdefault('size', (200,200))
        kwargs.setdefault('color', (0.9,0.9,0.9,1))
        super(flickrEngine, self).__init__(**kwargs)

        self.search_text = kwargs.get('search_text')
        self.USER_ID = '23307960@N04' # SET THE FLICKR USER ID HERE TO FETCH THE FAVORITES
        self.client = FlickrClient(API_KEY)
        self.photos = self.client.flickr_photos_search(text=self.search_text,per_page=8)
        self.num_of_photos = len(self.photos)

    def generatePhotos(self):
        for photo in self.photos:
            self.farm_id = photo('farm')
            self.server_id = photo('server')
            self.photo_id = photo('id')
            self.secret = photo('secret')
            self.url = "http://farm"+self.farm_id+".static.flickr.com/"+self.server_id+"/"+self.photo_id+"_"+self.secret+".jpg"
            x = int(random.uniform(200, self.get_parent_window().width-200))
            y = int(random.uniform(100, self.get_parent_window().height-100))
            rot = random.uniform(0, 360)
            self.pic = FlickrPhoto(filename=self.url, loader=loader, pos=(x, y), rotation=rot)
            self.add_widget(self.pic)



class flickrSearchButton(MTButton):
    '''Responsible for removing older images and downloading new images'''
    def __init__(self, **kwargs):
        kwargs.setdefault('text_widget', None)
        kwargs.setdefault('label', "SEARCH")
        super(flickrSearchButton, self).__init__(**kwargs)
        self.txt_widget = kwargs.get('text_widget')
        self.flickme = None

    def do_search(self):
        if self.flickme:
            self.parent.remove_widget(self.flickme)
        self.flickme = flickrEngine(search_text=self.txt_widget.label)
        self.parent.add_widget(self.flickme)
        self.flickme.generatePhotos()

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.do_search()
            return True

class flickrControl(MTWidget):
    '''This widget handles the controls text input and the search button'''
    def __init__(self, **kwargs):
        super(flickrControl, self).__init__(**kwargs)
        self.text_input = MTTextInput(pos=(105,0),size=(100,100), style={'font-size': 50})
        self.add_widget(self.text_input)
        self.flickSearch = flickrSearchButton(text_widget=self.text_input)
        self.add_widget(self.flickSearch)
        self.text_input.push_handlers('on_text_validate', self.on_text_validate)

    def on_text_validate(self):
        self.flickSearch.do_search()

def pymt_plugin_activate(root, ctx):
    ctx.flickControl = flickrControl()
    root.add_widget(ctx.flickControl)

def pymt_plugin_deactivate(root, ctx):
    root.remove_widget(ctx.flickControl)

if __name__ == '__main__':
    w = MTWindow()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
