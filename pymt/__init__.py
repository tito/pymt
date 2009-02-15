'''PyMT, a multi touch UI toolkit for pyglet.

PyMT is a python module for developing multi-touch enabled media rich applications.

Currently the aim is to allow for quick and easy interaction design and rapid prototype development. There is also a focus on logging tasks or sessions of user interaction to quantitative data and the analysis/visualization of such data.

You can visit http://code.google.com/p/pymt/ for more informations !
'''


from mtpyglet import *
from graphx import *
from ui import *
from pyglet import *
from obj import OBJ
from shader import *
from vector import *
from plugin import *
from loader import *
from gesture import *
from pymt.ui import *

import sys, getopt, os

def curry(fn, *cargs, **ckwargs):
    def call_fn(*fargs, **fkwargs):
        d = ckwargs.copy()
        d.update(fkwargs)
        return fn(*(cargs + fargs), **d)
    return call_fn

# PYMT Options management
# Can be overrided in command line
if not os.path.basename(sys.argv[0]).startswith('sphinx'):
    options = {'host': '127.0.0.1', 'port': 3333, 'eventstats': False}
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hp:H:fwFe',
            ['help', 'port=', 'host=', 'fullscreen', 'windowed', 'fps', 'event',
             'dump-frame', 'dump-format=', 'dump-prefix='])
        for opt, arg in opts:
            if opt in ['-h', '--help']:
                pymt_usage()
                sys.exit(0)
            elif opt in ['-p', '--port']:
                options['port'] = int(arg)
            elif opt in ['-H', '--host']:
                options['host'] = str(arg)
            elif opt in ['-f', '--fullscreen']:
                options['fullscreen'] = True
            elif opt in ['-w', '--windowed']:
                options['fullscreen'] = False
            elif opt in ['-F', '--fps']:
                options['show_fps'] = True
            elif opt in ['-e', '--eventstats']:
                options['eventstats'] = True
            elif opt in ['--dump-frame']:
                options['dump_frame'] = True
            elif opt in ['--dump-prefix']:
                options['dump_prefix'] = str(arg)
            elif opt in ['--dump-format']:
                options['dump_format'] = str(arg)

    except getopt.GetoptError, err:
        print str(err), sys.argv, __name__
        pymt_usage()
        sys.exit(2)
