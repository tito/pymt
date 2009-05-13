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
__all__ = ['default_css', 'css_get_style', 'get_truncated_classname', 'pymt_sheet']

from ..logger import pymt_logger
import os
import sys
import shutil
import logging
import re
import cssutils


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
    border-radius: 0;
    border-width: 1.5;
}

vectorslider {
    slider-color: rgba(255, 71, 0, 255);
    bg-color: rgba(51, 102, 230);
}

display {
    /* color of touch */
    touch-color: rgba(255, 0, 0, 255);
}

form,
vkeyboard,
flippablewidget,
button {
    bg-color: rgba(60, 60, 60, 100);

    /* background alpha layer */
    draw-alpha-background: 0;
    alpha-background: 1, 1, 1, 1;

    /* text shadow */
    draw-text-shadow: 0;
    text-shadow-color: rgba(22, 22, 22, 63);
    text-shadow-position: -1 1;

    /* additional border */
    draw-border: 0;
}

keybutton {
    bg-color: rgba(20, 20, 20, 200);
    color-down: rgba(200, 200, 200, 150);
}

formslider,
slider, xyslider, vectorslider, multislider, boundaryslider {
    bg-color: rgb(51, 51, 51);
    slider-color: rgb(255, 127, 0);
}

kineticscrolltext {
    color: rgba(255, 255, 255, 127);
    item-color: rgb(100, 100, 100);
    item-selected: rgb(150, 150, 150);
}

kineticcontainer {
    bg-color: rgba(90, 90, 90, 127)
}

window {
    bg-color: rgb(20, 20, 20);
}

button.better {
    bg-color: rgb(50, 50, 50);
    draw-text-shadow: 1;
    draw-alpha-background: 1;
    border-radius: 8;
    font-size: 11;
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

    if widget.__class__ in css_cache:
        return css_cache[widget.__class__]

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
            if s.element[1] not in reversed(widget_classes):
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
            value = None

            # color decoder with rgb / rgba
            if len(prop.value) >= 2 and prop.value[0] in ('"', "'") and prop.value[-1] in ('"', "'"):
                value = prop.value[1:-1]
            elif prop.value.startswith('rgb'):
                res = re.match('rgba?\((.*)\)', prop.value)
                value = map(lambda x: int(x) / 255., re.split(',\ ?', res.groups()[0]))
                if len(value) == 3:
                    value.append(1)
            elif prop.value.startswith('#'):
                res = prop.value[1:]
                value = [int(x, 16)/255. for x in re.split('([0-9a-f]{2})', res) if x != '']
                if len(value) == 3:
                    value.append(1)
            else:
                value = prop.value
            styles[prop.name] = value

    css_cache[widget.__class__] = styles
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


if __name__ == '__main__':
    from pymt import *
    w = MTWidget()
    print w
    print css_get_style(widget=w)
    w = MTWindow()
    print w
    print css_get_style(widget=w)
