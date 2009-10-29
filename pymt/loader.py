'''
Loader: asynchronous loader, easily extensible.

This is the Asynchronous Loader. You can use it to load an image
and use it, even if data are not yet available. You must specify a default
loading image for using a such loader ::

    from pymt import *
    loader = Loader(loading_image='load.png')
    sprite = loader.sprite('mysprite.png')

You can also load image from url ::

    sprite = loader.sprite('http://mysite.com/test.png')

'''

__all__ = ['ProxySprite', 'ProxyImage', 'Loader']

import threading
import pyglet.image
import pyglet.sprite
import time
import urllib
from logger import pymt_logger
from clock import getClock

try:
    # Used for gdk thread lock access.
    import gtk
except:
    pass

class ProxyImage(pyglet.image.AbstractImage):
    '''ProxyImage is a derivation of AbstractImage of pyglet.
    You have the same abstraction, except that he use loading_image when
    the final image are not yet available.

    Don't instanciate directly, use the loader ::

        from pymt import *
        loader = Loader(loading_image='load.png')
        image = loader.image('myimage.png')

    You can use the loader to get image in a synchronous way ::

        image2 = loader.image('test.png', async=False)
    '''
    def __init__(self, name, loader, image=None, loading_image=None):
        self.name = name
        self.loader = loader
        self.image = image
        self.loading_image = loading_image
        self._width = self.loading_image.width
        self._height = self.loading_image.height
        self._sprite = None
        super(ProxyImage, self).__init__(self.width, self.height)

    def get_image_data(self):
        if self.image:
            return self.image.get_image_data()
        return self.loading_image.get_image_data()

    def get_texture(self, rectangle=False):
        if self.image:
            return self.image.get_texture(rectangle=rectangle)
        return self.loading_image.get_texture(rectangle=rectangle)

    def get_region(self, x, y, width, height):
        if self.image:
            return self.image.get_region(x, y, width, height)
        return self.loading_image.get_region(x, y, width, height)

    def save(self, filename=None, file=None, encoder=None):
        if self.image:
            return self.image.save(filename, file, encoder)
        return self.loading_image.save(filename, file, encoder)

    def blit(self, x, y, z=0):
        if self.image:
            return self.image.blit(x, y, z)
        return self.loading_image.blit(x, y, z)

    def blit_into(self, source, x, y, z=0):
        if self.image:
            return self.image.blit_into(source, x, y, z)
        return self.loading_image.blit_into(source, x, y, z)

    def blit_to_texture(self, target, level, x, y, z=0):
        if self.image:
            return self.image.blit_to_texture(target, level, x, y, z)
        return self.loading_image.blit_to_texture(target, level, x, y, z)

    def _get_image(self):
        if not self.image:
            self.image = self.loader.get_image(self.name)
            if self.image:
                self._update_dimensions()
                if self._sprite:
                    self._sprite._update_image()
        if self.image:
            return self.image
        return self.loading_image

    def _update_dimensions(self):
        if self.image:
            self.width = self.image.width
            self.height = self.image.height

    def _set_width(self, w):
        self._width = w
    def _get_width(self):
        if self.image:
            return self.image.width
        return self._width
    width = property(_get_width, _set_width)

    def _set_height(self, h):
        self._height = h
    def _get_height(self):
        if self.image:
            return self.image.height
        return self._height
    height = property(_get_height, _set_height)

    def _get_image_data(self):
        if self.image:
            return self.image.image_data
        return self.loading_image.image_data
    image_data = property(_get_image_data)

    def _get_texture(self):
        if self.image:
            return self.image.texture
        return self.loading_image.texture
    texture = property(_get_texture)

    def _get_mipmapped_texture(self):
        if self.image:
            return self.image.mipmapped_texture
        return self.loading_image.mipmapped_texture
    mipmapped_texture = property(_get_mipmapped_texture)


class ProxySprite(pyglet.sprite.Sprite):
    '''ProxySprite is a derivation of Sprite of pyglet.
    You have the same abstraction, except that he use loading_image when
    the final image are not yet available.

    Don't instanciate directly, use the loader ::

        from pymt import *
        loader = Loader(loading_image='load.png')
        image = loader.sprite('myimage.png')
    '''
    def __init__(self, img, x=0, y=0, blend_src=770, blend_dest=771, batch=None, group=None, usage='dynamic'):
        self._internal_image = img
        if isinstance(self._internal_image, ProxyImage):
            self._internal_image._sprite = self
        super(ProxySprite, self).__init__(img, x, y, blend_src, blend_dest, batch, group, usage)

    def _update_image(self):
        self.image = self._internal_image

class Loader(object):
    '''Base for loading image in an asynchronous way.
    Current loader is based on pyglet.image.load method, and can
    create only Sprite and Image pyglet object.
    
    .. note::
        It'll be reworked in the next version to support loading
        of other object.

    '''
    def __init__(self, loading_image, async=True):
        self.cache = {}
        self.loadlist = {}
        self.updatelist = []
        self.thread = None
        self.loading_image = self.image(loading_image, async=False)
        self.default_async=async
        getClock().schedule_interval(self._run_update, .5)

    def image(self, name, async=None):
        '''Load an image, and return a ProxyImage'''
        # get data cache
        data = self.get_image(name)
        if data:
            return ProxyImage(name=name, loader=self, image=data,
                              loading_image=self.loading_image)

        # no data ? user want data async or not ?
        if async is None:
            async = self.default_async
        if not async:
            return pyglet.image.load(name)

        # prepare proxy image
        obj = ProxyImage(name=name, loader=self, image=None,
                          loading_image=self.loading_image)

        # add name into loadlist
        if not name in self.loadlist:
            self.loadlist[name] = []
        self.loadlist[name].append(obj)

        # start loading
        self._start_load()

        return obj

    def sprite(self, name, async=None):
        '''Load an sprite, and return a ProxySprite'''
        img = self.image(name, async)
        return ProxySprite(img)

    def get_image(self, name):
        if name in self.cache:
            return self.cache[name]
        return None

    def _run_update(self, dt):
        while len(self.updatelist):
            obj = self.updatelist.pop()
            obj._get_image()

    def _start_load(self):
        if self.thread:
            if self.thread.isAlive():
                return
            del self.thread
        self.thread = threading.Thread(target=self._run_load)
        self.thread.setDaemon(True)
        self.thread.start()

    def _run_load(self):
        while len(self.loadlist):
            name, objs = self.loadlist.popitem()
            try:
                fd = urllib.urlopen(name)
                if fd.getcode() < 200 or fd.getcode() >= 300:
                    pymt_logger.error('unable to load image %s (errorcode=%d)' % \
                        (name, fd.getcode()))
                    fd.close()
                    continue


                # Special case for gdk loader
                # We experienced random crash while using pyglet.image.load
                # in gdk_pixbuf_loader_write().
                # Since we don't known what pyglet will use to load image
                # we lock the loading each time
                try:
                    gtk.gdk.threads_enter()
                except:
                    pass

                # Load image
                try:
                    self.cache[name] = pyglet.image.load(name, file=fd)
                except Exception, e:
                    pymt_logger.error('unable to load image %s : %s' % (name, e))

                try:
                    gtk.gdk.threads_leave()
                except:
                    pass

                # Close fd
                fd.close()

                # Notify object for new data
                for obj in objs:
                    self.updatelist.append(obj)

            except Exception, e:
                pymt_logger.error('unable to load image %s : %s' % (name, e))
