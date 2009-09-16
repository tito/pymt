%module(directors="1") pymtcore

%{
#define SWIG_FILE_WITH_INIT
#include "widget.h"
%}

%feature("director");

%feature("ref")   MTWidget "$this->ref();"
%feature("unref") MTWidget "$this->unref(1);"

%include "widget.h"
