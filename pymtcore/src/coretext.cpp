#include <iostream>
#include "coretext.h"

CoreText::CoreText()
{
    this->label         = "";
    this->fontname      = "";
    this->fontsize      = 10.;
    this->bold          = false;
    this->multiline     = false;
    this->need_refresh  = true;
    this->width         = width;
    this->height        = height;
    this->image         = NULL;
    this->provider_create();
}

CoreText::~CoreText()
{
    this->provider_destroy();
}

void CoreText::_set_label(const std::string &label)
{
    if ( label == this->label )
        return;
    this->label         = label;
    this->need_refresh  = true;
}

std::string CoreText::_get_label(void)
{
    return this->label;
}

void CoreText::_set_fontname(const std::string &fontname)
{
    if ( this->fontname == fontname )
        return;
    this->fontname      = fontname;
    this->need_refresh  = true;
}

std::string CoreText::_get_fontname(void)
{
    return this->fontname;
}

void CoreText::_set_fontsize(double size)
{
    if ( this->fontsize == size )
        return;
    this->fontsize      = size;
    this->need_refresh  = true;
}

double CoreText::_get_fontsize(void)
{
    return this->fontsize;
}

void CoreText::_set_bold(bool bold)
{
    if ( this->bold == bold )
        return;
    this->bold         = bold;
    this->need_refresh = true;
}

bool CoreText::_get_bold(void)
{
    return this->bold;
}

void CoreText::_set_multiline(bool multiline)
{
    if ( this->multiline == multiline )
        return;
    this->multiline     = multiline;
    this->need_refresh  = true;
}

bool CoreText::_get_multiline(void)
{
    return this->multiline;
}

Texture *CoreText::get_texture(void)
{
    if ( this->image == NULL || this->need_refresh == true )
    {
        this->need_refresh = false;
        this->provider_refresh();
    }

    if ( this->image == NULL )
        return NULL;

    return this->image->get_texture();
}

void CoreText::provider_create(void)
{
#ifdef HAVE_CAIRO
    this->cr_surface    = NULL;
    this->cr            = NULL;

    this->cr_surface    = cairo_image_surface_create(CAIRO_FORMAT_ARGB32, this->width, this->height);
    if ( this->cr_surface == NULL )
        return;

    this->cr            = cairo_create(this->cr_surface);
    if ( this->cr == NULL )
        return;
#endif
}

void CoreText::provider_destroy(void)
{
#ifdef HAVE_CAIRO
    if ( this->cr != NULL )
    {
        cairo_destroy(this->cr);
        this->cr = NULL;
    }

    if ( this->cr_surface != NULL )
    {
        cairo_surface_destroy(this->cr_surface);
        this->cr_surface = NULL;
    }
#endif
}

void CoreText::provider_refresh(void)
{
#ifdef HAVE_CAIRO
    cairo_text_extents_t    extents;

    if ( this->cr == NULL )
        return;

    cairo_set_font_size(this->cr, 24);

    cairo_text_extents(this->cr, this->label.c_str(), &extents);
    std::cout << "Text <" << this->label.c_str() << "> is " << extents.width << "x" << extents.height << std::endl;

    /* update the size of the surface
     */
    if ( cairo_image_surface_get_width(this->cr_surface) != extents.width ||
         cairo_image_surface_get_height(this->cr_surface) != extents.height )
    {
        this->width = extents.width;
        this->height = extents.height;
        this->provider_destroy();
        this->provider_create();
    }

    cairo_set_font_size(this->cr, 24);

    cairo_move_to(this->cr, 0, extents.height);
    cairo_set_source_rgb(this->cr, 1., 1., 1.);
    cairo_show_text(this->cr, this->label.c_str());
    cairo_surface_write_to_png(this->cr_surface, "output.png");

    if ( this->image != NULL )
    {
        if ( this->image->_width != this->width ||
             this->image->_height != this->height )
        {
            // TODO add unref
            //delete this->image;
            this->image = NULL;
        }
    }

    if ( this->image == NULL )
    {
        this->image = new CoreImage("");
        if ( this->image == NULL )
            return;
    }

    // draw cairo onto texture
    this->image->_width     = extents.width;
    this->image->_height    = extents.height;
    this->image->offset     = 0;
    this->image->pitch      = 0;
    this->image->format     = "BGRA";
    this->image->pixels     = cairo_image_surface_get_data(this->cr_surface);
#endif
}
