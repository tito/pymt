#!/usr/bin/env python

"""Setup script for the Vorbis module distribution."""

import os, re, sys, string
from distutils.core import setup
from distutils.extension import Extension

VERSION_MAJOR = 1
VERSION_MINOR = 4
pyvorbis_version = str(VERSION_MAJOR) + '.' + str(VERSION_MINOR)

try:
    import ogg._ogg
except ImportError:
    print '''You must have the Ogg Python bindings
installed in order to build and install
these bindings. Import of ogg._ogg failed.'''
    sys.exit(1)

def get_setup():
    data = {}
    r = re.compile(r'(\S+)\s*?=\s*(.+)')
    
    if not os.path.isfile('Setup'):
        print "No 'Setup' file. Perhaps you need to run the configure script."
        sys.exit(1)

    f = open('Setup', 'r')
    
    for line in f.readlines():
        m = r.search(line)
        if not m:
            print "Error in setup file:", line
            sys.exit(1)
        key = m.group(1)
        val = m.group(2)
        data[key] = val
        
    return data

data = get_setup()

vorbis_include_dir = data['vorbis_include_dir']
vorbis_lib_dir = data['vorbis_lib_dir']
vorbis_libs = string.split(data['vorbis_libs'])

ogg_include_dir = data['ogg_include_dir']
ogg_lib_dir = data['ogg_lib_dir']

vorbismodule = Extension(name='vorbis',
                         sources=['src/vorbismodule.c',
                                  'src/pyvorbisfile.c',
                                  'src/pyvorbiscodec.c',
                                  'src/pyvorbisinfo.c',
                                  'src/vcedit.c',
                                  'src/general.c'],
                         define_macros = [('VERSION', '"%s"' %
                                           pyvorbis_version)],
                         include_dirs=[vorbis_include_dir,
                                       ogg_include_dir],
                         library_dirs=[vorbis_lib_dir,
                                       ogg_lib_dir],
                         libraries=vorbis_libs)

setup ( name = "pyvorbis",
        version = pyvorbis_version,
        description = "A wrapper for the Vorbis libraries.",
        author = "Andrew Chatham",
        author_email = "andrew.chatham@duke.edu",
        url = "http://dulug.duke.edu/~andrew/pyogg",

        packages = ['ogg'],
        package_dir = {'ogg' : 'src'},
        ext_package = 'ogg',
        ext_modules = [vorbismodule])




