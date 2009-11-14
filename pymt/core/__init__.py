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
                pymt.pymt_logger.debug('%s: option <%s> ignored by config' %
                    (category.capitalize(), option))
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


def core_register_libs(category, libs):
    category = category.lower()
    for option, lib in libs:
        try:
            # module activated in config ?
            if option not in pymt.options[category]:
                pymt.pymt_logger.debug('%s: option <%s> ignored by config' %
                    (category.capitalize(), option))
                continue

            # import module
            mod = __import__(name='%s.%s' % (category, lib),
                             globals=globals(),
                             locals=locals(),
                             fromlist=[lib], level=-1)

        except:
            pymt.pymt_logger.warning('%s: Unable to use <%s> as loader' %
                (category.capitalize(), option))
            pymt.pymt_logger.exception('')


from audio import *
from camera import *
from image import *
from text import *
from video import *
