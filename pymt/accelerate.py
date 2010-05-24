'''
Accelerate: wrapper around _accelerate module, written in cython

This module increase internal performance of PyMT.
'''

__all__ = ('accelerate', )

from pymt import options, pymt_logger

#: Accelerate module (None mean that the module is not available)
accelerate = None

# try to use cython is available
if options.get('use_accelerate'):
    try:
        import pyximport
        pyximport.install()
    except ImportError:
        pyximport = None
        pymt_logger.warning('Core: unable to use pyximport (not installed ?')
        pymt_logger.exception('')

    if pyximport:
        try:
            pymt_logger.info('Core: Compile accelerate module')
            import _accelerate as accelerate
            pymt_logger.info('Core: Accelerate module compiled')
        except ImportError:
            pymt_logger.warning('Core: Error while compiling accelerate module')
            pymt_logger.warning('Core: No core acceleration available')
else:
    pymt_logger.info('Core: Accelerate module disabled by user')

