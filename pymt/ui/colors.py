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

    /* selected text color */
    color-selected: rgba(255, 120, 255, 255);

    /* color when something is pushed */
    color-down: rgba(50, 50, 50, 150);

    /* background color of widget */
    bg-color: rgba(60, 60, 60, 150);

    /* font size */
    font-size: 10;
}

vkeyboard,
button {
    bg-color: rgba(20, 20, 20, 100);
}

keybutton {
    bg-color: rgba(20, 20, 20, 200);
}

form {
    bg-color: rgba(80, 80, 80, 100);
}

slider, xyslider, vectorslider, multislider {
    bg-color: rgb(51, 51, 51);
    slider-color: rgb(255, 127, 0);
}

kineticscrolltext {
    item-color: rgb(100, 100, 100);
    item-selected: rgb(150, 150, 150);
}

window {
    bg-color: rgb(45, 45, 45);
}
'''

def get_truncated_classname(name):
    if name.startswith('MT'):
        name = name[2:]
    return name.lower()

def css_get_style(widget=None, sheet=None):
    global pymt_sheet
    if not sheet:
        sheet = pymt_sheet

    widget_classes = list()
    parent = [widget.__class__]
    while parent and len(parent):
        # take only the first parent...
        widget_classes.append(get_truncated_classname(parent[0].__name__))
        # don't back too far
        if parent[0].__name__ in ['MTWidget', 'MTWindow']:
            break
        parent = parent[0].__bases__
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
            if prop.value.startswith('rgb'):
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
