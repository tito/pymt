'''
Fix CCV: Work around the odd behaviour in CCV where every touch outside of the
         calibration grid is mapped to (0,0).
'''
__all__ = ['InputPostprocFixCCV']

import pymt

class InputPostprocFixCCV(object):
    def __init__(self):
        '''
        InputPostprocFixCCV is a post-processor that just removes all touches
        that touch (0,0). It's unlikely that a user hits that precise point on
        purpose. CCV on the other hand maps *every* touch outside of the
        calibration grid to that coordinate, which is very annoying.
        I acknowledge that this has been fixed in some trunk version of CCV, but as
        of now, there are no proper releases for all platforms, hence the workaround.

        The CCV fix can be enabled in the PyMT config file ::
            [pymt]
            fixccv = 1
        '''
        self.active = pymt.pymt_config.getint('pymt', 'fixccv')

    def process(self, events):
        if not self.active:
            return events
        return [(type, touch) for type, touch in events \
                if touch.spos != (0,0)]
