'''
SVG widget: widget that display an svg image
'''
__all__ = ['MTSvg', 'MTSvgButton']

import os
import squirtle
import pymt
from ...logger import pymt_logger
from ..factory import MTWidgetFactory
from widget import MTWidget
from button import MTButton

class MTSvg(MTWidget):
    '''Render an svg image

    :Parameters:
        `filename` : str
            Filename of image
	`rawdata`  : str
	    The raw data of an SVG file. If given, the filename property will only be used for cache purposes.
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('filename', None)
	kwargs.setdefault('rawdata', None)
        if kwargs.get('filename') is None:
            raise Exception('No filename given to MTSvg')
        super(MTSvg, self).__init__(**kwargs)
	self.rawdata = kwargs.get('rawdata')
        self.filename = kwargs.get('filename')
        self.size = (self.svg.width, self.svg.height)

    def draw(self, **kwargs):
        self.svg.draw(self.x, self.y, **kwargs)

    def _get_filename(self):
        return self._filename
    def _set_filename(self, filename):
		# TODO remove this ugly code, improve loader for this
        try:
            if self.rawdata is None:
		pymt_logger.debug('loading %s' % filename)
		self.svg = squirtle.SVG(filename)
	    else:
		pymt_logger.debug('loading %s from rawdata' % filename)
		self.svg = squirtle.SVG(filename=filename, rawdata=self.rawdata)
        except Exception, e:
            try:
                svgpath = os.path.join(os.path.dirname(pymt.__file__), 'data/icons/svg')
                pymt_logger.exception('unable to load %s' % filename)
                pymt_logger.warning('trying %s' % (svgpath + filename))
                self.svg = squirtle.SVG(os.path.join(svgpath, filename))
            except Exception, e:
                pymt_logger.exception('unable to load file %s' % filename)
        self._filename = filename
        self.size = (self.svg.width, self.svg.height)
    filename = property(_get_filename, _set_filename)

class MTSvgButton(MTButton):
    '''Render an svg image

    :Parameters:
        `filename` : str
            Filename of image
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('filename', None)
        if kwargs.get('filename') is None:
            raise Exception('No filename given to MTSvgButton')
        super(MTSvgButton, self).__init__(**kwargs)
        self.filename = kwargs.get('filename')
        self.size = (self.svg.width, self.svg.height)

    def draw(self, **kwargs):
        self.svg.draw(self.x, self.y, **kwargs)

    def _get_filename(self):
        return self._filename
    def _set_filename(self, filename):
		# TODO remove this ugly code, improve loader for this
        try:
            pymt_logger.debug('loading %s' % filename)
            self.svg = squirtle.SVG(filename)
        except Exception, e:
            try:
                svgpath = os.path.join(os.path.dirname(pymt.__file__), 'data/icons/svg')
                pymt_logger.exception('unable to load %s' % filename)
                pymt_logger.warning('trying %s' % (svgpath + filename))
                self.svg = squirtle.SVG(os.path.join(svgpath, filename))
            except Exception, e:
                pymt_logger.exception('unable to load file %s' % filename)
        self._filename = filename
        self.size = (self.svg.width, self.svg.height)
    filename = property(_get_filename, _set_filename)

MTWidgetFactory.register('MTSvg', MTSvg)
