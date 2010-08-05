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

__all__ = (
    'css_get_style', 'get_truncated_classname',
    'pymt_sheet', 'css_add_sheet', 'css_add_file', 'css_get_widget_id',
    'css_register_state', 'css_add_keyword', 'css_register_prefix',
    'css_reload'
)

from pymt.logger import pymt_logger
from pymt.cache import Cache
from pymt.parser import parse_color, parse_image, parse_float4, \
        parse_float, parse_bool, parse_int, parse_int2, parse_string
from pymt import pymt_data_dir, pymt_home_dir
import os
import sys
import shutil
import logging
import re
import weakref

# Register CSS cache
Cache.register('pymt.css', limit=500, timeout=60)

#: Instance of the CSS sheet
pymt_sheet = None

#: State allowed to CSS rules (bg-color[-state] for eg)
pymt_css_states = ['-down', '-move', '-dragging', '-active', '-error',
                   '-validated', '-syskey']

#: Prefix allowed to CSS rules
pymt_css_prefix = ['key-', 'slider-', 'title-']

# Privates vars for reload features
_css_sources = []
_css_widgets = set()

# Auto conversion from css to a special type.
css_keyword_convert = {
    'color':                    parse_color,
    'bg-color':                 parse_color,
    'bg-color-full':            parse_color,
    'font-size':                parse_int,
    'font-name':                parse_string,
    'font-weight':              parse_string,
    'font-color':               parse_color,
    'border-image':             parse_string,
    'border-image-width':       parse_float4,
    'border-width':             parse_float,
    'border-radius':            parse_int,
    'border-radius-precision':  parse_float,
    'border-color':             parse_color,
    'slider-color':             parse_color,
    'touch-color':              parse_color,
    'draw-background':          parse_bool,
    'draw-text-shadow':         parse_bool,
    'draw-border':              parse_bool,
    'draw-border-image':        parse_bool,
    'draw-alpha-background':    parse_bool,
    'text-shadow-color':        parse_color,
    'text-shadow-position':     parse_int2,
    'alpha-background':         parse_float4,
    'item-color':               parse_color,
    'item-selected':            parse_color,
    'padding':                  parse_int2,
    'slider-border-radius':     parse_int,
    'slider-border-radius-precision': parse_float,
    'slider-alpha-background':  parse_float4,
    'slider-draw-background':   parse_bool,
    'draw-slider-border':       parse_bool,
    'draw-slider-alpha-background': parse_bool,
    'key-border-radius':        parse_int,
    'key-border-radius-precision': parse_float,
    'key-alpha-background':     parse_float4,
    'key-draw-background':      parse_bool,
    'key-border-color':         parse_color,
    'draw-key-border':          parse_bool,
    'draw-key-alpha-background': parse_bool,
    'vector-color':             parse_color,
    'title-color':              parse_color,
    'title-border-radius':      parse_int,
    'title-border-radius-precision': parse_float,
    'title-alpha-background':   parse_float4,
    'title-draw-background':    parse_bool,
    'draw-title-border':        parse_bool,
    'draw-title-alpha-background': parse_bool,
    'margin':                   parse_float4,
    'key-color':                parse_color,
    'syskey-color':             parse_color,
    'scrollbar-size':           parse_float,
    'scrollbar-margin':         parse_float4,
    'scrollbar-color':          parse_color,
    'bg-image':                 parse_image,
    'selected-color':           parse_color,
}

class CSSSheet(object):
    def __init__(self):
        self._rule = ''
        self._content = ''
        self._state = 'rule'
        self._css = {}

    def reset(self):
        self._rule = ''
        self._content = ''
        self._state = 'rule'
        self._css = {}

    def parse_text(self, text):
        '''Parse a CSS text, and inject in the current sheet'''
        # remove comment
        def _comment_remover(text):
            def replacer(match):
                s = match.group(0)
                if s.startswith('/'):
                    return ""
                else:
                    return s
            pattern = re.compile(
                r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
                re.DOTALL | re.MULTILINE
            )
            return re.sub(pattern, replacer, text)

        text = _comment_remover(text)
        self._rule = ''
        for line in text.split('\n'):
            self._parse_line(line)

    def _parse_line(self, line):
        '''Parse a line, and inject into rules or content, depend on current
        parser state'''
        if self._state == 'rule':
            r = line.split('{', 1)
            self._rule += ',' + r[0]
            if len(r) != 1:
                self._state = 'content'
                self._parse_line(r[1])

        elif self._state == 'content':
            r = line.split('}', 1)
            self._content += ';' + r[0]
            if len(r) != 1:
                self._push(self._rule, self._content)
                self._rule = ''
                self._content = ''
                self._state = 'rule'
                self._parse_line(r[1])

    def _push(self, rulestr, contentstr):
        '''Push a rules/contents into our sheet'''
        def extract(v):
            sname, svalue = v.split(':')
            name = sname.strip()
            value = svalue.strip()
            if name not in css_keyword_convert:
                # searching for a state
                for state in pymt_css_states:
                    if name.endswith(state):
                        name = name[:-len(state)]
                        break
                # searching for a prefix
                for prefix in pymt_css_prefix:
                    if name.startswith(prefix):
                        name = name[len(prefix):]
                        break
            if name in css_keyword_convert:
                try:
                    value = css_keyword_convert[name](value)
                except Exception:
                    pymt_logger.exception(
                        'Error while convert %s: %s' % (name, value))
            return sname.strip(), value

        rules = [x.strip() for x in rulestr.split(',') if x.strip() != '']
        keys = [extract(x.strip()) for x in contentstr.split(';') if x.strip() != '']
        for rule in rules:
            if rule in self._css:
                self._css[rule].update(dict(keys[:]))
            else:
                self._css[rule] = dict(keys[:])

    def get_style(self, widget):
        '''Return the style of a widget'''
        widget_classes = get_widget_parents(widget)
        widget_classes.append('*')
        styles = {}

        # 
        # TODO rework this part to match
        # #<objectid>  uniq
        # <objectname> uniq
        # .<class>     multiple
        #

        # match <objectname>
        for cls in reversed(widget_classes):
            for r, v in self._css.iteritems():
                if r == cls:
                    styles.update(v)

        # match .<classname>
        widget_cls = widget.cls
        if type(widget_cls) in (unicode, str):
            widget_cls = [widget.cls]
        if type(widget_cls) in (list, tuple):
            for kcls in widget_cls:
                cls = '.%s' % kcls
                if cls in self._css:
                    styles.update(self._css[cls])

                # match <objectname>.<classname>
                for name in reversed(widget_classes):
                    lcls = '%s%s' % (name, cls)
                    for r, v in self._css.iteritems():
                        if r == lcls:
                            styles.update(v)

        # match #<objectname>
        if hasattr(widget, 'id') and widget.id is not None:
            widgetid = '#%s' % widget.id
            if widgetid in self._css:
                styles.update(self._css[widgetid])

        return styles

def get_truncated_classname(name):
    '''Return the css-ized name of a class
    (remove the MT prefix, and all in lowercase)'''
    if name.startswith('MT'):
        name = name[2:]
    return name.lower()

widgets_parents = {}
def get_widget_parents(widget):
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
    '''Return the css id of a widget'''
    if not hasattr(widget, 'cls'):
        widget.__setattr__('cls', '')
    cls = widget.cls
    if type(cls) in (tuple, list):
        cls = '.'.join(cls)
    cid = ''
    if hasattr(widget, 'id') and widget.id:
        cid = '#%s#' % getattr(widget, 'id')
    idwidget = cid + str(widget.__class__) + ':' + cls
    return idwidget

def css_get_style(widget):
    '''Return a dict() with all the style for the widget.

    :Parameters:
        `widget`: class
            Widget to search CSS
    '''

    global pymt_sheet

    ref = weakref.ref(widget)
    if not ref in _css_widgets:
        _css_widgets.add(ref)

    idwidget = css_get_widget_id(widget)
    styles = Cache.get('pymt.css', idwidget)
    if styles is not None:
        return styles

    styles = pymt_sheet.get_style(widget)
    Cache.append('pymt.css', idwidget, styles)
    return styles

def css_add_sheet(text, _reload=False):
    '''Add a css text to use.
    Example ::

        mycss = '#buttonA { bg-color: rgba(255, 127, 0, 127); }'
        css_add_sheet(mycss)

    '''
    pymt_sheet.parse_text(text)
    if not _reload:
        _css_sources.append((css_add_sheet, (text, )))

def css_add_file(cssfile, _reload=False):
    '''Add a css file to use.
    Adds all the css rules in the given file to the pymt css rule set being
    used ::

        css_add_sheet(cssfile)

    '''
    with open(cssfile, 'r') as fd:
        pymt_sheet.parse_text(fd.read())
    if not _reload:
        _css_sources.append((css_add_file, (cssfile, )))

def css_register_state(name):
    '''Register a new state'''
    pymt_css_states.append('-%s' % name)

def css_register_prefix(name):
    '''Register a new prefix'''
    pymt_css_prefix.append('%s-' % name)

def css_add_keyword(keyword, convertfunc):
    '''Add a new keyword to be autoconverted when reading CSS.
    Convert function can be found in parser.py'''
    css_keyword_convert[keyword] = convertfunc

def css_reload():
    pymt_logger.debug('CSS: Reloading CSS in progress')
    pymt_sheet.reset()
    for callback, args in _css_sources[:]:
        callback(*args, _reload=True)
    Cache.remove('pymt.css')
    for r in _css_widgets.copy():
        o = r()
        if o is None:
            _css_widgets.remove(r)
            continue
        o.reload_css()
    pymt_logger.info('CSS: CSS Reloaded')

# Autoload the default css + user css
if 'PYMT_DOC' not in os.environ:
    # Add default CSSheet
    pymt_sheet = CSSSheet()
    css_add_file(os.path.join(pymt_data_dir, 'default.css'))

    # Add user css if exist
    css_filename = os.path.join(pymt_home_dir, 'user.css')
    if os.path.exists(css_filename):
        css_add_file(css_filename)


if __name__ == '__main__':
    from pymt import MTWidget, css_get_style, MTWindow
    w = MTWidget()
    print w
    print css_get_style(widget=w)
    w = MTWindow()
    print w
    print css_get_style(widget=w)
