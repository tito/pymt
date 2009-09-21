%module(directors="1") pymtcore

%{
#define SWIG_FILE_WITH_INIT
#include <iostream>
#include <vector>
#include "Python.h"
%}

%feature("director");
%feature("director:except") {
    if ($error != NULL) {
        throw Swig::DirectorMethodException();
    }
}

%exception {
    try { $action }
    catch (Swig::DirectorException &e) { SWIG_fail; }
}

%include "vector.i"
%include "image.i"
%include "texture.i"
%include "corewidget.i"
%include "widget.i"
%include "corewindow.i"
%include "utils.i"
