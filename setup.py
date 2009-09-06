from distutils.core import setup
from distutils.sysconfig import get_python_lib
import sys


sys.argv.append('install')
pylib = get_python_lib()
setup (name='pymt',
      version='0.3',
      author='PyMT Crew'
      author_email='pymt-dev@googlegroups.com',
      url='http://pymt.txzone.net/',
      license='GPL',
      packages=['pymt', 'pymt.lib','pymt.lib.osc', 'pymt.lib.cssutils',
                'pymt.lib.cssutils.css',
                'pymt.lib.cssutils.stylesheets',
                'pymt.graphx', 'pymt.mods',
                'pymt.input', 'pymt.input.providers',
                'pymt.input.postproc',
                'pymt.ui', 'pymt.ui.widgets',
                'pymt.ui.widgets.composed',
                'pymt.ui.widgets.layout', 'pymt.ui.widgets.form'],
      package_dir={'pymt': 'pymt'},
      package_data={'pymt': [
        'data/icons/filetype/*.png',
        'data/icons/svg/*.svg',
        'data/icons/*.png',
        'data/*.png',
        'data/*.ttf']
      }
)
