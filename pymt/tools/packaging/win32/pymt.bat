@ECHO off

set pymt_portable_root=%~dp0
ECHO botstrapping PyMT @ %pymt_portable_root%


IF DEFINED pymt_paths_initialized (GOTO :runpymt)

ECHO Setting Environment Variables:
ECHO #################################

set GST_REGISTRY=%pymt_portable_root%gstreamer\registry.bin
ECHO GST_REGISTRY
ECHO %GST_REGISTRY%
ECHO ---------------

set GST_PLUGIN_PATH=%pymt_portable_root%gstreamer\lib\gstreamer-0.10
ECHO GST_PLUGIN_PATH:
ECHO %GST_PLUGIN_PATH%
ECHO ---------------

set PATH=%pymt_portable_root%;%pymt_portable_root%Python;%pymt_portable_root%gstreamer\bin;%pymt_portable_root%MinGW\bin;%PATH%
ECHO PATH:
ECHO %PATH%
ECHO ----------------------------------

set PYTHONPATH=%pymt_portable_root%pymt;%PYTHONPATH%
ECHO PYTHONPATH:
ECHO %PYTHONPATH%
ECHO ----------------------------------

SET pymt_paths_initialized=1
ECHO ##################################


:runpymt

ECHO done bootstraping pymt...have fun!\n
ECHO running "python.exe %*" \n
python.exe  %*