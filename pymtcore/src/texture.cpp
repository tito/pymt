#include <Python.h>
#include <iostream>
#include <GL/glew.h>
#include "texture.h"
#include "private.h"

inline int nearest_pow2(int v)
{
	v -= 1;
	v |= v >> 1;
	v |= v >> 2;
	v |= v >> 4;
	v |= v >> 8;
	v |= v >> 16;
	return v + 1;
};

AbstractImage::AbstractImage(int width, int height)
{
    this->width		= width;
    this->height	= height;
	this->__ref_count	= 0;
}

AbstractImage::~AbstractImage(void)
{
}

void AbstractImage::ref(void)
{
	this->__ref_count++;
}

void AbstractImage::unref(void)
{
	this->__ref_count--;
	if ( this->__ref_count <= 0 )
		delete this;
}

int AbstractImage::get_ref_count(void)
{
    return this->__ref_count;
}

Texture::Texture(int width, int height, unsigned int target, unsigned int id) :
    AbstractImage(width, height)
{
    this->target		= target;
    this->id			= id;
	this->tex_coords[0] = 0.;
	this->tex_coords[1] = 0.;
	this->tex_coords[2] = 0.;
	this->tex_coords[3] = 1.;
	this->tex_coords[4] = 0.;
	this->tex_coords[5] = 0.;
	this->tex_coords[6] = 1.;
	this->tex_coords[7] = 1.;
	this->tex_coords[8] = 0.;
	this->tex_coords[9] = 0.;
	this->tex_coords[10] = 1.;
	this->tex_coords[11] = 0.;
}

Texture::~Texture()
{
}

Texture *Texture::create(int width, int height, int internalformat, bool rectangle)
{
	Texture *texture;
	GLuint	id;
	int target			= GL_TEXTURE_2D,
		texture_width	= 0,
		texture_height	= 0;

	if ( rectangle )
	{
		rectangle = false;
		std::cout << "rectangle texture not implemented yet." << std::endl;
#if 0
	
        if _is_pow2(width) and _is_pow2(height):
            rectangle = False
        elif gl_info.have_extension('GL_ARB_texture_rectangle'):
            target = GL_TEXTURE_RECTANGLE_ARB
        elif gl_info.have_extension('GL_NV_texture_rectangle'):
            target = GL_TEXTURE_RECTANGLE_NV
        else:
            rectangle = False
#endif
	}

	if ( rectangle )
	{
		texture_width	= width;
		texture_height	= height;
	}
	else
	{
		texture_width	= nearest_pow2(width);
		texture_height	= nearest_pow2(height);
	}

	GL( glGenTextures(1, &id) );
	GL( glBindTexture(target, id) );
	GL( glTexParameteri(target, GL_TEXTURE_MIN_FILTER, GL_LINEAR) );
	GL( glTexImage2D(target, 0, internalformat,
		texture_width, texture_height, 0, GL_RGBA,
		GL_UNSIGNED_BYTE, NULL) );

	texture = new Texture(texture_width, texture_height, target, id);

	if ( rectangle )
	{
		// texture.tex_coords = (0., 0., 0., width,
		// 0., 0., width, height, 0., 0., height, 0.)
	}

	GL( glFlush() );

	if ( texture_width == width && texture_height == height )
		return texture;

	return reinterpret_cast<Texture *>(texture->get_region(0, 0, width, height));
}

void *Texture::get_image_data(void)
{
	return NULL;
}

Texture *Texture::get_texture(bool rectangle)
{
	return this;
}

TextureRegion *Texture::get_region(int x, int y, int width, int height)
{
	return new TextureRegion(x, y, width, height, this);
}

TextureRegion::TextureRegion(int x, int y, int width, int height, Texture *owner) :
	Texture(width, height, owner->target, owner->id)
{
	this->x		= x;
	this->y		= y;
	this->owner = owner;
	this->owner->ref();
}

TextureRegion::~TextureRegion(void)
{
	this->owner->unref();
}
