'''
PyMT: a multi touch UI toolkit for pyglet.

PyMT is a python module for developing multi-touch enabled media rich applications.

Currently the aim is to allow for quick and easy interaction design and rapid prototype development. There is also a focus on logging tasks or sessions of user interaction to quantitative data and the analysis/visualization of such data.

You can visit http://code.google.com/p/pymt/ for more informations !
'''

from __future__ import with_statement
import ConfigParser
import sys, getopt, os
from logger import pymt_logger, LOG_LEVELS

# Include lib as new module.
pymt_base = os.path.dirname(sys.modules[__name__].__file__)
pymt_libs = os.path.join(pymt_base, 'lib')
sys.path = [pymt_libs] + sys.path

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
    pymt_config.set('pymt', 'log_level', 'debug')
    pymt_config.set('pymt', 'double_tap_time', '250')
    pymt_config.set('pymt', 'double_tap_distance', '20')
    pymt_config.add_section('tuio')
    pymt_config.set('tuio', 'host', '127.0.0.1')
    pymt_config.set('tuio', 'port', '3333')
    pymt_config.set('tuio', 'ignore', '[]')
    pymt_config.add_section('dump')
    pymt_config.set('dump', 'enabled', '0')
    pymt_config.set('dump', 'prefix', 'img_')
    pymt_config.set('dump', 'format', 'jpeg')

    level = LOG_LEVELS.get(pymt_config.get('pymt', 'log_level'))
    pymt_logger.setLevel(level=level)

    # Note: import are done after logger module initialization,
    # and configuration applied to logger.
    from mtpyglet import *
    from graphx import *
    from ui import *
    from obj import OBJ
    from shader import *
    from vector import *
    from plugin import *
    from loader import *
    from gesture import *
    from utils import *

    # Read config file if exist
    if os.path.exists(pymt_config_fn):
        try:
            pymt_config.read(pymt_config_fn)
        except Exception, e:
            pymt_logger.exception('error while reading local configuration')
    else:
        try:
            with open(pymt_config_fn, 'w') as fd:
                pymt_config.write(fd)
        except Exception, e:
            pymt_logger.exception('error while saving default configuration file')


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
        pymt_logger.error(err)
        pymt_usage()
        sys.exit(2)
