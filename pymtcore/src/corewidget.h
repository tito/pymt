#ifndef __PYMTCORE_COREWIDGET
#define __PYTMCORE_COREWIDGET

class MTCoreWidget
{
    // implement the ref counting mechanism
    int __ref_count;

public:
    MTCoreWidget()
    {
        this->__ref_count               = 0;
        this->parent                    = NULL;
        this->width                     = 0;
        this->height                    = 0;
        this->x                         = 0;
        this->y                         = 0;
        this->visible                   = true;

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

    void clear(void)
    {
        while ( !this->children.empty()  )
            this->remove_widget(this->children.back());
    }

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

    virtual void draw(void)
    {
    }

    virtual bool collide_point(double x, double y)
    {
        if ( x >= this->x && x <= (this->x + this->width) &&
             y >= this->y && y <= (this->y + this->height) )
            return true;
        return false;
    }

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

    void show(void)
    {
        this->visible = true;
    }

    void hide(void)
    {
        this->visible = false;
    }

    bool operator==(const MTCoreWidget *widget)
    {
        return (this == widget) ? true : false;
    }

    int get_ref_count(void)
    {
        return this->__ref_count;
    }

    std::vector<MTCoreWidget *> children;
    MTCoreWidget    *parent;
    double          x;
    double          y;
    double          width;
    double          height;
    bool            visible;

private:
    MTCoreWidget    *__root_window;
    MTCoreWidget    *__root_window_source;
    MTCoreWidget    *__parent_window;
    MTCoreWidget    *__parent_window_source;
    MTCoreWidget    *__parent_layout;
    MTCoreWidget    *__parent_layout_source;
};

int spam(double a, double b, double *oa, double *ob)
{
    *oa = a;
    *ob = b;
    return 0;
}

#endif
