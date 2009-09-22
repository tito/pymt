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

%typemap(directorin) (void *datadispatch)
{
    $input = ((PyObject *)datadispatch);
    Py_INCREF($input);
}

%typemap(directorin) (void *data)
{
    $input = ((PyObject *)data);
    Py_INCREF($input);
}

%typemap(in) (void *datadispatch)
{
    arg3 = $input;
}

%typemap(in) (void *data)
{
    arg2 = $input;
}


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
    static pos2d       p;

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

/* BIG BIG HACK to make properties work.
 *
 * SWIG BUG: attribute.i + director lead to error.
 * When you declare a class from this class,
 * and trying to use a property made with attribute.i,
 * director failed to call the method from this class.
 *
 * Regression test are now working. Don't move that
 * until all the regressing tests work.
 */
%feature("shadow") MTCoreWidget::_get_center() %{
def _get_center(*args): return $action(*args)
if _newclass:pos = property(_get_pos, _set_pos)
__swig_setmethods__["pos"] = _pymtcore.MTCoreWidget__set_pos
__swig_getmethods__["pos"] = _pymtcore.MTCoreWidget__get_pos
if _newclass:size = property(_get_size, _set_size)
__swig_setmethods__["size"] = _pymtcore.MTCoreWidget__set_size
__swig_getmethods__["size"] = _pymtcore.MTCoreWidget__get_size
if _newclass:center = property(_get_center, _set_center)
__swig_setmethods__["center"] = _pymtcore.MTCoreWidget__set_center
__swig_getmethods__["center"] = _pymtcore.MTCoreWidget__get_center
if _newclass:x = property(_get_x, _set_x)
__swig_setmethods__["x"] = _pymtcore.MTCoreWidget__set_x
__swig_getmethods__["x"] = _pymtcore.MTCoreWidget__get_x
if _newclass:y = property(_get_y, _set_y)
__swig_setmethods__["y"] = _pymtcore.MTCoreWidget__set_y
__swig_getmethods__["y"] = _pymtcore.MTCoreWidget__get_y
if _newclass:width = property(_get_width, _set_width)
__swig_setmethods__["width"] = _pymtcore.MTCoreWidget__set_width
__swig_getmethods__["width"] = _pymtcore.MTCoreWidget__get_width
if _newclass:height = property(_get_height, _set_height)
__swig_setmethods__["height"] = _pymtcore.MTCoreWidget__set_height
__swig_getmethods__["height"] = _pymtcore.MTCoreWidget__get_height
%}


%feature("ref")   MTCoreWidget "$this->ref();"
%feature("unref") MTCoreWidget "$this->unref(1);"

%director MTCoreWidget;
%include "corewidget.h"

%include <std_vector.i>
%template(VectorCoreWidget) std::vector<MTCoreWidget *>;

