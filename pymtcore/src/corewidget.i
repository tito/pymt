%{
#include "corewidget.h"
%}

%typemap(out) double *OutValue {
    PyObject *o, *o2, *o3;
    o = PyFloat_FromDouble(*$1);
    if ((!$result) || ($result == Py_None)) {
        $result = o;
    } else {
        if (!PyTuple_Check($result)) {
            PyObject *o2 = $result;
            $result = PyTuple_New(1);
            PyTuple_SetItem($result,0,o2);
        }
        o3 = PyTuple_New(1);
        PyTuple_SetItem(o3,0,o);
        o2 = $result;
        $result = PySequence_Concat(o2,o3);
        Py_DECREF(o2);
        Py_DECREF(o3);
    }
}

%typemap(in,numinputs=0) double *OutValue(double temp) {
    $1 = &temp;
}

int spam(double a, double b, double *OutValue, double *OutValue);
int MTCoreWidget::to_local(double x, double y, double *OutValue, double *OutValue);

%feature("ref")   MTCoreWidget "$this->ref();"
%feature("unref") MTCoreWidget "$this->unref(1);"

%director MTCoreWidget;
%include "corewidget.h"

%include <std_vector.i>
%template(VectorCoreWidget) std::vector<MTCoreWidget *>;
