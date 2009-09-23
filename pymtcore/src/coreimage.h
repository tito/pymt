#ifndef __PYMTCORE_COREIMAGE
#define __PYMTCORE_COREIMAGE

#include "texture.h"

void core_image_init();

class CoreImage
{
public:
	CoreImage(std::string filename);
    virtual ~CoreImage();
    virtual bool load();
    virtual void draw();
    virtual Texture *get_texture(bool rectangle=false);

	std::string     filename;
    double          opacity;
    double          scale;
    int             anchor_x;
    int             anchor_y;
    int             _width;
    int             _height;
    double          x;
    double          y;

    // Internal image data
    std::string     format;
    int             offset;
    unsigned int    pitch;
    void            *pixels;

protected:
    Texture         *create_texture(bool rectangle=false);

    Texture         *texture;
};

#endif
