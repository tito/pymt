#ifndef __PYMTCORE_WIDGET
#define __PYMTCORE_WIDGET

#include <iostream>
#include <vector>
#include "Python.h"

class MTWidget
{
public:
	MTWidget();
	virtual ~MTWidget();

    virtual void add_widget(MTWidget *widget)
    {
        this->children.push_back(widget);
    }

    virtual void remove_widget(MTWidget *widget)
    {
        std::vector<MTWidget *>::iterator i = this->children.begin();
		for ( ; i != this->children.end(); i++ )
        {
            if ( *i != widget )
                continue;
			delete *i;
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
