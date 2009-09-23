#include <iostream>
#include "coreimage.h"
#include "coreimage_private.h"

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
    surface = imlib_load_image(image.filename.c_str());
    if ( surface == NULL )
        return false;

	imlib_context_set_image(surface);

    image._width        = imlib_image_get_width();
    image._height       = imlib_image_get_height();
	image.offset		= 0;
	image.pitch			= 0;
    image.format        = "ARGB";
    image.pixels        = imlib_image_get_data();
	imlib_free_image();
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

