#ifndef __PYMTCORE_COREIMAGE
#define __PYMTCORE_COREIMAGE

class CoreImage;

typedef bool (*loader_t)(CoreImage &);

static std::vector<loader_t> loaders;

class CoreImage
{
public:
	CoreImage(std::string filename)
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

    virtual ~CoreImage()
    {
        if ( this->pixels != NULL )
        {
            free(this->pixels);
            this->pixels = NULL;
        }
    }

    virtual bool load()
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

    virtual void draw()
    {
        // TODO
    }


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

#ifdef HAVE_SDL_IMAGE
#include <SDL/SDL_image.h>
bool load_with_sdlimage(CoreImage &image)
{
    SDL_Surface *surface;
    surface = IMG_Load(image.filename.c_str());
    if ( surface == NULL )
        return false;
    image._width        = surface->w;
    image._height       = surface->h;
    image.offset        = surface->offset;
    image.pitch         = surface->pitch;
    //image.pixels        = surface->pixels;
    SDL_FreeSurface(surface);
    return true;
};
#endif // HAVE_SDL_IMAGE

#ifdef HAVE_IMLIB2
#include <Imlib2.h>
bool load_with_imlib2(CoreImage &image)
{
    Imlib_Image surface;
    surface = imlib_load_image_immediately(image.filename.c_str());
    if ( surface == NULL )
        return false;

    image._width        = imlib_image_get_width();
    image._height       = imlib_image_get_height();
    image.format        = imlib_image_format();
    //image.pixels        = imlib_image_get_data();
    return true;
}
#endif // HAVE_IMLIB2

void core_image_init()
{
#ifdef HAVE_SDL_IMAGE
    loaders.push_back(load_with_sdlimage);
#endif
#ifdef HAVE_IMLIB2
    loaders.push_back(load_with_imlib2);
#endif
}

#endif
