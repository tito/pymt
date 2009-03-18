'''
SVG widget: widget that display an svg image
'''
__all__ = ['MTSvg']

import os
import squirtle
import pymt
from ...logger import pymt_logger
from ..factory import MTWidgetFactory
from widget import MTWidget

class MTSvg(MTWidget):
    '''Render an svg image

    :Parameters:
        `filename` : str
            Filename of image
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('filename', None)
        if kwargs.get('filename') is None:
            raise Exception('No filename given to MTSvg')
        super(MTSvg, self).__init__(**kwargs)
        self.filename = kwargs.get('filename')

		# TODO this code is not ok, he change some attribute in gl
		# this impact is for all app, not only for squirtle.
        squirtle.setup_gl()

		# TODO remove this ugly code, improve loader for this
        try:
            pymt_logger.debug('loading %s' % self.filename)
            self.svg = squirtle.SVG(self.filename)
        except Exception, e:
            try:
                svgpath = os.path.join(os.path.dirname(pymt.__file__), 'data/icons/svg')
                pymt_logger.exception('unable to load %s' % self.filename)
                pymt_logger.warning('trying %s' % (svgpath + self.filename))
                self.svg = squirtle.SVG(os.path.join(svgpath, self.filename))
            except Exception, e:
                pymt_logger.exception('unable to load file %s' % self.filename)

        self.size = (self.svg.width, self.svg.height)

    def draw(self, **kwargs):
        self.svg.draw(self.x, self.y, **kwargs)

MTWidgetFactory.register('MTSvg', MTSvg)
