'''
PyMT: Python Multitouch Toolkit

PyMT is an open source library for developing multi-touch applications. It is
completely cross-platform (Linux/OSX/Win) and released under the terms of the
GNU LGPL.

It comes with native support for many multi-touch input devices, a growing
library of multi-touch aware widgets, hardware accelerated OpenGL drawing,
and an architecture that is designed to let you focus on building custom and
highly interactive applications as quickly and easily as possible.

Thanks to PyMT's pure Python interface, you can take advantage of its highly
dynamic nature and use any of the thousands of high quality Python libraries
out there.
At the same time, performance-critical sections are internally implemented
on the C-level to maximize performance.

See http://pymt.eu for more information.
'''

__version__ = '0.5.2-dev'

import sys
import getopt
import os
import shutil
from pymt.logger import pymt_logger, LOG_LEVELS

# internals for post-configuration
__pymt_post_configuration = []
def pymt_configure():
    '''Call post-configuration of PyMT.
    This function must be called in case of you create yourself the window.
    '''
    for callback in __pymt_post_configuration:
        callback()

def pymt_register_post_configuration(callback):
    '''Register a function to be call when pymt_configure() will be called.

    .. warning::
        Internal use only.
    '''
    __pymt_post_configuration.append(callback)

# Start !
pymt_logger.info('PyMT v%s' % (__version__))

#: Global settings options for pymt
pymt_options = {
    'use_accelerate': True,
    'shadow_window': True,
    'window': ('pygame', 'glut'),
    'text': ('pil', 'cairo', 'pygame'),
    'video': ('gstreamer', 'pyglet' ),
    'audio': ('pygame', 'gstreamer', ),
    'image': ('pil', 'pygame'),
    'camera': ('opencv', 'gstreamer', 'videocapture'),
    'svg': ('squirtle',),
    'spelling': ('enchant', 'osxappkit',),
}

# Read environment
for option in pymt_options:
    key = 'PYMT_%s' % option.upper()
    if key in os.environ:
        try:
            if type(pymt_options[option]) in (list, tuple):
                pymt_options[option] = (str(os.environ[key]),)
            else:
                pymt_options[option] = os.environ[key].lower() in \
                    ('true', '1', 'yes', 'yup')
        except Exception:
            pymt_logger.warning('Core: Wrong value for %s'
                                'environment key' % key)
            pymt_logger.exception('')

# Extract all needed path in pymt
#: PyMT directory
pymt_base_dir        = os.path.dirname(sys.modules[__name__].__file__)
#: PyMT external libraries directory
pymt_libs_dir        = os.path.join(pymt_base_dir, 'lib')
#: PyMT modules directory
pymt_modules_dir     = os.path.join(pymt_base_dir, 'modules')
#: PyMT data directory
pymt_data_dir        = os.path.join(pymt_base_dir, 'data')
#: PyMT input provider directory
pymt_providers_dir   = os.path.join(pymt_base_dir, 'input', 'providers')
#: PyMT icons config path (don't remove last '')
pymt_icons_dir        = os.path.join(pymt_data_dir, 'icons', '')
#: PyMT user-home storage directory
pymt_home_dir        = None
#: PyMT configuration filename
pymt_config_fn       = None
#: PyMT user modules directory
pymt_usermodules_dir = None

# Add lib in pythonpath
sys.path           = [pymt_libs_dir] + sys.path

# Don't go further if we generate documentation
if os.path.basename(sys.argv[0]) in ('sphinx-build', 'autobuild.py'):
    os.environ['PYMT_DOC'] = '1'
if os.path.basename(sys.argv[0]) in ('sphinx-build', ):
    os.environ['PYMT_DOC_INCLUDE'] = '1'
if not 'PYMT_DOC_INCLUDE' in os.environ:

    # Configuration management
    user_home_dir = os.path.expanduser('~')
    pymt_home_dir = os.path.join(user_home_dir, '.pymt')
    pymt_config_fn = os.path.join(pymt_home_dir, 'config')
    if not os.path.exists(pymt_home_dir):
        os.mkdir(pymt_home_dir)
    pymt_usermodules_dir = os.path.join(pymt_home_dir, 'mods')
    if not os.path.exists(pymt_usermodules_dir):
        os.mkdir(pymt_usermodules_dir)
    icon_dir = os.path.join(pymt_home_dir, 'icon')
    if not os.path.exists(icon_dir):
        shutil.copytree(os.path.join(pymt_data_dir, 'logo'), icon_dir)

    # configuration
    from pymt.config import *

    # Set level of logger
    level = LOG_LEVELS.get(pymt_config.get('pymt', 'log_level'))
    pymt_logger.setLevel(level=level)

    # Disable pyOpenGL auto GL Error Check?
    gl_check = pymt_config.get('pymt', 'gl_error_check')
    if gl_check.lower() in ['0', 'false', 'no']:
        import OpenGL
        OpenGL.ERROR_CHECKING = False

    # save sys argv, otherwize, gstreamer use it and display help..
    sys_argv = sys.argv
    sys.argv = sys.argv[:1]

    # Note: import are done after logger module initialization,
    # and configuration applied to logger.

    # first, compile & use accelerate module
    from pymt.accelerate import *

    # no dependices at all
    from pymt.baseobject import *
    from pymt.exceptions import *
    from pymt.resources import *
    from pymt.cache import Cache

    # system dependices
    from pymt.utils import *
    from pymt.event import *
    from pymt.clock import *
    from pymt.texture import *
    from pymt.plugin import *

    # internal dependices
    from pymt.graphx import *
    from pymt.vector import *
    from pymt.geometry import *

    # dependices
    from pymt.core import *
    from pymt.modules import *
    from pymt.input import *
    from pymt.base import *

    # after dependices
    from pymt.gesture import *
    from pymt.obj import OBJ
    from pymt.loader import *

    # widgets
    from pymt.ui import *

    # Can be overrided in command line
    try:
        opts, args = getopt.getopt(sys_argv[1:], 'hp:fkawFem:sn',
            ['help', 'fullscreen', 'windowed', 'fps', 'event',
             'module=', 'save', 'fake-fullscreen', 'auto-fullscreen',
             'display=', 'size='])

        # set argv to the non-read args
        sys.argv = sys_argv[0:1] + args

        need_save = False
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                pymt_usage()
                sys.exit(0)
            elif opt in ('-p', '--provider'):
                pid, args = arg.split(':', 1)
                pymt_config.set('input', pid, args)
            elif opt in ('-a', '--auto-fullscreen'):
                pymt_config.set('graphics', 'fullscreen', 'auto')
            elif opt in ('-k', '--fake-fullscreen'):
                pymt_config.set('graphics', 'fullscreen', 'fake')
            elif opt in ('-f', '--fullscreen'):
                pymt_config.set('graphics', 'fullscreen', '1')
            elif opt in ('-w', '--windowed'):
                pymt_config.set('graphics', 'fullscreen', '0')
            elif opt in ('-F', '--fps'):
                pymt_config.set('pymt', 'show_fps', '1')
            elif opt in ('-e', '--eventstats'):
                pymt_config.set('pymt', 'show_eventstats', '1')
            elif opt in ('--size', ):
                w, h = str(arg).split('x')
                pymt_config.set('graphics', 'width', w)
                pymt_config.set('graphics', 'height', h)
            elif opt in ('--display', ):
                pymt_config.set('graphics', 'display', str(arg))
            elif opt in ('-m', '--module'):
                if str(arg) == 'list':
                    pymt_modules.usage_list()
                    sys.exit(0)
                args = arg.split(':', 1)
                if len(args) == 1:
                    args += ['']
                pymt_config.set('modules', args[0], args[1])
            elif opt in ('-s', '--save'):
                need_save = True
            elif opt in ('-n', ):
                pymt_options['shadow_window'] = False

        if need_save:
            try:
                with open(pymt_config_fn, 'w') as fd:
                    pymt_config.write(fd)
            except Exception, e:
                pymt_logger.exception('Core: error while saving default'
                                      'configuration file')
            pymt_logger.info('Core: PyMT configuration saved.')
            sys.exit(0)

        # last initialization
        if pymt_options['shadow_window']:
            pymt_logger.debug('Core: Creating PyMT Window')
            shadow_window = MTWindow()
            pymt_configure()

    except getopt.GetoptError, err:
        pymt_logger.error('Core: %s' % str(err))
        pymt_usage()
        sys.exit(2)

# cleanup namespace
if not 'PYMT_DOC_INCLUDE' in os.environ:
    del level, need_save, opts, args
del sys, getopt, os, key
