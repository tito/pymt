from distutils.core import setup
import sys
import os

# extract version (simulate doc generation, pymt will be not imported)
os.environ['PYMT_DOC_INCLUDE'] = '1'
import pymt

# extracts all examples files except sandbox
examples = []
examples_allowed_ext = ('readme', 'py', 'wav', 'png', 'jpg', 'svg',
                        'avi', 'gif', 'txt', 'ttf', 'obj', 'mtl')
for root, subFolders, files in os.walk('examples'):
    if 'sandbox' in root:
        continue
    for file in files:
        ext = file.split('.')[-1].lower()
        if ext not in examples_allowed_ext:
            continue
        examples.append(os.path.join(root,file))

# setup !
setup(
    name='PyMT',
    version=pymt.__version__,
    author='PyMT Crew',
    author_email='pymt-dev@googlegroups.com',
    url='http://pymt.txzone.net/',
    license='LGPL',
    description='A framework for making accelerated multitouch UI',
    packages=[
        'pymt',
        'pymt.graphx',
        'pymt.core',
        'pymt.core.audio',
        'pymt.core.camera',
        'pymt.core.image',
        'pymt.core.text',
        'pymt.core.video',
        'pymt.input',
        'pymt.input.postproc',
        'pymt.input.providers',
        'pymt.lib',
        'pymt.lib.cssutils',
        'pymt.lib.cssutils.css',
        'pymt.lib.cssutils.stylesheets',
        'pymt.lib.osc',
        'pymt.modules',
        'pymt.ui',
        'pymt.ui.widgets',
        'pymt.ui.widgets.composed',
        'pymt.ui.widgets.form',
        'pymt.ui.widgets.layout',
        'pymt.ui.window',
        'pymt.tools',
        'pymt.tools.designerapp',
    ],
    package_dir={'pymt': 'pymt'},
    package_data={'pymt': [
        'data/icons/filetype/*.png',
        'data/icons/svg/*.svg',
        'data/icons/*.png',
        'data/*.css',
        'data/*.png',
        'data/*.ttf',
        'tools/designerapp/icons/*.png']
    },
    data_files=[('share/pymt-examples', examples)],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: BSD :: FreeBSD',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Artistic Software',
        'Topic :: Games/Entertainment',
        'Topic :: Multimedia :: Graphics :: 3D Rendering',
        'Topic :: Multimedia :: Graphics :: Capture :: Digital Camera',
        'Topic :: Multimedia :: Graphics :: Presentation',
        'Topic :: Multimedia :: Graphics :: Viewers',
        'Topic :: Multimedia :: Sound/Audio :: Players :: MP3',
        'Topic :: Multimedia :: Video :: Display',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: User Interfaces',
    ]
)
