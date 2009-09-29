%{
#include "corewidget.h"
%}

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

%typemap(directorin) PyObject *data
{
    $input = data;
    Py_INCREF(data);
}


%typemap(directorout) pos2d
{
    if ( !PySequence_Check($1) )
        throw std::invalid_argument("a sequence is expected");
    $result.x = PyFloat_AsDouble(PySequence_GetItem($1, 0));
    $result.y = PyFloat_AsDouble(PySequence_GetItem($1, 1));
}

%typemap(out) pos2d
{
    PyObject *ox, *oy;
    ox = PyFloat_FromDouble($1.x);
    oy = PyFloat_FromDouble($1.y);
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
%feature("shadow") CoreWidget::_get_center() %{
def _get_center(*args): return $action(*args)
if _newclass:pos = property(_get_pos, _set_pos)
__swig_setmethods__["pos"] = _pymtcore.CoreWidget__set_pos
__swig_getmethods__["pos"] = _pymtcore.CoreWidget__get_pos
if _newclass:size = property(_get_size, _set_size)
__swig_setmethods__["size"] = _pymtcore.CoreWidget__set_size
__swig_getmethods__["size"] = _pymtcore.CoreWidget__get_size
if _newclass:center = property(_get_center, _set_center)
__swig_setmethods__["center"] = _pymtcore.CoreWidget__set_center
__swig_getmethods__["center"] = _pymtcore.CoreWidget__get_center
if _newclass:x = property(_get_x, _set_x)
__swig_setmethods__["x"] = _pymtcore.CoreWidget__set_x
__swig_getmethods__["x"] = _pymtcore.CoreWidget__get_x
if _newclass:y = property(_get_y, _set_y)
__swig_setmethods__["y"] = _pymtcore.CoreWidget__set_y
__swig_getmethods__["y"] = _pymtcore.CoreWidget__get_y
if _newclass:width = property(_get_width, _set_width)
__swig_setmethods__["width"] = _pymtcore.CoreWidget__set_width
__swig_getmethods__["width"] = _pymtcore.CoreWidget__get_width
if _newclass:height = property(_get_height, _set_height)
__swig_setmethods__["height"] = _pymtcore.CoreWidget__set_height
__swig_getmethods__["height"] = _pymtcore.CoreWidget__get_height
%}


%feature("ref")   CoreWidget "$this->ref();"
%feature("unref") CoreWidget "$this->unref(1);"

%director CoreWidget;
%include "corewidget.h"

/* inline needed for Swig::Director things :/
*/
%inline %{
void CoreWidget::ref(void)
{
    // automaticly disown the object if it's handled here
    // we handle the reference counting ourself.
    Swig::Director *director = dynamic_cast<Swig::Director *>(this);

    this->__ref_count++;

    if ( director )
        director->swig_disown();
}
%}

%include <std_vector.i>
%template(VectorCoreWidget) std::vector<CoreWidget *>;

