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
        std::cout << "ctor " << this << std::endl;
        this->clear();
    }

    void clear(void)
    {
        /**
        MTWidget *widget;
        while ( this->children.begin() != this->children.end() )
        {
            std::cout << "size=" << this->children.size() << std::endl;
            widget = this->children.back();
            if ( widget->parent )
                widget->parent->unref();
            this->children.pop_back();
        }
        **/
    }

    int ref(void)
    {
        /* automaticly disown the object if it's handled here
         */
        Swig::Director *director = dynamic_cast<Swig::Director *>(this);
        std::cout << "ref(), director=" << director << " for " << this << std::endl;

        this->__ref_count++;

        if ( director )
        {
            std::cout << "disown called " << this << std::endl;
            director->swig_disown();
        }

        return this->__ref_count;
    }

    int unref(int fromswig=0)
    {
        std::cout << "unref " << this << " from " << fromswig << std::endl;
        this->__ref_count--;
        if ( this->__ref_count <= 0 )
        {
            std::cout << "delete this" << this << std::endl;
            delete this;
            return 0;
        } 

        if ( fromswig )
        {
            this->clear();
        }

        return this->__ref_count;
    }


    virtual void add_widget(MTWidget *widget)
    {
        this->children.push_back(widget);
        widget->ref();
        widget->parent = this;
        this->ref();
    }

    virtual void remove_widget(MTWidget *widget)
    {
        std::vector<MTWidget *>::iterator i = this->children.begin();
		for ( ; i != this->children.end(); i++ )
        {
            if ( *i != widget )
                continue;
            (*i)->parent->unref();
            (*i)->parent = NULL;
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

    void print_debug_internal(void)
    {
        std::cout << "Object " << this << std::endl;
        std::cout << "* __ref_count = " << this->__ref_count << std::endl;
    }

    std::vector<MTWidget *> children;
    MTWidget *parent;
};

#endif
