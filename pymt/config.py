'''
Config: base for PyMT configuration file
'''

__all__ = ('pymt_config', )

from ConfigParser import ConfigParser
import sys
import os
from pymt.logger import pymt_logger
from pymt import pymt_home_dir, pymt_config_fn, logger

# Version number of current configuration format
PYMT_CONFIG_VERSION = 12

#: PyMT configuration object
pymt_config = None

if not 'PYMT_DOC_INCLUDE' in os.environ:

    #
    # Read, analyse configuration file
    # Support upgrade of older config file version
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

        def write(self):
            with open(pymt_config_fn, 'w') as fd:
                ConfigParser.write(self, fd)

    # Create default configuration
    pymt_config = PyMTConfigParser()

    # Read config file if exist
    if os.path.exists(pymt_config_fn):
        try:
            pymt_config.read(pymt_config_fn)
        except Exception, e:
            pymt_logger.exception('Core: error while reading local'
                                  'configuration')

    pymt_config_version = pymt_config.getdefault('pymt', 'config_version', 0)

    # Add defaults section
    pymt_config.adddefaultsection('pymt')
    pymt_config.adddefaultsection('keyboard')
    pymt_config.adddefaultsection('graphics')
    pymt_config.adddefaultsection('input')
    pymt_config.adddefaultsection('dump')
    pymt_config.adddefaultsection('modules')
    pymt_config.adddefaultsection('widgets')

    # Upgrade default configuration until having the current version
    need_save = False
    if pymt_config_version != PYMT_CONFIG_VERSION:
        pymt_logger.warning('Config: Older configuration version detected'
                            '(%d instead of %d)' % (
                            pymt_config_version, PYMT_CONFIG_VERSION))
        pymt_logger.warning('Config: Upgrading configuration in progress.')
        need_save = True

    while pymt_config_version < PYMT_CONFIG_VERSION:
        pymt_logger.debug('Config: Upgrading from %d' % pymt_config_version)

        # Versionning introduced in version 0.4.
        if pymt_config_version == 0:

            pymt_config.setdefault('pymt', 'show_fps', '0')
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

        elif pymt_config_version == 4:
            # remove mouse simulator
            pymt_config.remove_option('pymt', 'enable_simulator')

        elif pymt_config_version == 5:
            # add fixccv
            pymt_config.setdefault('pymt', 'fixccv', '0')

        elif pymt_config_version == 6:
            # add log_file format
            pymt_config.setdefault('pymt', 'log_enable', '1')
            pymt_config.setdefault('pymt', 'log_dir', 'logs')
            pymt_config.setdefault('pymt', 'log_name', 'pymt_%y-%m-%d_%_.txt')

        elif pymt_config_version == 7:
            # add option to turn off pyOpenGL Error Checking
            pymt_config.setdefault('pymt', 'gl_error_check', '1')

        elif pymt_config_version == 8:
            pymt_config.setdefault('pymt', 'jitter_distance', '0')
            pymt_config.setdefault('pymt', 'jitter_ignore_devices',
                                   'mouse,mactouch,')

        elif pymt_config_version == 9:
            pymt_config.setdefault('widgets', 'keyboard_type', 'virtual')

        elif pymt_config_version == 10:
            pymt_config.setdefault('widgets', 'list_friction', '10')
            pymt_config.setdefault('widgets', 'list_friction_bound', '20')
            pymt_config.setdefault('widgets', 'list_trigger_distance', '5')

        elif pymt_config_version == 11:
            pymt_config.setdefault('graphics', 'window_icon', os.path.join(pymt_home_dir, 'icon', 'pymt32.png') )
        else:
            # for future.
            break

        # Pass to the next version
        pymt_config_version += 1

# Said to pymt_config that we've upgrade to latest version.
    pymt_config.set('pymt', 'config_version', PYMT_CONFIG_VERSION)

# Now, activate log file
    if pymt_config.getint('pymt', 'log_enable'):
        logger.pymt_logfile_activated = True

# If no configuration exist, write the default one.
    if not os.path.exists(pymt_config_fn) or need_save:
        try:
            pymt_config.write()
        except Exception, e:
            pymt_logger.exception('Core: error while saving default configuration file')
