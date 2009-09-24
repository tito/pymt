#ifndef __PYMTCORE_TEXTURE
#define __PYMTCORE_TEXTURE

#include <GL/gl.h>
#include "Python.h"

class TextureRegion;

class AbstractImage
{
public:
	AbstractImage(int width, int height);

	virtual void *get_image_data() = 0;
	virtual void *get_texture(bool rectangle=false) = 0;
	//virtual void *get_mipmapped_texture() = 0;
	virtual TextureRegion *get_region(int x, int y, int width, int height) = 0;

	int	width;
	int height;
};

class Texture : public AbstractImage
{
public:
	Texture(int width, int height, unsigned int target, unsigned int id);

    static Texture *create(int width, int height, int internalformat=GL_RGBA, bool rectangle=false);
	virtual void *get_image_data();
	virtual void *get_texture(bool rectangle=false);
	virtual TextureRegion *get_region(int x, int y, int width, int height);

	unsigned int	id;
	unsigned int	target;
};

class TextureRegion : public Texture
{
public:
	TextureRegion(int x, int y, int width, int height, Texture *owner);

	int		x;
	int		y;
	Texture *owner;
};

#endif
