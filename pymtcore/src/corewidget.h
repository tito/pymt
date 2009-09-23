#ifndef __PYMTCORE_COREWIDGET
#define __PYTMCORE_COREWIDGET

#include <vector>

typedef struct callback_s
{
    std::string event_name;
    PyObject    *callback;
} callback_t;

struct pos2d
{
    double x;
    double y;

    char *__str__(void)
    {
        static char tmp[128];
        snprintf(tmp, sizeof(tmp), "(%f, %f)", this->x, this->y);
        return tmp;
    }
};

class MTCoreWidget
{
public:
    MTCoreWidget();
    virtual ~MTCoreWidget();

    //
    // Reference counting
    //

    void ref(void);
    void unref(int fromswig=0);
    int get_ref_count(void);

    //
    // Children manipulation
    //

    virtual void add_widget(MTCoreWidget *widget);
    virtual void remove_widget(MTCoreWidget *widget);

    //
    // Event functions
    //

    virtual bool on_move(void *data);
    virtual bool on_resize(void *data);
    virtual bool on_update(void *data);
    virtual bool on_draw(void *data);
    virtual bool on_touch_down(void *data);
    virtual bool on_touch_move(void *data);
    virtual bool on_touch_up(void *data);

    //
    // Event dispatching
    //

    void connect(const std::string &event_name, PyObject *callback);
    void disconnect(const std::string &event_name, PyObject *callback);
	virtual bool dispatch_event_internal(const std::string &event_name, void *datadispatch);
    virtual bool dispatch_event(const std::string &event_name, void *datadispatch);

    //
    // Drawing functions
    //

    virtual void draw(void);

    //
    // Collisions functions
    //

    virtual bool collide_point(double x, double y);

    //
    // Coordinate transformation
    //

    virtual void to_local(double x, double y, double *ox, double *oy);
    virtual void to_parent(double x, double y, double *ox, double *oy);
    virtual void to_widget(double x, double y, double *ox, double *oy);
    virtual void to_window(double x, double y, double *ox, double *oy, bool initial=true);

    //
    // Accessors for window / layout
    //

    virtual MTCoreWidget *get_root_window(void);
    virtual MTCoreWidget *get_parent_window(void);
    virtual MTCoreWidget *get_parent_layout(void);

    //
    // Visibility of the widget
    //

    virtual void show(void);
    virtual void hide(void);

    //
    // Operators
    //

    bool operator==(const MTCoreWidget *widget);

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
    virtual pos2d &_get_pos(void);
    virtual void _set_size(pos2d &p);
    virtual pos2d &_get_size(void);
    virtual void _set_center(pos2d &p);
    virtual pos2d &_get_center(void);

    //
    // Public properties
    //

    std::vector<callback_t>     callbacks;
    std::vector<MTCoreWidget *> children;
    MTCoreWidget    *parent;
    bool            visible;

    MTCoreWidget    *__root_window;
    MTCoreWidget    *__root_window_source;
    MTCoreWidget    *__parent_window;
    MTCoreWidget    *__parent_window_source;
    MTCoreWidget    *__parent_layout;
    MTCoreWidget    *__parent_layout_source;

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
