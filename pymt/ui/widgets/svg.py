from __future__ import with_statement
from pyglet import *
from pyglet.gl import *
from pymt.graphx import *
from math import *
from pymt.ui.factory import MTWidgetFactory
from pymt.ui.widgets.widget import MTWidget
from pymt.lib import squirtle
from pymt.vector import *
from pymt.logger import pymt_logger

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
                svgpath = os.path.normpath(os.path.dirname(__file__) + '/../data/icons/svg/')
                pymt_logger.exception('unable to load %s' % self.filename)
                pymt_logger.warning('trying %s' % (svgpath + self.filename))
                self.svg = squirtle.SVG(os.path.join(svgpath, self.filename))
            except Exception, e:
                pymt_logger.exception('unable to load file %s' % self.filename)

        self.size = (self.svg.width, self.svg.height)

    def draw(self, **kwargs):
        self.svg.draw(self.x, self.y, **kwargs)

MTWidgetFactory.register('MTSvg', MTSvg)
