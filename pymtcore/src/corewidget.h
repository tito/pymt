#ifndef __PYMTCORE_COREWIDGET
#define __PYTMCORE_COREWIDGET

#include <vector>
#include "utils.h"

typedef struct callback_s
{
    std::string event_name;
    PyObject    *callback;
} callback_t;

class CoreWidget
{
public:
    CoreWidget();
    virtual ~CoreWidget();

    //
    // Reference counting
    //

    void ref(void);
    void unref(int fromswig=0);
    int get_ref_count(void);

    //
    // Children manipulation
    //

    virtual void add_widget(CoreWidget *widget);
    virtual void remove_widget(CoreWidget *widget);

    //
    // Event functions
    //

    virtual bool on_move(PyObject *data);
    virtual bool on_resize(PyObject *data);
    virtual bool on_update(PyObject *data);
    virtual bool on_draw(PyObject *data);
    virtual bool on_touch_down(PyObject *data);
    virtual bool on_touch_move(PyObject *data);
    virtual bool on_touch_up(PyObject *data);

    //
    // Event dispatching
    //

    void connect(const std::string &event_name, PyObject *callback);
    void disconnect(const std::string &event_name, PyObject *callback);
	virtual bool dispatch_event_internal(const std::string &event_name, PyObject *data);
    virtual bool dispatch_event(const std::string &event_name, PyObject *data);

    //
    // Drawing functions
    //

    virtual void draw(void);
    virtual void drawend(void);

    //
    // Collisions functions
    //

    virtual bool collide_point(double x, double y);

    //
    // Coordinate transformation
    //

    virtual pos2d to_local(double x, double y);
    virtual pos2d to_parent(double x, double y);
    virtual pos2d to_widget(double x, double y);
    virtual pos2d to_window(double x, double y, bool initial=true);

    //
    // Accessors for window / layout
    //

    virtual CoreWidget *get_root_window(void);
    virtual CoreWidget *get_parent_window(void);
    virtual CoreWidget *get_parent_layout(void);

    //
    // Visibility of the widget
    //

    virtual void show(void);
    virtual void hide(void);

    //
    // Operators
    //

    bool operator==(const CoreWidget *widget);

    //
    // Accessors, will be transformed into property with swig wrapper.
    //

    virtual void _set_x(double value);
    virtual double _get_x(void);
    virtual void _set_y(double value);
    virtual double _get_y(void);
    virtual void _set_width(double value);
    virtual double _get_width(void);
    virtual void _set_height(double value);
    virtual double _get_height(void);
    virtual void _set_pos(pos2d &p);
    virtual pos2d _get_pos(void);
    virtual void _set_size(pos2d &p);
    virtual pos2d _get_size(void);
    virtual void _set_center(pos2d &p);
    virtual pos2d _get_center(void);

    //
    // Public properties
    //

    std::vector<callback_t>     callbacks;
    std::vector<CoreWidget *> children;
    CoreWidget      *parent;
    bool            visible;

    CoreWidget      *__root_window;
    CoreWidget      *__root_window_source;
    CoreWidget      *__parent_window;
    CoreWidget      *__parent_window_source;
    CoreWidget      *__parent_layout;
    CoreWidget      *__parent_layout_source;

protected:

    bool __dispatch_event_dd(const std::string &event_name, double x, double y);

private:
    // implement the ref counting mechanism
    int             __ref_count;

    pos2d           __pos;
    pos2d           __size;

    void clear(void);
};

#endif
