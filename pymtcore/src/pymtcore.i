%module(directors="1") pymtcore

%{
#define SWIG_FILE_WITH_INIT
#include <iostream>
#include <vector>
#include "Python.h"
%}

%feature("director");

%include "vector.i"
%include "image.i"
%include "texture.i"
%include "corewidget.i"
%include "widget.i"
%include "corewindow.i"
