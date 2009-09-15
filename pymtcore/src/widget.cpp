#include "widget.h"

MTWidget::MTWidget()
{
    this->children = PyList_New(0);
}

MTWidget::~MTWidget()
{
    Py_XDECREF(this->children);
}

void MTWidget::add_widget(MTWidget *widget)
{
    if ( widget == NULL )
        return;
    PyList_Append(this->children, static_cast<PyObject *>(widget));
}

void MTWidget::remove_widget(MTWidget *widget)
{
	int			i;

    if ( widget == NULL )
        return;

	/* remove the first reference of widget
	 */
	i = PyList_Size(this->children);
	while ( --i >= 0 )
	{
		if ( static_cast<PyObject *>(widget) != PyList_GET_ITEM(this->children, i) )
			continue;
		PySequence_DelItem(this->children, i);
		return;

	}
}

void MTWidget::on_update(void)
{
	PyObject	*obj;
	int			i;

	i = PyList_Size(this->children);
	while ( --i >= 0 )
	{
		obj = PyList_GET_ITEM(this->children, i);

	}
}

void MTWidget::on_draw(void)
{
}

void MTWidget::draw(void)
{
}
