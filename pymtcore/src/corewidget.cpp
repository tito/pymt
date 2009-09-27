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

CoreWidget::CoreWidget()
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

CoreWidget::~CoreWidget()
{
    this->clear();
}


//
// Reference counting
//

void CoreWidget::unref(int fromswig)
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

void CoreWidget::add_widget(CoreWidget *widget)
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

void CoreWidget::remove_widget(CoreWidget *widget)
{
    CoreWidget *parent;
    std::vector<CoreWidget *>::iterator i = this->children.begin();

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

bool CoreWidget::on_move(void *data)
{
    return true;
}

bool CoreWidget::on_resize(void *data)
{
    return true;
}

bool CoreWidget::on_update(void *data)
{
    std::vector<CoreWidget *>::iterator i = this->children.begin();
    for ( ; i != this->children.end(); i++ )
        (*i)->dispatch_event("on_update", data);
    return true;
}

bool CoreWidget::on_draw(void *data)
{
    std::vector<CoreWidget *>::iterator i;

    if ( this->visible == false )
        return false;

    this->draw();
    for ( i = this->children.begin(); i != this->children.end(); i++ )
        (*i)->dispatch_event("on_draw", data);

    return true;
}

bool CoreWidget::on_touch_down(void *data)
{
    std::vector<CoreWidget *>::iterator i = this->children.begin();
    for ( ; i != this->children.end(); i++ )
        if ( (*i)->dispatch_event("on_touch_down", data) )
            return true;
    return false;
}

bool CoreWidget::on_touch_move(void *data)
{
    std::vector<CoreWidget *>::iterator i = this->children.begin();
    for ( ; i != this->children.end(); i++ )
        if ( (*i)->dispatch_event("on_touch_move", data) )
            return true;
    return false;
}

bool CoreWidget::on_touch_up(void *data)
{
    std::vector<CoreWidget *>::iterator i = this->children.begin();
    for ( ; i != this->children.end(); i++ )
        if ( (*i)->dispatch_event("on_touch_move", data) )
            return true;
    return false;
}


//
// Event dispatching
//

void CoreWidget::connect(const std::string &event_name, PyObject *callback)
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

void CoreWidget::disconnect(const std::string &event_name, PyObject *callback)
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

bool CoreWidget::dispatch_event_internal(const std::string &event_name, void *datadispatch)
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

bool CoreWidget::dispatch_event(const std::string &event_name, void *datadispatch)
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
		{
			PyErr_Print();
			return false;
		}

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

void CoreWidget::draw(void)
{
}


//
// Collisions functions
//

bool CoreWidget::collide_point(double x, double y)
{
    if ( x >= this->__pos.x && x <= (this->__pos.x + this->__size.x) &&
         y >= this->__pos.y && y <= (this->__pos.y + this->__size.y) )
        return true;
    return false;
}


//
// Coordinate transformation
//

void CoreWidget::to_local(double x, double y, double *ox, double *oy)
{
    *ox = x;
    *oy = y;
}

void CoreWidget::to_parent(double x, double y, double *ox, double *oy)
{
    *ox = x;
    *oy = y;
}

void CoreWidget::to_widget(double x, double y, double *ox, double *oy)
{
    if ( this->parent != NULL )
    {
        this->parent->to_widget(x, y, ox, oy);
        x = *ox;
        y = *oy;
    }

    this->to_local(x, y, ox, oy);
}

void CoreWidget::to_window(double x, double y, double *ox, double *oy, bool initial)
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

CoreWidget *CoreWidget::get_root_window(void)
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

CoreWidget *CoreWidget::get_parent_window(void)
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

CoreWidget *CoreWidget::get_parent_layout(void)
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

void CoreWidget::show(void)
{
    this->visible = true;
}

void CoreWidget::hide(void)
{
    this->visible = false;
}


//
// Operators
//

bool CoreWidget::operator==(const CoreWidget *widget)
{
    return (this == widget) ? true : false;
}

int CoreWidget::get_ref_count(void)
{
    return this->__ref_count;
}


//
// Accessors, will be transformed into property with swig wrapper.
//

void CoreWidget::_set_x(double value)
{
    if ( this->__pos.x == value )
        return;
    this->__pos.x = value;
    this->__dispatch_event_dd("on_move", this->__pos.x, this->__pos.y);
}

double CoreWidget::_get_x(void)
{
    return this->__pos.x;
}

void CoreWidget::_set_y(double value)
{
    if ( this->__pos.y == value )
        return;
    this->__pos.y = value;
    this->__dispatch_event_dd("on_move", this->__pos.x, this->__pos.y);
}

double CoreWidget::_get_y(void)
{
    return this->__pos.y;
}

void CoreWidget::_set_width(double value)
{
    if ( this->__size.x == value )
        return;
    this->__size.x = value;
    this->__dispatch_event_dd("on_resize", this->__size.x, this->__size.y);
}

double CoreWidget::_get_width(void)
{
    return this->__size.x;
}

void CoreWidget::_set_height(double value)
{
    if ( this->__size.y == value )
        return;
    this->__size.y = value;
    this->__dispatch_event_dd("on_resize", this->__size.x, this->__size.y);
}

double CoreWidget::_get_height(void)
{
    return this->__size.y;
}

void CoreWidget::_set_pos(pos2d &p)
{
    if ( p.x == this->__pos.x && p.y == this->__pos.y )
        return;
    this->__pos = p;
    this->__dispatch_event_dd("on_move", this->__pos.x, this->__pos.y);
}

pos2d &CoreWidget::_get_pos(void)
{
    return this->__pos;
}

void CoreWidget::_set_size(pos2d &p)
{
    if ( p.x == this->__size.x && p.y == this->__size.y )
        return;
    this->__size = p;
    this->__dispatch_event_dd("on_resize", this->__size.x, this->__size.y);
}

pos2d &CoreWidget::_get_size(void)
{
    return this->__size;
}

void CoreWidget::_set_center(pos2d &p)
{
    static pos2d pos;
    pos.x = p.x - this->__size.x / 2.;
    pos.y = p.y - this->__size.y / 2.;
    this->_set_pos(pos);
}

pos2d &CoreWidget::_get_center(void)
{
    static pos2d pos;
    pos.x = this->__pos.x + this->__size.x / 2.;
    pos.y = this->__pos.y + this->__size.y / 2.;
    return pos;
}

bool CoreWidget::__dispatch_event_dd(const std::string &event_name, double x, double y)
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

void CoreWidget::clear(void)
{
    while ( !this->children.empty()  )
        this->remove_widget(this->children.back());

    while ( !this->callbacks.empty() )
    {
        callback_t c = this->callbacks.back();
        this->disconnect(c.event_name.c_str(), c.callback);
    }
}
