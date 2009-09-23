#include <iostream>
#include <Python.h>
#include "corewidget.h"

class CoreWidgetException_s : public std::exception
{
    virtual const char *what() const throw()
    {
        return "Error while calling dispatch_event.";
    }
} CoreWidgetException;

MTCoreWidget::MTCoreWidget()
{
    this->parent                    = NULL;
    this->visible                   = true;
    this->__pos.x                   = 0;
    this->__pos.y                   = 0;
    this->__size.x                  = 100;
    this->__size.y                  = 100;

    this->__ref_count               = 0;
    this->__root_window             = NULL;
    this->__root_window_source      = NULL;
    this->__parent_window           = NULL;
    this->__parent_window_source    = NULL;
    this->__parent_layout           = NULL;
    this->__parent_layout_source    = NULL;
}

MTCoreWidget::~MTCoreWidget()
{
    this->clear();
}


//
// Reference counting
//

void MTCoreWidget::unref(int fromswig)
{
    // if swig don't have anymore a reference on it,
    // and we are orphan, clear our children list.
    if ( fromswig && this->parent == NULL )
        this->clear();

    // decrement the reference counting
    this->__ref_count--;
    if ( this->__ref_count <= 0 )
    {
        delete this;
        return;
    }
}


//
// Children manipulation
//

void MTCoreWidget::add_widget(MTCoreWidget *widget)
{
    // TODO add exception, a widget cannot have 2 parent !
    if ( widget->parent != NULL )
        return;

    // add the widget at the back
    this->children.push_back(widget);

    // reference the widget and ourself as parent
    this->ref();
    widget->ref();
    widget->parent = this;
}

void MTCoreWidget::remove_widget(MTCoreWidget *widget)
{
    MTCoreWidget *parent;
    std::vector<MTCoreWidget *>::iterator i = this->children.begin();

    // reference ourself, we don't want to be removed
    // when a widget remove is done
    this->ref();

    for ( ; i != this->children.end(); i++ )
    {
        // if the widget is not found, continue
        if ( *i != widget )
            continue;

        // remove the widget from the list
        this->children.erase(i);

        // prevent recursion on unref() call
        parent = (*i)->parent;
        (*i)->parent = NULL;
        if ( parent != NULL )
            parent->unref();

        // unref the children.
        (*i)->unref();
        break;
    }

    // unref ourself.
    this->unref();
}


//
// Event functions
//

bool MTCoreWidget::on_move(void *data)
{
    return true;
}

bool MTCoreWidget::on_resize(void *data)
{
    return true;
}

bool MTCoreWidget::on_update(void *data)
{
    std::vector<MTCoreWidget *>::iterator i = this->children.begin();
    for ( ; i != this->children.end(); i++ )
        (*i)->on_update(data);
    return true;
}

bool MTCoreWidget::on_draw(void *data)
{
    std::vector<MTCoreWidget *>::iterator i;

    if ( this->visible == false )
        return false;

    this->draw();
    for ( i = this->children.begin(); i != this->children.end(); i++ )
        (*i)->on_draw(data);

    return true;
}

bool MTCoreWidget::on_touch_down(void *data)
{
    std::vector<MTCoreWidget *>::iterator i = this->children.begin();
    for ( ; i != this->children.end(); i++ )
        if ( (*i)->on_touch_down(data) )
            return true;
    return false;
}

bool MTCoreWidget::on_touch_move(void *data)
{
    std::vector<MTCoreWidget *>::iterator i = this->children.begin();
    for ( ; i != this->children.end(); i++ )
        if ( (*i)->on_touch_move(data) )
            return true;
    return false;
}

bool MTCoreWidget::on_touch_up(void *data)
{
    std::vector<MTCoreWidget *>::iterator i = this->children.begin();
    for ( ; i != this->children.end(); i++ )
        if ( (*i)->on_touch_move(data) )
            return true;
    return false;
}


//
// Event dispatching
//

void MTCoreWidget::connect(const std::string &event_name, PyObject *callback)
{
    callback_t c;

    // disconnect event_name first.
    this->disconnect(event_name, NULL);

    // push new callback
    c.event_name    = std::string(event_name);
    c.callback      = callback;
    Py_INCREF(c.callback);
    this->callbacks.push_back(c);
}

void MTCoreWidget::disconnect(const std::string &event_name, PyObject *callback)
{
    std::vector<callback_t>::iterator i;
    for ( i = this->callbacks.begin(); i != this->callbacks.end(); i++ )
    {
        // event name match ?
        if ( (*i).event_name != event_name )
            continue;
        // match a specific callback ?
        if ( callback != NULL && (*i).callback != callback )
            continue;
        Py_DECREF((*i).callback);
        this->callbacks.erase(i);
        return;
    }
}

bool MTCoreWidget::dispatch_event_internal(const std::string &event_name, void *datadispatch)
{
    if ( event_name == "on_move" )
        return this->on_move(datadispatch);
    if ( event_name == "on_resize" )
        return this->on_resize(datadispatch);
    if ( event_name == "on_draw" )
        return this->on_draw(datadispatch);
    if ( event_name == "on_update" )
        return this->on_update(datadispatch);
    if ( event_name == "on_touch_up" )
        return this->on_touch_up(datadispatch);
    if ( event_name == "on_touch_move" )
        return this->on_touch_move(datadispatch);
    if ( event_name == "on_touch_down" )
        return this->on_touch_down(datadispatch);
    std::cout << "unknown dispatch_event_internal for " << event_name << std::endl;
    return false;
}

bool MTCoreWidget::dispatch_event(const std::string &event_name, void *datadispatch)
{
    PyObject *result;
    std::vector<callback_t>::iterator i;

    // check if a callback exist for this event
    for ( i = this->callbacks.begin(); i != this->callbacks.end(); i++ )
    {
        if ( (*i).event_name != event_name )
            continue;

        // event found, let's call the function !
        result = PyObject_CallFunctionObjArgs(
            (*i).callback, (PyObject *)datadispatch, NULL);
        if ( PyErr_Occurred() )
            throw CoreWidgetException;

        // convert the return to a boolean
        if ( result == NULL )
            return false;
        return PyObject_IsTrue(result) ? true : false;
    }

    return this->dispatch_event_internal(event_name, datadispatch);
}


//
// Drawing functions
//

void MTCoreWidget::draw(void)
{
}


//
// Collisions functions
//

bool MTCoreWidget::collide_point(double x, double y)
{
    if ( x >= this->__pos.x && x <= (this->__pos.x + this->__size.x) &&
         y >= this->__pos.y && y <= (this->__pos.y + this->__size.y) )
        return true;
    return false;
}


//
// Coordinate transformation
//

void MTCoreWidget::to_local(double x, double y, double *ox, double *oy)
{
    *ox = x;
    *oy = y;
}

void MTCoreWidget::to_parent(double x, double y, double *ox, double *oy)
{
    *ox = x;
    *oy = y;
}

void MTCoreWidget::to_widget(double x, double y, double *ox, double *oy)
{
    if ( this->parent != NULL )
    {
        this->parent->to_widget(x, y, ox, oy);
        x = *ox;
        y = *oy;
    }

    this->to_local(x, y, ox, oy);
}

void MTCoreWidget::to_window(double x, double y, double *ox, double *oy, bool initial)
{
    if ( initial == false )
    {
        this->to_parent(x, y, ox, oy);
        x = *ox;
        y = *oy;
    }

    if ( this->parent != NULL )
    {
        this->parent->to_window(x, y, ox, oy, false);
        return;
    }

    *ox = x;
    *oy = y;
}


//
// Accessors for window / layout
//

MTCoreWidget *MTCoreWidget::get_root_window(void)
{
    if ( this->parent == NULL )
        return NULL;

    if ( this->__root_window_source != this->parent ||
         this->__root_window == NULL )
    {
        this->__root_window = this->parent->get_root_window();
        if ( this->__root_window == NULL )
            return NULL;
        this->__root_window_source = this->parent;
    }

    return this->__root_window;
}

MTCoreWidget *MTCoreWidget::get_parent_window(void)
{
    if ( this->parent == NULL )
        return NULL;

    if ( this->__parent_window_source != this->parent ||
         this->__parent_window == NULL )
    {
        this->__parent_window = this->parent->get_parent_window();
        if ( this->__parent_window == NULL )
            return NULL;
        this->__parent_window_source = this->parent;
    }

    return this->__parent_window;
}

MTCoreWidget *MTCoreWidget::get_parent_layout(void)
{
    if ( this->parent == NULL )
        return NULL;

    if ( this->__parent_layout_source != this->parent ||
         this->__parent_layout == NULL )
    {
        this->__parent_layout = this->parent->get_parent_layout();
        if ( this->__parent_layout == NULL )
            return NULL;
        this->__parent_layout_source = this->parent;
    }

    return this->__parent_layout;
}


//
// Visibility of the widget
//

void MTCoreWidget::show(void)
{
    this->visible = true;
}

void MTCoreWidget::hide(void)
{
    this->visible = false;
}


//
// Operators
//

bool MTCoreWidget::operator==(const MTCoreWidget *widget)
{
    return (this == widget) ? true : false;
}

int MTCoreWidget::get_ref_count(void)
{
    return this->__ref_count;
}


//
// Accessors, will be transformed into property with swig wrapper.
//

void MTCoreWidget::_set_x(double value)
{
    if ( this->__pos.x == value )
        return;
    this->__pos.x = value;
    this->__dispatch_event_dd("on_move", this->__pos.x, this->__pos.y);
}

double MTCoreWidget::_get_x(void)
{
    return this->__pos.x;
}

void MTCoreWidget::_set_y(double value)
{
    if ( this->__pos.y == value )
        return;
    this->__pos.y = value;
    this->__dispatch_event_dd("on_move", this->__pos.x, this->__pos.y);
}

double MTCoreWidget::_get_y(void)
{
    return this->__pos.y;
}

void MTCoreWidget::_set_width(double value)
{
    if ( this->__size.x == value )
        return;
    this->__size.x = value;
    this->__dispatch_event_dd("on_resize", this->__size.x, this->__size.y);
}

double MTCoreWidget::_get_width(void)
{
    return this->__size.x;
}

void MTCoreWidget::_set_height(double value)
{
    if ( this->__size.y == value )
        return;
    this->__size.y = value;
    this->__dispatch_event_dd("on_resize", this->__size.x, this->__size.y);
}

double MTCoreWidget::_get_height(void)
{
    return this->__size.y;
}

void MTCoreWidget::_set_pos(pos2d &p)
{
    if ( p.x == this->__pos.x && p.y == this->__pos.y )
        return;
    this->__pos = p;
    this->__dispatch_event_dd("on_move", this->__pos.x, this->__pos.y);
}

pos2d &MTCoreWidget::_get_pos(void)
{
    return this->__pos;
}

void MTCoreWidget::_set_size(pos2d &p)
{
    if ( p.x == this->__size.x && p.y == this->__size.y )
        return;
    this->__size = p;
    this->__dispatch_event_dd("on_resize", this->__size.x, this->__size.y);
}

pos2d &MTCoreWidget::_get_size(void)
{
    return this->__size;
}

void MTCoreWidget::_set_center(pos2d &p)
{
    static pos2d pos;
    pos.x = p.x - this->__size.x / 2.;
    pos.y = p.y - this->__size.y / 2.;
    this->_set_pos(pos);
}

pos2d &MTCoreWidget::_get_center(void)
{
    static pos2d pos;
    pos.x = this->__pos.x + this->__size.x / 2.;
    pos.y = this->__pos.y + this->__size.y / 2.;
    return pos;
}

bool MTCoreWidget::__dispatch_event_dd(const std::string &event_name, double x, double y)
{
    bool result;
    PyObject *o, *o2, *o3;
    o = PyTuple_New(2);
    if ( o == NULL )
        return false;
    o2 = PyFloat_FromDouble(x);
    o3 = PyFloat_FromDouble(y);
    PyTuple_SetItem(o, 0, o2);
    PyTuple_SetItem(o, 1, o3);

    result = this->dispatch_event(event_name, o);

    Py_XDECREF(o);

    return result;
}

void MTCoreWidget::clear(void)
{
    while ( !this->children.empty()  )
        this->remove_widget(this->children.back());

    while ( !this->callbacks.empty() )
    {
        callback_t c = this->callbacks.back();
        this->disconnect(c.event_name.c_str(), c.callback);
    }
}
