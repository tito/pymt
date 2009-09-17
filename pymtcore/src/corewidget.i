%{
#include "corewidget.h"
%}

%feature("ref")   MTCoreWidget "$this->ref();"
%feature("unref") MTCoreWidget "$this->unref(1);"

%director MTCoreWidget;
%include "corewidget.h"

%include <std_vector.i>
%template(VectorCoreWidget) std::vector<MTCoreWidget *>;
