from mtpyglet import *
from graphx import *
from ui import *
from pyglet import *
from obj import OBJ
from shader import *

def curry(fn, *cargs, **ckwargs):
	def call_fn(*fargs, **fkwargs):
		d = ckwargs.copy()
		d.update(fkwargs)
		return fn(*(cargs + fargs), **d)
	return call_fn