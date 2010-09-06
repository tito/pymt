'''
Core: providers for image, text, video, audio, camera...
'''

import os
import pymt

if 'PYMT_DOC' in os.environ:
    # stub for sphinx generation
    def core_select_lib(category, llist):
        pass
    def core_register_libs(category, libs):
        pass
else:
    def core_select_lib(category, llist):
        category = category.lower()
        for option, modulename, classname in llist:
            try:
                # module activated in config ?
                if option not in pymt.pymt_options[category]:
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
                pymt.pymt_logger.info('%s: using <%s> as %s provider' %
                    (category.capitalize(), option, category))
                return cls

            except Exception as e:
                pymt.pymt_logger.warning('%s: Unable to use <%s> as %s'
                     'provider' % ( category.capitalize(), option, category))
                pymt.pymt_logger.debug('', exc_info=e)

        pymt.pymt_logger.critical('%s: Unable to find any valuable %s provider'
              'at all!' % (category.capitalize(),category.capitalize()))


    def core_register_libs(category, libs):
        category = category.lower()
        for option, lib in libs:
            try:
                # module activated in config ?
                if option not in pymt.pymt_options[category]:
                    pymt.pymt_logger.debug('%s: option <%s> ignored by config' %
                        (category.capitalize(), option))
                    continue

                # import module
                __import__(name='%s.%s' % (category, lib),
                           globals=globals(),
                           locals=locals(),
                           fromlist=[lib],
                           level=-1)

            except Exception as e:
                pymt.pymt_logger.warning('%s: Unable to use <%s> as loader!' %
                    (category.capitalize(), option))
                pymt.pymt_logger.debug('', exc_info=e)


from pymt.core.audio import *
from pymt.core.camera import *
from pymt.core.image import *
from pymt.core.text import *
from pymt.core.video import *
from pymt.core.svg import *
from pymt.core.spelling import *

# only after core loading, load extensions
from text.markup import *
