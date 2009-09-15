%module(directors="1") pymtcore

%{
#define SWIG_FILE_WITH_INIT
#include "widget.h"
%}

%feature("director");

%include "widget.h"
