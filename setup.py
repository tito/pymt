from distutils.core import setup
import sys


sys.argv.append('install')

setup (name='pymt',
      version='0.1',
      author='Thomas Hansen',
      author_email='thomas.hansen@gmail.com',
      url='http://code.google.com/p/pymt/',
      license='GPL',
      packages=['pymt', 'pymt.osc', 'pymt.ui'],
      data_files=[(sys.prefix+'/Lib/site-packages/pymt/data/icons', ['pymt/data/icons/videoWidgetMute.png', 'pymt/data/icons/videoWidgetPause.png', 'pymt/data/icons/videoWidgetPlay.png'])]
)



