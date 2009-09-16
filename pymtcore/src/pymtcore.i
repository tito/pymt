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

%feature("ref")   MTCoreWidget "$this->ref();"
%feature("unref") MTCoreWidget "$this->unref(1);"

%director MTCoreWidget;
%include "corewidget.h"
%include "widget.h"

%include <std_vector.i>
%template(VectorCoreWidget) std::vector<MTCoreWidget *>;
