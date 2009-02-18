'''PyMT, a multi touch UI toolkit for pyglet.

PyMT is a python module for developing multi-touch enabled media rich applications.

Currently the aim is to allow for quick and easy interaction design and rapid prototype development. There is also a focus on logging tasks or sessions of user interaction to quantitative data and the analysis/visualization of such data.

You can visit http://code.google.com/p/pymt/ for more informations !
'''

from __future__ import with_statement
import ConfigParser
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

# Don't go further if we generate documentation
if not os.path.basename(sys.argv[0]).startswith('sphinx'):

    # Configuration management
    pymt_home_dir = os.path.expanduser('~/.pymt/')
    pymt_config_fn = os.path.join(pymt_home_dir, 'config')
    if not os.path.exists(pymt_home_dir):
        os.mkdir(pymt_home_dir)

    # Create default configuration
    pymt_config = ConfigParser.ConfigParser()
    pymt_config.add_section('pymt')
    pymt_config.set('pymt', 'show_fps', '0')
    pymt_config.set('pymt', 'show_eventstats', '0')
    pymt_config.set('pymt', 'fullscreen', '1')
    pymt_config.add_section('tuio')
    pymt_config.set('tuio', 'host', '127.0.0.1')
    pymt_config.set('tuio', 'port', '3333')
    pymt_config.add_section('dump')
    pymt_config.set('dump', 'enabled', '0')
    pymt_config.set('dump', 'prefix', 'img_')
    pymt_config.set('dump', 'format', 'jpeg')

    # Read config file if exist
    if os.path.exists(pymt_config_fn):
        try:
            pymt_config.read(pymt_config_fn)
        except Exception, e:
            print 'Warning: error while reading local configuration :', e
    else:
        try:
            with open(pymt_config_fn, 'w') as fd:
                pymt_config.write(fd)
        except Exception, e:
            print 'Warning: error while saving default configuration file :', e


    # Can be overrided in command line
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hp:H:fwFe',
            ['help', 'port=', 'host=', 'fullscreen', 'windowed', 'fps', 'event',
             'dump-frame', 'dump-format=', 'dump-prefix='])
        for opt, arg in opts:
            if opt in ['-h', '--help']:
                pymt_usage()
                sys.exit(0)
            elif opt in ['-p', '--port']:
                pymt_config.set('tuio', 'port', str(arg))
            elif opt in ['-H', '--host']:
                pymt_config.set('tuio', 'host', str(arg))
            elif opt in ['-f', '--fullscreen']:
                pymt_config.set('pymt', 'fullscreen', '1')
            elif opt in ['-w', '--windowed']:
                pymt_config.set('pymt', 'fullscreen', '0')
            elif opt in ['-F', '--fps']:
                pymt_config.set('pymt', 'show_fps', '1')
            elif opt in ['-e', '--eventstats']:
                pymt_config.set('pymt', 'show_eventstats', '1')
            elif opt in ['--dump-frame']:
                pymt_config.set('dump', 'enabled', '1')
            elif opt in ['--dump-prefix']:
                pymt_config.set('dump', 'prefix', str(arg))
            elif opt in ['--dump-format']:
                pymt_config.set('dump', 'format', str(arg))

    except getopt.GetoptError, err:
        print str(err), sys.argv, __name__
        pymt_usage()
        sys.exit(2)
