'''
SVG widget: widget that display an svg image
'''
__all__ = ('MTSvg', 'MTSvgButton')

import os

from pymt import pymt_data_dir
from pymt.logger import pymt_logger
from pymt.ui.widgets.widget import MTWidget
from pymt.ui.widgets.button import MTButton

squirtle = None

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
        global squirtle
        if squirtle is None:
            import squirtle
        # TODO remove this ugly code, improve loader for this
        try:
            if self.rawdata is None:
                pymt_logger.debug('SVG: loading %s' % filename)
                self.svg = squirtle.SVG(filename)
            else:
                pymt_logger.debug('SVG: loading %s from rawdata' % filename)
                self.svg = squirtle.SVG(filename=filename, rawdata=self.rawdata)
        except Exception:
            try:
                svgpath = os.path.join(pymt_data_dir, 'icons/svg')
                pymt_logger.exception('SVG: unable to load %s' % filename)
                pymt_logger.warning('SVG: trying %s' % (svgpath + filename))
                self.svg = squirtle.SVG(os.path.join(svgpath, filename))
            except Exception:
                pymt_logger.exception('SVG: unable to load file %s' % filename)
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
        global squirtle
        if squirtle is None:
            import squirtle
		# TODO remove this ugly code, improve loader for this
        try:
            pymt_logger.debug('SVGButton: loading %s' % filename)
            self.svg = squirtle.SVG(filename)
        except Exception, e:
            try:
                svgpath = os.path.join(pymt_data_dir, 'icons/svg')
                pymt_logger.exception('SVGButton: unable to load %s' % filename)
                pymt_logger.warning('SVGButton: trying %s' % (
                    svgpath + filename))
                self.svg = squirtle.SVG(os.path.join(svgpath, filename))
            except Exception, e:
                pymt_logger.exception('SVGButton: unable to load file %s' % filename)
        self._filename = filename
        self.size = (self.svg.width, self.svg.height)
    filename = property(_get_filename, _set_filename)
