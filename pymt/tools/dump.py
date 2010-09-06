'''
Dump tool to have a possibility to log all what we want from user
If they have any troubles with debugging.

Missing:
    compilation support
    acceleration support
'''

import os
import sys
import time
from ConfigParser import ConfigParser
from StringIO import StringIO
from xmlrpclib import ServerProxy
import OpenGL
from OpenGL.GL import *

os.environ['PYMT_SHADOW_WINDOW'] = '0'
import pymt
from pymt import *
from pymt.logger import pymt_logger_history

report = []

def title(t):
    report.append('')
    report.append('=' * 80)
    report.append(t)
    report.append('=' * 80)
    report.append('')

# ----------------------------------------------------------
# Start output debugging
# ----------------------------------------------------------

title('Global')
report.append('OS platform     : %s' % sys.platform)
report.append('Python EXE      : %s' % sys.executable)
report.append('Python Version  : %s' % sys.version)
report.append('Python API      : %s' % sys.api_version)
report.append('PyMT Version    : %s' % pymt.__version__)
report.append('Install path    : %s' % os.path.dirname(pymt.__file__))
report.append('Install date    : %s' % time.ctime(os.path.getctime(pymt.__file__)))

title('OpenGL')
w = MTWindow()
report.append('PyOpenGL Version: %s' % OpenGL.__version__)
report.append('GL Vendor: %s' % glGetString(GL_VENDOR))
report.append('GL Renderer: %s' % glGetString(GL_RENDERER))
report.append('GL Version: %s' % glGetString(GL_VERSION))
ext = glGetString(GL_EXTENSIONS)
if ext is None:
    report.append('GL Extensions: %s' % ext)
else:
    report.append('GL Extensions:')
    for x in ext.split():
        report.append('\t%s' % x)
w.close()

title('Libraries')
def testimport(libname):
    try:
        l = __import__(libname)
        report.append('%-20s exist' % libname)
    except ImportError, e:
        report.append('%-20s is missing' % libname)
for x in (
    'gst',
    'pygame',
    'pygame.midi',
    'numpy',
    'OpenGL',
    'OpenGL.GL',
    'OpenGL.GLU',
    'pymt.ext.accelerate',
    'pyglet',
    'videocapture',
    'squirtle',
    'PIL',
    'cairo',
    'opencv',
    'opencv.cv',
    'opencv.highgui',
    ):
    testimport(x)

title('Core selection')
report.append('Audio  = %s' % SoundLoader._classes)
report.append('Camera = %s' % Camera)
report.append('Image  = %s' % ImageLoader.loaders)
report.append('Text   = %s' % Label)
report.append('Video  = %s' % Video)
report.append('Window = %s' % MTWindow)

title('Configuration')
s = StringIO()
ConfigParser.write(pymt_config, s)
report.extend(s.getvalue().split('\n'))

title('Input availability')
for x in TouchFactory.list():
    report.append(x)

title('Log')
for x in pymt_logger_history.history:
    report.append(x.message)

title('Environ')
for k, v in os.environ.iteritems():
    report.append('%s = %s' % (k, v))

title('Options')
for k, v in pymt_options.iteritems():
    report.append('%s = %s' % (k, v))


report = '\n'.join(report)

print report
print
print

try:
    reply = raw_input('Do you accept to send report to paste.pocoo.org (Y/n) : ')
except EOFError:
    sys.exit(0)

if reply.lower().strip() in ('', 'y'):
    print 'Please wait while sending the report...'

    s = ServerProxy('http://paste.pocoo.org/xmlrpc/')
    r = s.pastes.newPaste('text', report)

    print
    print
    print 'REPORT posted at http://paste.pocoo.org/show/%s/' % r
    print
    print
else:
    print 'No report posted.'

# On windows system, the console leave directly after the end
# of the dump. That's not cool if we want get report url
raw_input('Enter any key to leave.')
