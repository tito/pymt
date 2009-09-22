%module(directors="1") pymtcore

%{
#define SWIG_FILE_WITH_INIT
#include <iostream>
#include <vector>
#include "Python.h"
%}

%include "std_string.i"

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

%include "coreimage.i"
%include "corewidget.i"
%include "corewindow.i"
%include "widget.i"

/**
%include "vector.i"
%include "texture.i"
%include "utils.i"
**/
