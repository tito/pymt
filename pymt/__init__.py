'''
PyMT: multitouch toolkit

PyMT is a python module for developing multi-touch enabled media rich applications.

Currently the aim is to allow for quick and easy interaction design and rapid prototype development. There is also a focus on logging tasks or sessions of user interaction to quantitative data and the analysis/visualization of such data.

You can visit http://pymt.txzone.net/ for more informations !
'''

__version__ = '0.4.0a3'

from ConfigParser import ConfigParser
import sys
import getopt
import os
from logger import pymt_logger, LOG_LEVELS

# Version number of current configuration format
PYMT_CONFIG_VERSION = 4

# Global settings options for pymt
options = {
    'shadow_window': True,
    'window': ('pygame', 'glut'),
    'text': ('pil', 'cairo', 'pygame'),
    'video': ('gstreamer', 'pyglet' ),
    'audio': ('pygame', ),
    'image': ('pil', 'pygame'),
    'camera': ('opencv', 'gstreamer', 'videocapture'),
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
            pymt_logger.warning('Core: Wrong value for %s environment key' % key)
            pymt_logger.exception('')

# Include lib as new module.
pymt_base_dir = os.path.dirname(sys.modules[__name__].__file__)
pymt_libs_dir = os.path.join(pymt_base_dir, 'lib')
pymt_modules_dir = os.path.join(pymt_base_dir, 'modules')
pymt_data_dir = os.path.join(pymt_base_dir, 'data')
pymt_providers_dir = os.path.join(pymt_base_dir, 'input', 'providers')
sys.path = [pymt_libs_dir] + sys.path

# Don't go further if we generate documentation
if os.path.basename(sys.argv[0]) in ('sphinx-build', 'autobuild.py'):
    os.environ['PYMT_DOC'] = '1'
if os.path.basename(sys.argv[0]) in ('sphinx-build', ):
    os.environ['PYMT_DOC_INCLUDE'] = '1'
if not 'PYMT_DOC_INCLUDE' in os.environ:

    # Configuration management
    pymt_home_dir = os.path.expanduser('~/.pymt/')
    pymt_config_fn = os.path.join(pymt_home_dir, 'config')
    if not os.path.exists(pymt_home_dir):
        os.mkdir(pymt_home_dir)
    pymt_usermodules_dir = os.path.expanduser('~/.pymt/mods/')
    if not os.path.exists(pymt_usermodules_dir):
        os.mkdir(pymt_usermodules_dir)


    #
    # Read, analyse configuration file
    # Support upgrade of older config file version
    # FIXME: move configuration part in another file
    #

    class PyMTConfigParser(ConfigParser):
        def setdefault(self, section, option, value):
            if self.has_option(section, option):
                return
            self.set(section, option, value)
        def getdefault(self, section, option, defaultvalue):
            if not self.has_section(section):
                return defaultvalue
            if not self.has_option(section, option):
                return defaultvalue
            return self.getint(section, option)
        def adddefaultsection(self, section):
            if self.has_section(section):
                return
            self.add_section(section)


    # Create default configuration
    pymt_config = PyMTConfigParser()

    # Read config file if exist
    if os.path.exists(pymt_config_fn):
        try:
            pymt_config.read(pymt_config_fn)
        except Exception, e:
            pymt_logger.exception('Core: error while reading local configuration')

    pymt_config_version = pymt_config.getdefault('pymt', 'config_version', 0)

    # Add defaults section
    pymt_config.adddefaultsection('pymt')
    pymt_config.adddefaultsection('keyboard')
    pymt_config.adddefaultsection('graphics')
    pymt_config.adddefaultsection('input')
    pymt_config.adddefaultsection('dump')
    pymt_config.adddefaultsection('modules')

    # Upgrade default configuration until having the current version
    need_save = False
    if pymt_config_version != PYMT_CONFIG_VERSION:
        pymt_logger.warning('Config: Older configuration version detected (%d instead of %d)' % (
                            pymt_config_version, PYMT_CONFIG_VERSION))
        pymt_logger.warning('Config: Upgrading configuration in progress.')
        need_save = True

    while pymt_config_version != PYMT_CONFIG_VERSION:
        pymt_logger.debug('Config: Upgrading from %d' % pymt_config_version)

        # Versionning introduced in version 0.4.
        if pymt_config_version == 0:

            pymt_config.setdefault('pymt', 'show_fps', '0')
            pymt_config.setdefault('pymt', 'show_eventstats', '0')
            pymt_config.setdefault('pymt', 'log_level', 'info')
            pymt_config.setdefault('pymt', 'double_tap_time', '250')
            pymt_config.setdefault('pymt', 'double_tap_distance', '20')
            pymt_config.setdefault('pymt', 'enable_simulator', '1')
            pymt_config.setdefault('pymt', 'ignore', '[]')
            pymt_config.setdefault('keyboard', 'layout', 'qwerty')
            pymt_config.setdefault('graphics', 'fbo', 'hardware')
            pymt_config.setdefault('graphics', 'fullscreen', '0')
            pymt_config.setdefault('graphics', 'width', '640')
            pymt_config.setdefault('graphics', 'height', '480')
            pymt_config.setdefault('graphics', 'vsync', '1')
            pymt_config.setdefault('graphics', 'display', '-1')
            pymt_config.setdefault('graphics', 'line_smooth', '1')
            pymt_config.setdefault('dump', 'enabled', '0')
            pymt_config.setdefault('dump', 'prefix', 'img_')
            pymt_config.setdefault('dump', 'format', 'jpeg')
            pymt_config.setdefault('input', 'default', 'tuio,0.0.0.0:3333')
            pymt_config.setdefault('input', 'mouse', 'mouse')

            # activate native input provider in configuration
            if sys.platform == 'darwin':
                pymt_config.setdefault('input', 'mactouch', 'mactouch')
            elif sys.platform == 'win32':
                pymt_config.setdefault('input', 'wm_touch', 'wm_touch')
                pymt_config.setdefault('input', 'wm_pen', 'wm_pen')

        elif pymt_config_version == 1:
            # add retain postproc configuration
            pymt_config.setdefault('pymt', 'retain_time', '0')
            pymt_config.setdefault('pymt', 'retain_distance', '50')

        elif pymt_config_version == 2:
            # add show cursor
            pymt_config.setdefault('graphics', 'show_cursor', '1')

        elif pymt_config_version == 3:
            # add multisamples
            pymt_config.setdefault('graphics', 'multisamples', '2')

        else:
            # for future.
            pass

        # Pass to the next version
        pymt_config_version += 1

    # Said to pymt_config that we've upgrade to latest version.
    pymt_config.set('pymt', 'config_version', PYMT_CONFIG_VERSION)

    if not os.path.exists(pymt_config_fn) or need_save:
        try:
            with open(pymt_config_fn, 'w') as fd:
                pymt_config.write(fd)
        except Exception, e:
            pymt_logger.exception('Core: error while saving default configuration file')


    # Set level of logger
    level = LOG_LEVELS.get(pymt_config.get('pymt', 'log_level'))
    pymt_logger.setLevel(level=level)

    # save sys argv, otherwize, gstreamer use it and display help..
    sys_argv = sys.argv
    sys.argv = sys.argv[:1]

    # Note: import are done after logger module initialization,
    # and configuration applied to logger.

    # no dependices at all
    from baseobject import *
    from exceptions import *
    from cache import Cache

    # system dependices
    from utils import *
    from time import *
    from event import *
    from clock import *
    from texture import *
    from plugin import *

    # internal dependices
    from graphx import *
    from vector import *

    # dependices
    from core import *
    from modules import *
    from input import *
    from base import *

    # after dependices
    from gesture import *
    from obj import OBJ

    # widgets
    from ui import *

    #from plugin import *
    #from loader import *


    # Can be overrided in command line
    try:
        opts, args = getopt.getopt(sys_argv[1:], 'hp:fwFem:s',
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
                pymt_config.set('graphics', 'fullscreen', 'auto')
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
                args = arg.split(':', 1)
                if len(args) == 1:
                    args += ['']
                pymt_config.set('modules', args[0], args[1])
            elif opt in ['-s', '--save']:
                need_save = True

        if need_save:
            try:
                with open(pymt_config_fn, 'w') as fd:
                    pymt_config.write(fd)
            except Exception, e:
                pymt_logger.exception('Core: error while saving default configuration file')
            pymt_logger.info('Core: PyMT configuration saved.')
            sys.exit(0)

        # last initialization
        if options['shadow_window']:
            pymt_logger.debug('Core: Creating PyMT Window')
            shadow_window = MTWindow()

    except getopt.GetoptError, err:
        pymt_logger.error('Core: %s' % str(err))
        pymt_usage()
        sys.exit(2)
