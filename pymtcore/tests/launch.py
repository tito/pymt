import unittest
import os

if __name__ == '__main__':
    alltests = []
    suite = unittest.TestSuite()
    for file in os.listdir(os.path.join('.', os.path.dirname(__file__))):
        if not file.startswith('test_'):
            continue
        if file[-3:] != '.py':
            continue
        file = file[:-3]
        m = __import__(name=file)
        tests = [getattr(m, test) for test in dir(m) if test[-8:] == 'TestCase']
        print '-> Load %d class(es) from %s' % (len(tests), file)
        for test in tests:
            alltests += unittest.TestLoader().loadTestsFromTestCase(test)

    alltests = unittest.TestSuite(alltests)

    print
    unittest.TextTestRunner(verbosity=2).run(alltests)

