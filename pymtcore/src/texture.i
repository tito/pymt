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

%feature("ref")        AbstractImage     "$this->ref();"
%feature("unref")      AbstractImage     "$this->unref();"
%feature("ref")        Texture           "$this->ref();"
%feature("unref")      Texture           "$this->unref();"
%feature("ref")        TextureRegion     "$this->ref();"
%feature("unref")      TextureRegion     "$this->unref();"

%include "texture.h"
