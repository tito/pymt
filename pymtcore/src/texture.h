#ifndef __PYMTCORE_TEXTURE
#define __PYMTCORE_TEXTURE

#include <GL/gl.h>
#include "Python.h"

class TextureRegion;

class AbstractImage
{
public:
	AbstractImage(int width, int height);
	void ref(void);
	void unref(void);

	virtual void *get_image_data(void) = 0;
	virtual void *get_texture(bool rectangle=false) = 0;
	//virtual void *get_mipmapped_texture() = 0;
	virtual TextureRegion *get_region(int x, int y, int width, int height) = 0;

	int	width;
	int height;

protected:
	virtual ~AbstractImage(void);
	int	refcount;
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
	double			tex_coords[12];

protected:
	virtual ~Texture();
};

class TextureRegion : public Texture
{
public:
	TextureRegion(int x, int y, int width, int height, Texture *owner);

	int		x;
	int		y;
	Texture *owner;

protected:
	virtual ~TextureRegion();
};

#endif
