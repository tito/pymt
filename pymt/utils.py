__all__ = ['intersection', 'difference', 'curry', 'strtotuple']

import re

def intersection(set1, set2):
    return filter(lambda s:s in set2, set1)

def difference(set1, set2):
    return filter(lambda s:s not in set2, set1)

def curry(fn, *cargs, **ckwargs):
    def call_fn(*fargs, **fkwargs):
        d = ckwargs.copy()
        d.update(fkwargs)
        return fn(*(cargs + fargs), **d)
    return call_fn

def strtotuple(s):
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

