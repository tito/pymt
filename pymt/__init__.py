r"""PyMT, a multi touch UI toolkit for pyglet.

PyMT is a python module for developing multi-touch enabled media rich applications.

Currently the aim is to allow for quick and easy interaction design and rapid prototype development. There is also a focus on logging tasks or sessions of user interaction to quantitative data and the analysis/visualization of such data.

You can visit http://code.google.com/p/pymt/ for more informations !
"""


from mtpyglet import *
from graphx import *
from ui import *
from pyglet import *
from obj import OBJ
from shader import *
from vector import Vector
from plugin import *
from loader import *
from gesture import *
from pymt.ui import *

def curry(fn, *cargs, **ckwargs):
    def call_fn(*fargs, **fkwargs):
        d = ckwargs.copy()
        d.update(fkwargs)
        return fn(*(cargs + fargs), **d)
    return call_fn
