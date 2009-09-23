#include <iostream>
#include <vector>
#include <exception>
#include <stdlib.h>
#include "coreimage.h"
#include "coreimage_private.h"

std::vector<loader_t> loaders;

GLuint _get_internalformat(std::string &format)
{
    if ( format.length() == 4 )
        return GL_RGBA;
    else if ( format.length() == 3 )
        return GL_RGB;
    else if ( format.length() == 2 )
        return GL_LUMINANCE_ALPHA;
    else if ( format == "A" )
        return GL_ALPHA;
    else if ( format == "L" )
        return GL_LUMINANCE;
    else if ( format == "I" )
        return GL_INTENSITY;
    return GL_RGBA;
}

bool _get_gl_format_and_type(std::string &format, GLuint *outformat, GLuint *outtype)
{
    if ( format == "I" )
    {
        *outformat = GL_LUMINANCE;
        *outtype = GL_UNSIGNED_BYTE;
    }
    else if ( format == "L" )
    {
        *outformat = GL_LUMINANCE;
        *outtype = GL_UNSIGNED_BYTE;
    }
    else if ( format == "LA" )
    {
        *outformat = GL_LUMINANCE_ALPHA;
        *outtype = GL_UNSIGNED_BYTE;
    }
    else if ( format == "R" )
    {
        *outformat = GL_RED;
        *outtype = GL_UNSIGNED_BYTE;
    }
    else if ( format == "G" )
    {
        *outformat = GL_GREEN;
        *outtype = GL_UNSIGNED_BYTE;
    }
    else if ( format == "B" )
    {
        *outformat = GL_BLUE;
        *outtype = GL_UNSIGNED_BYTE;
    }
    else if ( format == "A" )
    {
        *outformat = GL_ALPHA;
        *outtype = GL_UNSIGNED_BYTE;
    }
    else if ( format == "RGB" )
    {
        *outformat = GL_RGB;
        *outtype = GL_UNSIGNED_BYTE;
    }
    else if ( format == "RGBA" )
    {
        *outformat = GL_RGBA;
        *outtype = GL_UNSIGNED_BYTE;
    }
    else
        return false;
    return true;
/**
    else if ( format == "ARGB' and
          gl_info.have_extension('GL_EXT_bgra') and
          gl_info.have_extension('GL_APPLE_packed_pixels')):
        return GL_BGRA, GL_UNSIGNED_INT_8_8_8_8_REV
    else if (format == 'ABGR' and
          gl_info.have_extension('GL_EXT_abgr')):
        return GL_ABGR_EXT, GL_UNSIGNED_BYTE
    else if (format == 'BGR' and
          gl_info.have_extension('GL_EXT_bgra')):
        return GL_BGR, GL_UNSIGNED_BYTE
    else if (format == 'BGRA' and
          gl_info.have_extension('GL_EXT_bgra')):
        return GL_BGRA, GL_UNSIGNED_BYTE
**/
}

CoreImage::CoreImage(std::string filename)
{
    this->filename  = filename;
    this->opacity   = 1;
    this->scale     = 1;
    this->anchor_x  = 0;
    this->anchor_y  = 0;
    this->x         = 0;
    this->y         = 0;
    this->_width    = 0;
    this->_height   = 0;

    this->offset    = 0;
    this->pitch     = 0;
    this->pixels    = NULL;

    this->texture   = NULL;

    this->load();
}

CoreImage::~CoreImage()
{
    if ( this->pixels != NULL )
    {
        free(this->pixels);
        this->pixels = NULL;
    }

    if ( this->texture != NULL )
    {
        delete this->texture;
        this->texture = NULL;
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

Texture *CoreImage::create_texture(bool rectangle)
{
    GLuint  internalformat, format = 0, type = 0;
    Texture *texture;
    void    *data;

    internalformat = _get_internalformat(this->format);
    texture = new Texture(this->_width, this->_height, internalformat, rectangle);
    if ( texture == NULL )
        return NULL;

    if ( _get_gl_format_and_type(this->format, &format, &type) == false )
    {
        // unable to found a suitable format for opengl
        // conversion is needed
        delete texture;
        throw std::exception();
    }
    else
    {
        data = this->pixels;
    }

    glBindTexture(texture->target, texture->id);
    glTexImage2D(texture->target, 0, internalformat,
        this->_width, this->_height, 0,
        format, type, data);

    return texture;
}

Texture *CoreImage::get_texture(bool rectangle)
{
    if ( this->texture == NULL )
        this->texture = this->create_texture(rectangle);
    return this->texture;
}

