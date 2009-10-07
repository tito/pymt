%{
#include "texture.h"
%}

%feature("ref")        AbstractImage     "$this->ref();"
%feature("unref")      AbstractImage     "$this->unref();"
%feature("ref")        Texture           "$this->ref();"
%feature("unref")      Texture           "$this->unref();"
%feature("ref")        TextureRegion     "$this->ref();"
%feature("unref")      TextureRegion     "$this->unref();"

%include "texture.h"
