%module(directors="1") pymtcore

%{
#define SWIG_FILE_WITH_INIT
#include "vector.h"
#include "texture.h"
#include "image.h"
#include "widget.h"
%}

%include "vector.h"
%include "texture.h"
%include "image.h"


%feature("director");

%feature("ref")   MTWidget "$this->ref();"
%feature("unref") MTWidget "$this->unref(1);"

%director MTWidget;
%include "widget.h"

%include <std_vector.i>
%template(vecwidget) std::vector<MTWidget *>;
