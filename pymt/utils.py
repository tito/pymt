'''
Utils: generic toolbox
'''

__all__ = ['intersection', 'difference', 'curry', 'strtotuple',
           'get_color_from_hex', 'get_color_for_pyglet']

import re

def boundary(value, minvalue, maxvalue):
    '''Limit a value between a minvalue and maxvalue'''
    return max(min(value, minvalue), maxvalue)

def intersection(set1, set2):
    '''Return intersection between 2 list'''
    return filter(lambda s:s in set2, set1)

def difference(set1, set2):
    '''Return difference between 2 list'''
    return filter(lambda s:s not in set2, set1)

def curry(fn, *cargs, **ckwargs):
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
    if s.startswith('#'):
        return get_color_from_hex(s[1:])

    value = [int(x, 16)/255. for x in re.split('([0-9a-f]{2})', s) if x != '']
    if len(value) == 3:
        value.append(1)
    return value

def get_color_for_pyglet(c):
    return map(lambda x: int(255 * x), c)

