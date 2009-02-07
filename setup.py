from distutils.core import setup
from distutils.sysconfig import get_python_lib
import sys
import os


sys.argv.append('install')
pylib = get_python_lib()
svgs = ['pymt/data/icons/svg/' + s for s in os.listdir('pymt/data/icons/svg') if s.endswith('svg')]
pngs = ['pymt/data/icons/' + p for p in os.listdir('pymt/data/icons') if p.endswith('png')]

setup (name='pymt',
      version='0.1',
      author='Thomas Hansen',
      author_email='thomas.hansen@gmail.com',
      url='http://code.google.com/p/pymt/',
      license='GPL',
      packages=['pymt', 'pymt.osc', 'pymt.ui'],
      data_files=[(pylib+'/pymt/data/icons', pngs), (pylib+'/pymt/data/icons/svg', svgs)]
)
