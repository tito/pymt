'''
Touch Factory : Factory of touch providers.
'''

__all__ = ['TouchFactory']

class TouchFactory:
    __providers__ = {}

    @staticmethod
    def register(name, classname):
        TouchFactory.__providers__[name] = classname

    @staticmethod
    def list():
        return TouchFactory.__providers__

    @staticmethod
    def get(name):
        if name in TouchFactory.__providers__:
            return TouchFactory.__providers__[name]
        return None
