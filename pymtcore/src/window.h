#ifndef __PYMTCORE_WINDOW
#define __PYMTCORE_WINDOW

#include "Python.h"

class MTWindow
{
    public:

    MTWindow(int width, int height, bool fullscreen, bool vsync, int display);
    virtual ~MTWindow();

    void on_update(void);

    void draw(void);
    void on_draw(void);

    void add_widget(PyObject *widget);
    void remove_widget(PyObject *widget);
};

#endif
