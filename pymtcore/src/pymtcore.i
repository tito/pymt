%module(directors="1") pymtcore

%{
#define SWIG_FILE_WITH_INIT
#include "widget.h"
%}

%include "widget.h"

%feature("director");

