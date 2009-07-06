'''
Touch Provider: Abstract class for a provider
'''

__all__ = ['TouchProvider']

class TouchProvider(object):

    def __init__(self, **kwargs):
        if self.__class__ == TouchProvider:
            raise NotImplementedError, 'class TouchProvider is abstract'

    def start(self):
        pass

    def stop(self):
        pass

    def update(self, dispatch_fn):
        pass

