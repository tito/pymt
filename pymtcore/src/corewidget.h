#ifndef __PYMTCORE_COREWIDGET
#define __PYTMCORE_COREWIDGET

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
    MTCoreWidget()
    {
        this->parent                    = NULL;
        this->visible                   = true;
        this->__pos.x                   = 0;
        this->__pos.y                   = 0;
        this->__size.x                  = 0;
        this->__size.y                  = 0;

        this->__ref_count               = 0;
        this->__root_window             = NULL;
        this->__root_window_source      = NULL;
        this->__parent_window           = NULL;
        this->__parent_window_source    = NULL;
        this->__parent_layout           = NULL;
        this->__parent_layout_source    = NULL;
    }

    virtual ~MTCoreWidget()
    {
        this->clear();
    }


    //
    // Reference counting
    //

    void ref(void)
    {
        // automaticly disown the object if it's handled here
        // we handle the reference counting ourself.
        Swig::Director *director = dynamic_cast<Swig::Director *>(this);

        this->__ref_count++;

        if ( director )
            director->swig_disown();
    }

    void unref(int fromswig=0)
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

    virtual void add_widget(MTCoreWidget *widget)
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

    virtual void remove_widget(MTCoreWidget *widget)
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

    virtual void on_update(void)
    {
        std::vector<MTCoreWidget *>::iterator i = this->children.begin();
        for ( ; i != this->children.end(); i++ )
            (*i)->on_update();
    }

    virtual void on_draw(void)
    {
        std::vector<MTCoreWidget *>::iterator i;

        if ( this->visible == false )
            return;
        
        this->draw();
        for ( i = this->children.begin(); i != this->children.end(); i++ )
            (*i)->on_draw();
    }

    virtual bool on_touch_down(void *touch)
    {
        std::vector<MTCoreWidget *>::iterator i = this->children.begin();
        for ( ; i != this->children.end(); i++ )
            if ( (*i)->on_touch_down(touch) )
                return true;
        return false;
    }

    virtual bool on_touch_move(void *touch)
    {
        std::vector<MTCoreWidget *>::iterator i = this->children.begin();
        for ( ; i != this->children.end(); i++ )
            if ( (*i)->on_touch_move(touch) )
                return true;
        return false;
    }

    virtual bool on_touch_up(void *touch)
    {
        std::vector<MTCoreWidget *>::iterator i = this->children.begin();
        for ( ; i != this->children.end(); i++ )
            if ( (*i)->on_touch_move(touch) )
                return true;
        return false;
    }

    //
    // Drawing functions
    //

    virtual void draw(void)
    {
    }


    //
    // Collisions functions
    //

    virtual bool collide_point(double x, double y)
    {
        if ( x >= this->__pos.x && x <= (this->__pos.x + this->__size.x) &&
             y >= this->__pos.y && y <= (this->__pos.y + this->__size.y) )
            return true;
        return false;
    }


    //
    // Coordinate transformation
    //

    virtual void to_local(double x, double y, double *ox, double *oy)
    {
        *ox = x;
        *oy = y;
    }

    virtual void to_parent(double x, double y, double *ox, double *oy)
    {
        *ox = x;
        *oy = y;
    }

    virtual void to_widget(double x, double y, double *ox, double *oy)
    {
        if ( this->parent != NULL )
        {
            this->parent->to_widget(x, y, ox, oy);
            x = *ox;
            y = *oy;
        }

        this->to_local(x, y, ox, oy);
    }

    virtual void to_window(double x, double y, double *ox, double *oy, bool initial=true)
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

    virtual MTCoreWidget *get_root_window(void)
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

    virtual MTCoreWidget *get_parent_window(void)
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

    virtual MTCoreWidget *get_parent_layout(void)
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

    void show(void)
    {
        this->visible = true;
    }

    void hide(void)
    {
        this->visible = false;
    }


    //
    // Operators
    //

    bool operator==(const MTCoreWidget *widget)
    {
        return (this == widget) ? true : false;
    }

    int get_ref_count(void)
    {
        return this->__ref_count;
    }


    //
    // Accessors, will be transformed into property with swig wrapper.
    //

    void _set_x(double value)
    {
        this->__pos.x = value;
    }

    double _get_x(void)
    {
        return this->__pos.x;
    }

    void _set_y(double value)
    {
        this->__pos.y = value;
    }

    double _get_y(void)
    {
        return this->__pos.y;
    }

    void _set_width(double value)
    {
        this->__size.x = value;
    }

    double _get_width(void)
    {
        return this->__size.x;
    }

    void _set_height(double value)
    {
        this->__size.y = value;
    }

    double _get_height(void)
    {
        return this->__size.y;
    }

    void _set_pos(double x, double y)
    {
        this->__pos.x = x;
        this->__pos.y = y;
    }

    void _set_pos(const pos2d p)
    {
        this->__pos = p;
    }

    pos2d &_get_pos(void)
    {
        return this->__pos;
    }

    void _get_pos(double *ox, double *oy)
    {
        *ox = this->__pos.x;
        *oy = this->__pos.y;
    }

    void _set_size(double x, double y)
    {
        this->__size.x = x;
        this->__size.y = y;
    }

    void _get_size(double *ox, double *oy)
    {
        *ox = this->__size.x;
        *oy = this->__size.y;
    }

    void _set_center(double x, double y)
    {
        this->__pos.x = x - this->__size.x / 2.;
        this->__pos.y = y - this->__size.y / 2.;
    }

    void _get_center(double *ox, double *oy)
    {
        *ox = this->__pos.x + this->__size.x / 2.;
        *oy = this->__pos.y + this->__size.y / 2.;
    }


    //
    // Public properties
    //

    std::vector<MTCoreWidget *> children;
    MTCoreWidget    *parent;
    bool            visible;

    MTCoreWidget    *__root_window;
    MTCoreWidget    *__root_window_source;
    MTCoreWidget    *__parent_window;
    MTCoreWidget    *__parent_window_source;
    MTCoreWidget    *__parent_layout;
    MTCoreWidget    *__parent_layout_source;

private:
    // implement the ref counting mechanism
    int             __ref_count;
    pos2d           __pos;
    pos2d           __size;

    void clear(void)
    {
        while ( !this->children.empty()  )
            this->remove_widget(this->children.back());
    }


};

#endif
