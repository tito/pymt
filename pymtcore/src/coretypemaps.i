%typemap(out) Texture *
{
    $result = SWIG_NewPointerObj(SWIG_as_voidptr($1), $1_descriptor, SWIG_POINTER_OWN);
    $1->ref();
}
