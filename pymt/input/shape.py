'''
Touch Shape: Represent the shape of the touch
'''

__all__ = ['TouchShape', 'TouchShapeRect']

class TouchShape(object):
    '''Abstract class for all implementation of a shape'''
    pass

class TouchShapeRect(TouchShape):
    '''Represent a rectangle shape.'''
    __slots__ = ['width', 'height']
    
