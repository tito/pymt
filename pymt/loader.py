import pyglet.image
import pyglet.sprite

class ProxyImage(pyglet.image.AbstractImage):
    def __init__(self, name, loader, image=None, loading_image=None):
        self.name = name
        self.loader = loader
        self.image = data
        self.loading_image = image
        self._width, self._height = (0, 0)
        self._sprite = None

    def get_image_data(self):
        if self.image:
            return self.image.get_image_data()
        if self.loading_image:
            return self.loading_image.get_image_data()

    def get_texture(self, rectangle=False):
        if self.image:
            return self.image.get_texture(rectangle=rectangle)
        if self.loading_image:
            return self.loading_image.get_texture(rectangle=rectangle)

    def get_region(self, x, y, width, height):
        if self.image:
            return self.image.get_region(x, y, width, height)
        if self.loading_image:
            return self.loading_image.get_region(x, y, width, height)

    def save(self, filename=None, file=None, encoder=None):
        if self.image:
            return self.image.save(filename, file, encoder)
        if self.loading_image:
            return self.loading_image.save(filename, file, encoder)

    def blit(self, x, y, z=0):
        if self.image:
            return self.image.blit(x, y, z)
        if self.loading_image:
            return self.loading_image.blit(x, y, z)

    def blit_into(self, source, x, y, z=0):
        if self.image:
            return self.image.blit_into(source, x, y, z)
        if self.loading_image:
            return self.loading_image.blit_into(source, x, y, z)

    def blit_to_texture(self, target, level, x, y, z=0):
        if self.image:
            return self.image.blit_to_texture(target, level, x, y, z)
        if self.loading_image:
            return self.loading_image.blit_to_texture(target, level, x, y, z)

    def _get_image(self):
        if not self.image:
            self.image = self.loader.get_image(self.name)
            if self.image:
                self._update_dimensions()
                if self._sprite:
                    self._sprite._update_image()
        if not self.image:
            return self.loading_image
        return self.image

    def _update_dimensions(self):
        if self.image:
            self.image.width = self.width
            self.image.height = self.height

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
        if self.loading_image:
            return self.loading_image.image_data
    image_data = property(_get_image_data)

    def _get_texture(self):
        if self.image:
            return self.image.texture
        if self.loading_image:
            return self.loading_image.texture
    texture = property(_get_texture)

    def _get_mipmapped_texture(self):
        if self.image:
            return self.image.mipmapped_texture
        if self.loading_image:
            return self.loading_image.mipmapped_texture
    mipmapped_texture = property(_get_mipmapped_texture)


class ProxySprite(pyglet.sprite.Sprite):
    def __init__(self, img, x=0, y=0, blend_src=770, blend_dest=771, batch=None, group=None, usage='dynamic'):
        self._internal_image = img
        if isinstance(self._internal_image, ProxyImage):
            self._internal_image._sprite = self
        pyglet.sprite.Sprite(img, x, y, blend_src, blend_dest, batch, group, usage)

    def _update_image(self):
        self.image = self._internal_image

class Loader(object):
    def __init__(self, loading_image=None):
        self.cache = {}
        self.loadlist = []
        self.thread = None
        self.loading_image = loading_image

    def sprite(self, name, async=True):
        data = self.get_image_data(name)
        if not data:
            if not async:
                return pyglet.image.load(name)
            if not name in self.loadlist:
                self.loadlist.append(name)
                self._start_load()
        return ProxySprite(name=name, loader=self, data=data)

    def get_image(self, name):
        if name in self.cache:
            return self.cache[name]
        return None

    def _start_load(self):
        if self.thread:
            if self.thread.isAlive():
                return
            del self.thread
        self.thread = threading.Thread(target=self._run_load)
        self.thread.start()

    def _run_load(self):
        while len(self.loadlist):
            name = self.loadlist.pop()
            try:
                self.cache[name] = pyglet.image.load(name)
            except Exception, e:
                print 'Loader: unable to load image %s' % name, e
