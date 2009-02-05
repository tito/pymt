from distutils.core import setup
from distutils.sysconfig import get_python_lib
import sys


sys.argv.append('install')
pylib = get_python_lib()
setup (name='pymt',
      version='0.1',
      author='Thomas Hansen',
      author_email='thomas.hansen@gmail.com',
      url='http://code.google.com/p/pymt/',
      license='GPL',
      packages=['pymt', 'pymt.osc', 'pymt.ui'],
      data_files=[(pylib+'/pymt/data/icons', ['pymt/data/icons/videoWidgetMute.png', 'pymt/data/icons/videoWidgetPause.png', 'pymt/data/icons/videoWidgetPlay.png',
                'pymt/data/icons/pause.png', 'pymt/data/icons/fullscreen.png', 'pymt/data/icons/stop.png'
                 ])]
)
