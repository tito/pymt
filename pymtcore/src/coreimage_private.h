#ifndef __COREIMAGE_PRIVATE
#define __COREIMAGE_PRIVATE

#include <vector>
#include "coreimage.h"

typedef bool (*loader_t)(CoreImage &);

extern std::vector<loader_t> loaders;

#endif
