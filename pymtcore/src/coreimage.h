#ifndef __PYMTCORE_COREIMAGE
#define __PYMTCORE_COREIMAGE

void core_image_init();

class CoreImage
{
public:
	CoreImage(std::string filename);
    virtual ~CoreImage();
    virtual bool load();
    virtual void draw();

	std::string     filename;
    double          opacity;
    double          scale;
    std::string     anchor_x;
    std::string     anchor_y;
    double          _width;
    double          _height;
    double          x;
    double          y;

    // Internal image data
    std::string     format;
    int             offset;
    unsigned int    pitch;
    void            *pixels;
};

#endif
