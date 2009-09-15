#ifndef __PYMTCORE_WIDGET
#define __PYMTCORE_WIDGET

#include "Python.h"

class MTWidget
{
public:
	MTWidget();
	virtual ~MTWidget();

    virtual void add_widget(PyObject *widget);
    virtual void remove_widget(PyObject *widget);

    virtual void on_update(void);

    virtual void draw(void);
    virtual void on_draw(void);

	PyObject *children;
};

#endif
