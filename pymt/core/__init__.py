'''
Core: providers for image, text, video, audio, camera...
'''

import pymt

def core_select_lib(category, llist):
    category = category.lower()
    for option, modulename, classname in llist:
        try:
            # module activated in config ?
            if option not in pymt.options[category]:
                continue

            # import module
            mod = __import__(name='%s.%s' % (category, modulename),
                             globals=globals(),
                             locals=locals(),
                             fromlist=[modulename], level=-1)
            cls = mod.__getattribute__(classname)

            # ok !
            pymt.pymt_logger.info('%s: use <%s> as %s provider' %
                (category.capitalize(), option, category))
            return cls

        except:
            pymt.pymt_logger.warning('%s: Unable to use <%s> as %s provider' %
                (category.capitalize(), option, category))
            pymt.pymt_logger.exception('')

    pymt.pymt_logger.critical('%s: Unable to found a valuable provider !' %
        (category.capitalize()))

from text import *
from image import *
from video import *
