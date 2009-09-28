%{
#include "texture.h"
%}

%extend Texture
{
%typemap(out) double tex_coords[12]
{
    $result = PyTuple_New(12);
    for ( int i = 0; i < 12; i++ )
        PyTuple_SetItem($result, i, PyFloat_FromDouble($1[i]));
}
}

%include "texture.h"
