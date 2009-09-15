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
        __ref_count = 0;
    }

    virtual ~MTWidget()
    {
    }

    int ref(void)
    {
        return ++this->__ref_count;
    }

    int unref(void)
    {
        this->__ref_count--;
        if ( this->__ref_count <= 0 )
        {
            delete this;
            return 0;
        } 

        return this->__ref_count;
    }


    virtual void add_widget(MTWidget *widget)
    {
        this->children.push_back(widget);
        widget->ref();
    }

    virtual void remove_widget(MTWidget *widget)
    {
        std::vector<MTWidget *>::iterator i = this->children.begin();
		for ( ; i != this->children.end(); i++ )
        {
            if ( *i != widget )
                continue;
            (*i)->unref();
            return;
		}

    }

    virtual void on_update(void)
    {
        std::vector<MTWidget *>::iterator i = this->children.begin();
        for ( ; i != this->children.end(); i++ )
        {
            (*i)->on_update();
        }
    }

    virtual void on_draw(void)
    {
        std::vector<MTWidget *>::iterator i = this->children.begin();

        this->draw();

        for ( ; i != this->children.end(); i++ )
        {
            (*i)->on_draw();
        }
    }

    virtual void draw(void)
    {
    }

    std::vector<MTWidget *> children;
};

#endif
