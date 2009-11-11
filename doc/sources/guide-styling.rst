===============
Styling Widgets
===============

About styling in PyMT
---------------------

They are lot of way to do styling on a application.
PyMT use the CSS way : Cascading Style Sheet. A CSS look like this ::

  #mywidget {
    background-color: rgba(255, 100, 255, 125);
    draw-border: 1;
   }

They are some things similar to the CSS 2.1 (like background-color), but
we introduce our CSS command (like draw-border.).

Learning CSS concept
--------------------

A CSS is a way to dispatch style in widget. A widget have :

* Type (MTButton for ex.) and his parents (MTButton derivate from MTWidget)
* ID (like *mybutton*)
* A CSS Classname (like *toolbar*)

CSS syntax is construct like this ::

  selector1, selector2 {
    rule1;
    rule2;
  }

Selector have multiple syntax ::

  /* Syntax of selector */
  type {}
  #id  {}
  .class {}

  /* More possibility */
  type.class {}
  type#id    {}
  #id.class  {}

Here is some possibility with CSS ::

  /* Access to all widget with toolbar classname */
  .toolbar { }

  /* All buttons */
  MTButton { }

  /* All buttons in widget with toolbar classname */
  .toolbar MTButton { }

  /* All buttons in the toolbar with ID "mytoolbar" */
  #mytoolbar MTButton { }

  /* All sliders and radial */
  Slider, Radial { }


Use CSS with Widgets
--------------------

Default CSS
~~~~~~~~~~~

PyMT have a default CSS, available in `pymt/ui/colors.py`.
This CSS specify a default value for each style attribute in every widget.

__init__ attributes
~~~~~~~~~~~~~~~~~~~

When a widget is created, CSS are computed to match the current
widget (type, class and ID). This is done at __init__ type on MTWidget.

You can specify ID and CSS classname at __init__ type ::

  btn_newfile = MTButton(id="file-new", cls="toolbar-btn")
  btn_savefile = MTButton(id="file-save", cls="toolbar-btn")

And make a CSS like this ::

  /* Use red color to all button with toolbar-btn class */
  .toolbar-btn {
    background-color: rgb(255, 0, 0);
  }

  /* Make the file-save button in green */
  #file-save {
    background-color: rgb(0, 255, 0);
  }


Additional CSS
~~~~~~~~~~~~~~~

Your CSS must be the first thing to do before creating Widget.
You can add additionnal CSS at runtime ::

  my_css = '''
      .toolbar-btn {
        background-color: rgb(255, 0, 0);
      }
      #file-save {
        background-color: rgb(0, 255, 0);
      }
  '''

  css_add_sheet(my_css)

Inner styling
~~~~~~~~~~~~~

You can add our styling at __init__ time using style attribute ::

  btn = MTButton(style={'background-color': (1, 0, 0, 1)})

Or change style at runtime ::

  btn.apply_style({'background-color': (0, 1, 0, 1)})


