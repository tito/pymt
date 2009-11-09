'''
PyMT: a multi touch UI toolkit, designed for programming on novel interfaces.

PyMT is a python module for developing multi-touch enabled media rich applications.

Currently the aim is to allow for quick and easy interaction design and rapid prototype development. There is also a focus on logging tasks or sessions of user interaction to quantitative data and the analysis/visualization of such data.

You can visit http://code.google.com/p/pymt/ for more informations !
'''

from __future__ import with_statement
import ConfigParser
import sys
import getopt
import os
from logger import pymt_logger, LOG_LEVELS

# Global settings options for pymt
options = {
    'shadow_window': True,
    'window': ('pygame', 'glut'),
    'text': ('cairo', 'pyglet', 'pygame'),
}

# Read environment
for option in options:
    key = 'PYMT_%s' % option.upper()
    if key in os.environ:
        try:
            if type(options[option]) in (list, tuple):
                options[option] = (str(os.environ[key]),)
            else:
                options[option] = os.environ[key].lower() in \
                    ('true', '1', 'yes', 'yup')
        except:
            pymt_logger.warning('Wrong value for %s environment key' % key)
            pymt_logger.exception('')

# Include lib as new module.
pymt_base_dir = os.path.dirname(sys.modules[__name__].__file__)
pymt_libs_dir = os.path.join(pymt_base_dir, 'lib')
pymt_modules_dir = os.path.join(pymt_base_dir, 'mods')
pymt_data_dir = os.path.join(pymt_base_dir, 'data')
pymt_providers_dir = os.path.join(pymt_base_dir, 'input', 'providers')
sys.path = [pymt_libs_dir] + sys.path

# Don't go further if we generate documentation
if not os.path.basename(sys.argv[0]).startswith('sphinx'):

    # Configuration management
    pymt_home_dir = os.path.expanduser('~/.pymt/')
    pymt_config_fn = os.path.join(pymt_home_dir, 'config')
    if not os.path.exists(pymt_home_dir):
        os.mkdir(pymt_home_dir)
    pymt_usermodules_dir = os.path.expanduser('~/.pymt/mods/')
    if not os.path.exists(pymt_usermodules_dir):
        os.mkdir(pymt_usermodules_dir)

    # Create default configuration
    pymt_config = ConfigParser.ConfigParser()
    pymt_config.add_section('pymt')
    pymt_config.set('pymt', 'show_fps', '0')
    pymt_config.set('pymt', 'show_eventstats', '0')
    pymt_config.set('pymt', 'log_level', 'info')
    pymt_config.set('pymt', 'double_tap_time', '250')
    pymt_config.set('pymt', 'double_tap_distance', '20')
    pymt_config.set('pymt', 'enable_simulator', '1')
    pymt_config.set('pymt', 'ignore', '[]')
    pymt_config.add_section('keyboard')
    pymt_config.set('keyboard', 'layout', 'qwerty')
    pymt_config.add_section('graphics')
    pymt_config.set('graphics', 'fbo', 'hardware')
    pymt_config.set('graphics', 'fullscreen', '1')
    pymt_config.set('graphics', 'width', '640')
    pymt_config.set('graphics', 'height', '480')
    pymt_config.set('graphics', 'vsync', '1')
    pymt_config.set('graphics', 'display', '-1')
    pymt_config.set('graphics', 'line_smooth', '1')
    pymt_config.add_section('input')
    pymt_config.set('input', 'default', 'tuio,0.0.0.0:3333')
    pymt_config.set('input', 'mouse', 'mouse')
    pymt_config.add_section('dump')
    pymt_config.set('dump', 'enabled', '0')
    pymt_config.set('dump', 'prefix', 'img_')
    pymt_config.set('dump', 'format', 'jpeg')
    pymt_config.add_section('modules')

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

    # Set level of logger
    level = LOG_LEVELS.get(pymt_config.get('pymt', 'log_level'))
    pymt_logger.setLevel(level=level)

    # Note: import are done after logger module initialization,
    # and configuration applied to logger.
    from exceptions import *
    from clock import *
    from image import *
    from modules import *
    from input import *
    from base import *
    from graphx import *
    from ui import *
    from obj import OBJ
    from shader import *
    from vector import *
    from plugin import *
    from loader import *
    from gesture import *
    from utils import *
    from texture import *
    from text import *
    from video import *


    # Can be overrided in command line
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hp:fwFem:s',
            ['help', 'fullscreen', 'windowed', 'fps', 'event',
             'module=', 'save',
             'display=', 'size=', 'dump-frame', 'dump-format=', 'dump-prefix='])
        need_save = False
        for opt, arg in opts:
            if opt in ['-h', '--help']:
                pymt_usage()
                sys.exit(0)
            elif opt in ['-p', '--provider']:
                id, args = arg.split(':', 1)
                pymt_config.set('input', id, args)
            elif opt in ['-f', '--fullscreen']:
                pymt_config.set('graphics', 'fullscreen', '1')
            elif opt in ['-w', '--windowed']:
                pymt_config.set('graphics', 'fullscreen', '0')
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
            elif opt in ['--size']:
                w, h = str(arg).split('x')
                pymt_config.set('graphics', 'width', w)
                pymt_config.set('graphics', 'height', h)
            elif opt in ['--display']:
                pymt_config.set('graphics', 'display', str(arg))
            elif opt in ['-m', '--module']:
                if str(arg) == 'list':
                    pymt_modules.usage_list()
                    sys.exit(0)
                pymt_config.set('modules', str(arg), '')
            elif opt in ['-s', '--save']:
                need_save = True

        if need_save:
            try:
                with open(pymt_config_fn, 'w') as fd:
                    pymt_config.write(fd)
            except Exception, e:
                pymt_logger.exception('error while saving default configuration file')
            pymt_logger.info('PyMT configuration saved.')
            sys.exit(0)

        # last initialization
        if options['shadow_window']:
            pymt_logger.debug('Creating shadow window')
            shadow_window = MTWindow(shadow=True)

    except getopt.GetoptError, err:
        pymt_logger.error(err)
        pymt_usage()
        sys.exit(2)
