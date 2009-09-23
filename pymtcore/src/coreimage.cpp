#include <iostream>
#include <vector>
#include <stdlib.h>
#include "coreimage.h"
#include "coreimage_private.h"

std::vector<loader_t> loaders;

CoreImage::CoreImage(std::string filename)
{
    this->filename  = filename;
    this->opacity   = 1;
    this->scale     = 1;
    this->anchor_x  = "";
    this->anchor_y  = "";
    this->x         = 0;
    this->y         = 0;
    this->_width    = 0;
    this->_height   = 0;

    this->offset    = 0;
    this->pitch     = 0;
    this->pixels    = NULL;

    this->load();
}

CoreImage::~CoreImage()
{
    if ( this->pixels != NULL )
    {
        free(this->pixels);
        this->pixels = NULL;
    }
}

bool CoreImage::load()
{
    std::vector<loader_t>::iterator i;
    bool ret;

    for ( i = loaders.begin(); i != loaders.end(); i++ )
    {
        ret = (*i)(*this);
        if ( ret == true )
            return true;
    }
    return false;
}

void CoreImage::draw()
{
}

