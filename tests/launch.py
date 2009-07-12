import unittest
import os
from pymt import *

if __name__ == '__main__':
    alltests = []
    for file in os.listdir(os.path.join('.', os.path.dirname(__file__))):
        if not file.startswith('test_'):
            continue
        if file[-3:] != '.py':
            continue
        file = file[:-3]
        m = __import__(name=file)
        tests = [getattr(m, test) for test in dir(m) if test[-8:] == 'TestCase']
        pymt_logger.debug('Load %d class(es) from %s', len(tests), file)
        if len(tests):
            alltests += tests

    alltests = [unittest.TestLoader().loadTestsFromTestCase(m) for m in alltests]
    unittest.main()

