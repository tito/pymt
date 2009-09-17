%{
#include "corewidget.h"
%}

%extend MTCoreWidget
{

/* Theses typemap can will convert output
 * arg *ox and *oy into a tuple
 */
%typemap(argout) double *ox, double *oy
{
    PyObject *o, *o2, *o3;
    o = PyFloat_FromDouble(*$1);
    if ( (!$result) || ($result == Py_None) )
    {
        $result = o;
    }
    else
    {
        if (!PyTuple_Check($result))
        {
            PyObject *o2 = $result;
            $result = PyTuple_New(1);
            PyTuple_SetItem($result,0,o2);
        }

        o3 = PyTuple_New(1);
        PyTuple_SetItem(o3, 0, o);
        o2 = $result;
        $result = PySequence_Concat(o2,o3);
        Py_DECREF(o2);
        Py_DECREF(o3);
    }
}

%typemap(in,numinputs=0) double *ox(double temp), double *oy(double temp)
{
    $1 = &temp;
}

};

%typemap(out) pos2d&
{
    PyObject *ox, *oy;
    ox = PyFloat_FromDouble($1->x);
    oy = PyFloat_FromDouble($1->y);
    $result = PyTuple_New(2);
    PyTuple_SetItem($result, 0, ox);
    PyTuple_SetItem($result, 1, oy);
}

%typemap(in) pos2d&
{
    pos2d       p;

    if ( !PyTuple_Check($input) )
    {
        PyErr_SetString(PyExc_TypeError, "only tuple are accepted");
        return NULL;
    }
    else if ( PyTuple_Size($input) != 2 )
    {
        PyErr_SetString(PyExc_TypeError, "tuple must have exactly 2 doubles in");
        return NULL;
    }
    else
    {
        p.x = PyFloat_AsDouble(PyTuple_GetItem($input, 0));
        p.y = PyFloat_AsDouble(PyTuple_GetItem($input, 1));
        $1 = &p;
    }
}

%feature("ref")   MTCoreWidget "$this->ref();"
%feature("unref") MTCoreWidget "$this->unref(1);"

%director MTCoreWidget;
%include "corewidget.h"

%include <std_vector.i>
%template(VectorCoreWidget) std::vector<MTCoreWidget *>;

%include <attribute.i>
%attribute(MTCoreWidget, pos2d&, pos, _get_pos, _set_pos);


