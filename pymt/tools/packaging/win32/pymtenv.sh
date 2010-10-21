#!/bin/sh
export PYMT_PORTABLE_ROOT=`dirname $0`
echo bootstrapping PyMT @ $PYMT_PORTABLE_ROOT

if [ "X$PYMT_PATHS_INITIALIZED" != "X1" ]; then

echo Setting Environment Variables:
echo #################################

export GST_REGISTRY=$PYMT_PORTABLE_ROOT/gstreamer/registry.bin
echo GST_REGISTRY is $GST_REGISTRY
echo ----------------------------------

export GST_PLUGIN_PATH=$PYMT_PORTABLE_ROOT/gstreamer/lib/gstreamer-0.10
echo GST_PLUGIN_PATH is $GST_PLUGIN_PATH
echo ----------------------------------

export PATH=$PYMT_PORTABLE_ROOT:$PYMT_PORTABLE_ROOT/Python:$PYMT_PORTABLE_ROOT/gstreamer/bin:$PYMT_PORTABLE_ROOT/MinGW/bin:$PATH
echo PATH is $PATH
echo ----------------------------------

set PYTHONPATH=$PYMT_PORTABLE_ROOT/pymt:$PYTHONPATH
echo PYTHONPATH is $PYTHONPATH

export PYMT_PATHS_INITIALIZED=1
echo ##################################

fi

echo done bootstraping pymt...have fun!
echo
