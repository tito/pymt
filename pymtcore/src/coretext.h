#ifndef __PYMTCORE_CORETEXT
#define __PYMTCORE_CORETEXT

#include "coreimage.h"
#include "texture.h"

#ifdef HAVE_CAIRO
#include <cairo.h>
#endif

class CoreText
{
public:
    CoreText();
    virtual ~CoreText();

    void _set_label(const std::string &label);
    std::string _get_label(void);

    void _set_fontname(const std::string &fontname);
    std::string _get_fontname(void);

    void _set_fontsize(double size);
    double _get_fontsize(void);

    void _set_bold(bool bold);
    bool _get_bold(void);

    void _set_multiline(bool multiline);
    bool _get_multiline(void);

    Texture *get_texture();

protected:
    std::string     label;
    std::string     fontname;
    double          fontsize;
    bool            bold;
    bool            multiline;
    bool            need_refresh;
    CoreImage       *image;
    int             width;
    int             height;

    void            provider_create(void);
    void            provider_destroy(void);
    void            provider_refresh(void);

#ifdef HAVE_CAIRO
    cairo_surface_t *cr_surface;
    cairo_t         *cr;
#endif
};

#endif
