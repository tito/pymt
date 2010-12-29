'''
Accelerate: wrapper around _accelerate module, written in cython.

This module increase internal performance of PyMT. User should not use directly
this module. It's designed to enhance performance of :

    * event dispatching (EventDispatcher class)
    * event traversal (Widget class, on_update and on_draw)
    * collide method (Widget class, collide_point)

Accelerate module use cython, and is activated by default, if cython is
correctly installed. Please refer to http://www.cython.org/ about how
to install cython on your environment.

You can control the usage of accelerate module with env variable ::

    PYMT_USE_ACCELERATE

If the env is set to 0, the module will be deactivated.
'''

__all__ = ('accelerate', )

from pymt import pymt_options, pymt_logger

#: Accelerate module (None mean that the module is not available)
accelerate = None

# try to use cython is available
if pymt_options.get('use_accelerate'):
    try:
        import pymt.c_ext.c_accelerate as accelerate
        pymt_logger.info('Core: Using accelerate module')
    except ImportError, e:
        pymt_logger.warning('Core: Accelerate module not available <%s>' % e)
        pymt_logger.warning('Core: Execute "python setup.py build_ext '
                            '--inplace"')
else:
    pymt_logger.info('Core: Accelerate module disabled by user')

