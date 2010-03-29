__all__ = ('test', 'test_runpymt', 'test_image')

def test_image():
    pass

def test_runpymt(*largs, **kwargs):
    from pymt import runTouchApp, curry, getClock, stopTouchApp
    kwargs.setdefault('frame', 1)

    class testinfo(object):
        frame = kwargs.get('frame') + 1

    def test_runpymt_stop(info, *largs):
        info.frame -= 1
        if info.frame == 0:
            stopTouchApp()

    getClock().schedule_interval(curry(test_runpymt_stop, testinfo), 0)
    runTouchApp(*largs)

def test(cond):
    '''Test a condition, and print the result on the screen'''
    import sys
    import inspect
    frame = sys._current_frames().values()[0]
    callers = inspect.getouterframes(frame)
    caller = callers[1]
    info = inspect.getframeinfo(caller[0])
    code = info.code_context[0].replace('\n','').strip()
    if cond:
        testresult(code, 'OK')
    else:
        testresult(code, 'Failed')

def testresult(code, ret):
    '''Print a result on the screen'''
    import os, sys
    print '%-25s %-35s %4s' % (
        '%s:%s' % (os.environ['__modname'][5:],
                   os.environ['__testname'][9:]),
        code,
        ret
    )

def _set_testinfo(a, b):
    import os
    os.environ['__modname'] = a
    os.environ['__testname'] = b


if __name__ == '__main__':
    import os
    import sys

    def testrun(modname, testname):
        _set_testinfo(modname, testname)
        mod = __import__(modname)
        getattr(mod, testname)()

    def testrun_launch(modname, testname):
        import subprocess
        p = subprocess.Popen(
            ['python', __file__, modname, testname],
            stderr=subprocess.PIPE
        )
        p.communicate()

    if len(sys.argv) == 3:
        modname = sys.argv[1][:-3]
        testname = sys.argv[2]
        testrun(modname, testname)
    else:
        current_dir = os.path.dirname(__file__)
        if current_dir == '':
            current_dir = '.'
        for modname in os.listdir(current_dir):
            if not modname.startswith('test_'):
                continue
            if modname[-3:] != '.py':
                continue
            mod = __import__(modname[:-3])
            for testname in dir(mod):
                if not testname.startswith('unittest_'):
                    continue
                testrun_launch(modname, testname)
