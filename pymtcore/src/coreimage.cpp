#include <iostream>
#include <vector>
#include <exception>
#include <stdlib.h>
#include <GL/glew.h>
#include "coreimage.h"
#include "coreimage_private.h"
#include "private.h"

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
**/
    else if ( format == "BGRA" and glewIsSupported("GL_EXT_bgra") )
	{
		*outformat = GL_BGRA;
		*outtype = GL_UNSIGNED_BYTE;
	}
    else
        return false;
    return true;
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

    if ( filename != "" )
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
        this->texture->unref();
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
    texture = Texture::create(this->_width, this->_height, internalformat, rectangle);
    if ( texture == NULL )
        return NULL;

    if ( _get_gl_format_and_type(this->format, &format, &type) == false )
    {
        // unable to found a suitable format for opengl
        // conversion is needed
        format = GL_RGBA;
        type = GL_UNSIGNED_BYTE;
        data = this->pixels;

		std::cout << "Image: unable to found appropriate type for <" <<
			this->format << ">, do conversion." << std::endl;
		data = PyMem_Malloc(this->_width * this->_height * 4);
		if ( data == NULL )
		{
			std::cerr << "Image: unable to request memory" << std::endl;
			return NULL;
		}

		if ( this->format == "BGRA" )
		{
			std::cout << "Image: convert from ARGB to BGRA" << std::endl;
			unsigned char *out	= (unsigned char *)data,
						  *in	= (unsigned char *)this->pixels,
						  *limit	= out + this->_width * this->_height * 4;
			for ( ; out < limit; out += 4, in += 4 )
			{
				*(out)		= *(in + 2);
				*(out + 1)	= *(in + 1);
				*(out + 2)	= *(in + 0);
				*(out + 3)	= *(in + 3);
			}
		}
		else
		{
			std::cout << "Image: no converter found from format " << this->format << std::endl;
			data = this->pixels;
		}
    }
    else
    {
        data = this->pixels;
    }

    GL( glBindTexture(texture->target, texture->id) );

    GL( glTexImage2D(texture->target, 0, internalformat,
        this->_width, this->_height, 0,
        format, type, data) );

	// some conversion have been done, free memory
	if ( data != this->pixels )
	{
		PyMem_Free(data), data = NULL;
	}

    return texture;
}

Texture *CoreImage::get_texture(bool rectangle)
{
    if ( this->texture == NULL )
	{
        this->texture = this->create_texture(rectangle);
		this->texture->ref();
	}
    return this->texture;
}

