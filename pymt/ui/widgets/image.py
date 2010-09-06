'''
MTImage: MTImage displays an image on the screen that can be repositioned.
         If you want to rotate it, use MTScatterImage instead.
'''

__all__ = ('MTImage', )

from pymt.core.image import Image
from pymt.ui.factory import MTWidgetFactory
from pymt.ui.widgets.container import MTContainer


def MTImage(arg, **kwargs):
    '''
    Convenience wrapper for MTContainer(Image(...)).
    Allows to easily display an image. For a full reference on the
    parameters accepted, please refer to the documentation of the
    `Image` class:
    '''
    return MTContainer(Image(arg, **kwargs))

MTImage.__doc__ += Image.__doc__
MTWidgetFactory.register('MTImage', MTImage)

