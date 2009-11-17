'''
Utils: generic toolbox
'''

__all__ = ['intersection', 'difference', 'curry', 'strtotuple',
           'get_color_from_hex', 'get_color_for_pyglet',
           'is_color_transparent', 'boundary', 'connect',
           'deprecated']

import re
import functools
import warnings
import logger

def boundary(value, minvalue, maxvalue):
    '''Limit a value between a minvalue and maxvalue'''
    return min(max(value, minvalue), maxvalue)

def intersection(set1, set2):
    '''Return intersection between 2 list'''
    return filter(lambda s:s in set2, set1)

def difference(set1, set2):
    '''Return difference between 2 list'''
    return filter(lambda s:s not in set2, set1)

def curry(fn, *cargs, **ckwargs):
    '''Change the function signature to pass new variable.'''
    def call_fn(*fargs, **fkwargs):
        d = ckwargs.copy()
        d.update(fkwargs)
        return fn(*(cargs + fargs), **d)
    return call_fn

def strtotuple(s):
    '''Convert a tuple string into tuple,
    with some security check. Designed to be used
    with eval() function ::

        a = (12, 54, 68)
        b = str(a)         # return '(12, 54, 68)'
        c = strtotuple(b)  # return (12, 54, 68)

    '''
    # security
    if not re.match('^[,.0-9 ()\[\]]*$', s):
        raise Exception('Invalid characters in string for tuple conversion')
    # fast syntax check
    if s.count('(') != s.count(')'):
        raise Exception('Invalid count of ( and )')
    if s.count('[') != s.count(']'):
        raise Exception('Invalid count of [ and ]')
    r = eval(s)
    if type(r) not in (list, tuple):
        raise Exception('Conversion failed')
    return r

def get_color_from_hex(s):
    '''Transform from hex string color to pymt color'''
    if s.startswith('#'):
        return get_color_from_hex(s[1:])

    value = [int(x, 16)/255. for x in re.split('([0-9a-f]{2})', s) if x != '']
    if len(value) == 3:
        value.append(1)
    return value

def get_color_for_pyglet(c):
    '''Transform from pymt color to pyglet color'''
    return map(lambda x: int(255 * x), c)

def is_color_transparent(c):
    '''Return true if alpha channel is 0'''
    if len(c) < 4:
        return False
    if float(c[3]) == 0.:
        return True
    return False

def connect(w1, p1, w2, p2, func=lambda x: x):
    '''Connect events to a widget property'''
    w1.connect(p1, w2, p2, func)

def deprecated(func):
    '''This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.'''

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warning = "Call to deprecated function %s.  In %s, Line: %d." % (func.__name__, func.func_code.co_filename, func.func_code.co_firstlineno + 1 )
        logger.pymt_logger.warn(warning)
        return func(*args, **kwargs)
    return new_func

