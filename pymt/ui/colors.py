'''
Colors: css & themes

Currently, the default css is included in this file.
You can easily extend the default style by create a css file
in your ~/.pymt/user.css.

Exemple of user.css ::

    * {
        /* increase the font-size of every widget */
        font-size: 18;
    }

.. warning::
    Only class name of widget is currently use to search CSS.

We cannot describe how to style every widget in this class.
If you want to known which attribute is needed to style a widget,
please look on the widget documentation.

'''

from __future__ import with_statement
__all__ = ['default_css', 'css_get_style', 'get_truncated_classname',
           'pymt_sheet', 'css_add_sheet', 'css_get_widget_id']

from ..logger import pymt_logger
from parser import *
import os
import sys
import shutil
import logging
import re
import cssutils

# Auto conversion from css to a special type.
auto_convert = {
    'color':                    parse_color,
    'color-down':               parse_color,
    'bg-color':                 parse_color,
    'bg-color-move':            parse_color,
    'bg-color-full':            parse_color,
    'font-size':                parse_int,
    'font-name':                parse_string,
    'font-weight':              parse_string,
    'font-color':               parse_color,
    'border-width':             parse_float,
    'border-radius':            parse_int,
    'border-radius-precision':  parse_float,
    'slider-color':             parse_color,
    'touch-color':              parse_color,
    'draw-text-shadow':         parse_bool,
    'draw-border':              parse_bool,
    'draw-alpha-background':    parse_bool,
    'text-shadow-color':        parse_color,
    'text-shadow-position':     parse_int2,
    'alpha-background':         parse_float4,
    'item-color':               parse_color,
    'item-selected':            parse_color,
	'padding':                  parse_int,
    'slider-border-radius':     parse_int,
    'slider-border-radius-precision': parse_float,
    'slider-alpha-background':  parse_float4,
    'draw-slider-border':       parse_bool,
    'draw-slider-alpha-background': parse_bool,
    'key-border-radius':        parse_int,
    'key-border-radius-precision': parse_float,
    'key-alpha-background':     parse_float4,
    'draw-key-border':          parse_bool,
    'draw-key-alpha-background': parse_bool,
    'vector-color':             parse_color,
    'title-color':              parse_color,
    'title-color':              parse_color,
    'title-border-radius':      parse_int,
    'title-border-radius-precision': parse_float,
    'title-alpha-background':   parse_float4,
    'draw-title-border':        parse_bool,
    'draw-title-alpha-background': parse_bool,
    'margin':                   parse_float4,
    'key-color':                parse_color,
    'syskey-color':                parse_color,
}

# Default CSS of PyMT
default_css = '''
* {
    /* text color */
    color: rgba(255, 255, 255, 255);

    /* color when something is pushed */
    color-down: rgba(50, 50, 50, 150);

    /* background color of widget */
    bg-color: rgba(60, 60, 60, 150);

    /* fonts */
    font-size: 10;
    font-name: "";
    font-weight: normal; /* normal, bold, italic, bolditalic */
    font-color: rgba(255, 255, 255, 255);

    /* borders */
    border-width: 1.5;
    border-radius: 0;
	border-radius-precision: 1;
    draw-border: 0;

    /* background alpha layer */
    draw-alpha-background: 0;
    alpha-background: 1 1 0.5 0.5;

    /* text shadow */
    draw-text-shadow: 0;
    text-shadow-color: rgba(22, 22, 22, 63);
    text-shadow-position: -1 1;
}

vectorslider {
    slider-color: rgba(255, 71, 0, 255);
    bg-color: rgba(51, 102, 230);
}

display {
    /* color of touch */
    touch-color: rgba(255, 0, 0, 255);
}

popup,
colorpicker,
form,
vkeyboard,
flippablewidget,
button {
    bg-color: rgba(60, 60, 60, 100);
}

formslider,
slider, xyslider, vectorslider, multislider, boundaryslider {
    padding: 8;
    bg-color: rgb(51, 51, 51);
    slider-color: rgb(255, 127, 0);
    draw-slider-border: 0;
    slider-border-radius: 0;
    slider-border-radius-precision: 1;
    draw-slider-alpha-background: 0;
    slider-alpha-background: 1 1 .5 .5;
}

kineticscrolltext {
    color: rgba(255, 255, 255, 127);
    item-color: rgb(100, 100, 100);
    item-selected: rgb(150, 150, 150);
}

kineticcontainer {
    bg-color: rgba(90, 90, 90, 127)
}

kineticlist {
    title-color: rgb(127, 127, 127);
    draw-title-border: 0;
    title-border-radius: 0;
    title-border-radius-precision: 1;
    draw-title-alpha-background: 0;
    title-alpha-background: 1 1 .5 .5;
}

.kineticlist-search {
    /* kinetic search button */
    bg-color: rgba(0, 255, 0, 127);
    alpha-background: 1 1 .7 .7;
    draw-alpha-background: 1;
}

.kineticlist-delete {
    /* kinetic delete button */
    bg-color: rgba(255, 0, 0, 127);
    alpha-background: 1 1 .7 .7;
    draw-alpha-background: 1;
}

window {
    bg-color: rgb(20, 20, 20);
}

modalwindow {
	bg-color: rgba(0, 0, 0, 200);
}

innerwindow {
    bg-color: rgba(255, 255, 255, 175);
    bg-color-move: rgba(0, 175, 0, 175);
    bg-color-full: rgba(175, 0, 0, 175);
    border-width: 30;
}

vectorslider,
objectdisplay {
    vector-color: rgb(255, 255, 255);
}

vkeyboard {
    /* onboard keyboard */
    margin: 10 50 10 50;
    border-radius: 15;
    border-radius-precision: 0.35;
    key-border-radius: 5;
    key-border-radius-precision: 1;
    draw-key-border: 1;
    key-alpha-background: 1 1 .7 .7;
    draw-key-alpha-background: 1;
    draw-border: 1;
    key-color: rgba(20, 20, 20, 255);
    syskey-color: rgba(20, 20, 40, 255);
    color-down: rgba(200, 200, 200, 127);
}

popup {
    /* popup widget */
    border-radius: 5;
    alpha-background: 1 1 .7 .7;
    draw-alpha-background: 1;
    draw-border: 1;
}

.popup-button {
    bg-color: rgba(40, 40, 40, 255);
    alpha-background: 1 1 .7 .7;
    draw-alpha-background: 1;
    draw-border: 1;
    border-radius: 5;
}

.popup-button-submit {
    bg-color: rgba(40, 40, 70, 255);
}

'''

def get_truncated_classname(name):
    '''Return the css-ized name of a class
    (remove the MT prefix, and all in lowercase)'''
    if name.startswith('MT'):
        name = name[2:]
    return name.lower()

widgets_parents = {}
def get_widget_parents(widget):
    global widgets_parents
    parent = [widget.__class__]
    if not widget.__class__ in widgets_parents:
        widget_classes = list()
        while parent and len(parent):
            # take only the first parent...
            widget_classes.append(get_truncated_classname(parent[0].__name__))
            # don't back too far
            if parent[0].__name__ in ['MTWidget', 'MTWindow']:
                break
            parent = parent[0].__bases__
        widgets_parents[widget.__class__] = widget_classes
    return widgets_parents[widget.__class__]

def css_get_widget_id(widget):
    if not hasattr(widget, 'cls'):
        widget.__setattr__('cls', '')
    if type(widget.cls) == str:
        idwidget = str(widget.__class__) + ':' + widget.cls
    else:
        idwidget = str(widget.__class__) + ':' + '.'.join(widget.cls)
    return idwidget

css_cache = {}
def css_get_style(widget, sheet=None):
    '''Return a dict() with all the style for the widget.

    :Parameters:
        `widget` : class
            Widget to search CSS
        `sheet` : sheet
            Custom style sheet to use (instead of pymt_sheet)
    '''

    global pymt_sheet
    global css_cache

    idwidget = css_get_widget_id(widget)
    if idwidget in css_cache:
        return css_cache[idwidget]

    if not sheet:
        sheet = pymt_sheet

    widget_classes = get_widget_parents(widget)
    widget_classes.append('*')

    styles = dict()
    rules = []

    # first, select rules that match the widget
    for w in pymt_sheet.cssRules:
        rule_selected = False
        rule_score = 0
        # get the appropriate selector
        for s in w.selectorList:
            rule_stop_processing = False
            if s.element is not None:
                if s.element[1] not in reversed(widget_classes):
                    continue
            if s.specificity[2] == 1:
                cssclass = s.selectorText.split('.')[1:]
                if type(widget.cls) == str:
                    if widget.cls not in cssclass:
                        rule_stop_processing = True
                        continue
                else:
                    rule_stop_processing = True
                    for c in widget.cls:
                        if c in cssclass:
                            rule_stop_processing = False
            if rule_stop_processing:
                continue
            # selector match !
            rule_selected = True
            # get the better score
            a, b, c, d = s.specificity
            score = b * 100 + c * 10 + d
            if score > rule_score:
                rule_score = score
        # rule ok :)
        if rule_selected:
            rules.append([rule_score, w])

    # sort by score / parent
    #TODO

    # compiles rules
    for score, rule in rules:
        for prop in rule.style.getProperties():
            value = prop.value
            if prop.name in auto_convert:
                try:
                    value = auto_convert[prop.name](prop.value)
                except:
                    pymt_logger.exception(
                        'Error while convert %s: %s' % (prop.name, prop.value))
                    pass
            styles[prop.name] = value

    css_cache[idwidget] = styles
    return styles


# Add default CSS
parser = cssutils.CSSParser(loglevel=logging.ERROR)
pymt_sheet = parser.parseString(default_css)

# Add user css if exist
pymt_home_dir = os.path.expanduser('~/.pymt/')
css_filename = os.path.join(pymt_home_dir, 'user.css')
if os.path.exists(css_filename):
    user_sheet = parser.parseFile(css_filename)
    for rule in user_sheet.cssRules:
        pymt_sheet.add(rule)

def css_add_sheet(text):
	global pymt_sheet
	pymt_sheet.cssText += text

if __name__ == '__main__':
    from pymt import *
    w = MTWidget()
    print w
    print css_get_style(widget=w)
    w = MTWindow()
    print w
    print css_get_style(widget=w)
