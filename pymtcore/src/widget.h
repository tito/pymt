#ifndef __PYMTCORE_WIDGET
#define __PYMTCORE_WIDGET

#include <iostream>
#include <vector>
#include "Python.h"

class MTWidget
{
    // implement the ref counting mechanism
    int __ref_count;

public:
    MTWidget()
    {
        this->__ref_count = 0;
        this->parent = NULL;
    }

    virtual ~MTWidget()
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


    virtual void add_widget(MTWidget *widget)
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

    virtual void remove_widget(MTWidget *widget)
    {
        MTWidget *parent;
        std::vector<MTWidget *>::iterator i = this->children.begin();

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
        std::vector<MTWidget *>::iterator i = this->children.begin();
        for ( ; i != this->children.end(); i++ )
            (*i)->on_update();
    }

    virtual void on_draw(void)
    {
        std::vector<MTWidget *>::iterator i = this->children.begin();

        this->draw();

        for ( ; i != this->children.end(); i++ )
            (*i)->on_draw();
    }

    virtual void draw(void)
    {
    }


    int get_ref_count(void)
    {
        return this->__ref_count;
    }

    std::vector<MTWidget *> children;
    MTWidget *parent;
};

#endif
