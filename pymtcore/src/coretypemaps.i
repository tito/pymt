%typemap(out) Texture *
{
    $result = SWIG_NewPointerObj(SWIG_as_voidptr($1), $1_descriptor, SWIG_POINTER_OWN);
    $1->ref();
}

%typemap(out) float tex_coords[12]
{
    $result = PyTuple_New(12);
    for ( int i = 0; i < 12; i++ )
        PyTuple_SetItem($result, i, PyFloat_FromDouble($1[i]));
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

