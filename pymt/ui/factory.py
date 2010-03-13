'''
Factory: all widgets are registered through this factory

It is needed for external instance, like XMLWidget.
'''

__all__ = ['MTWidgetFactory']

class MTWidgetFactory(object):
    '''Widget factory. Designed to register all the PyMT widget,
    and get them from a limited context (like eval)
    '''

    _widgets = {}

    @staticmethod
    def register(widgetname, widgetclass):
        '''Add a widget into our database'''
        if not widgetname in MTWidgetFactory._widgets:
            MTWidgetFactory._widgets[widgetname] = widgetclass

    @staticmethod
    def get(widgetname):
        '''Get a widget from database'''
        if widgetname in MTWidgetFactory._widgets:
            return MTWidgetFactory._widgets[widgetname]
        raise Exception('Widget %s are not known in MTWidgetFactory' % widgetname)

real_import = False
modules_instances = {}
modules_import = {}
modules = {
    'MTAnchorLayout':          'widgets.layout.anchorlayout',
    'MTBoundarySlider':        'widgets.slider',
    'MTBoxLayout':             'widgets.layout.boxlayout',
    'MTButton':                'widgets.button',
    'MTButtonMatrix':          'widgets.buttonmatrix',
    'MTCircularSlider':        'widgets.circularslider',
    'MTColorPicker':           'widgets.composed.colorpick',
    'MTContainer':             'widgets.container',
    'MTCoverFlow':             'widgets.coverflow',
    'MTDisplay':               'widgets.display',
    'MTDragable':              'widgets.dragable',
    'MTFileBrowser':           'widgets.composed.filebrowser',
    'MTFileBrowserView':       'widgets.composed.filebrowser',
    'MTFileEntryView':         'widgets.composed.filebrowser',
    'MTFileIconEntryView':     'widgets.composed.filebrowser',
    'MTFileListEntryView':     'widgets.composed.filebrowser',
    'MTFlippableWidget':       'widgets.flippable',
    'MTForm':                  'widgets.form.form',
    'MTFormButton':            'widgets.form.button',
    'MTFormCheckbox':          'widgets.form.checkbox',
    'MTFormInput':             'widgets.form.input',
    'MTFormLabel':             'widgets.form.label',
    'MTFormSlider':            'widgets.form.slider',
    'MTGestureWidget':         'widgets.gesturewidget',
    'MTGridLayout':            'widgets.layout.gridlayout',
    'MTImageButton':           'widgets.button',
    'MTInnerWindow':           'widgets.composed.innerwindow',
    'MTKinetic':               'widgets.kinetic',
    'MTKineticImage':          'widgets.composed.kineticlist',
    'MTKineticItem':           'widgets.composed.kineticlist',
    'MTKineticList':           'widgets.composed.kineticlist',
    'MTKineticObject':         'widgets.composed.kineticlist',
    'MTLabel':                 'widgets.label',
    'MTModalPopup':            'widgets.composed.modalpopup',
    'MTModalWindow':           'widgets.modalwindow',
    'MTMultiSlider':           'widgets.slider',
    'MTObjectDisplay':         'widgets.objectdisplay',
    'MTPopup':                 'widgets.composed.popup',
    'MTRectangularWidget':     'widgets.rectangle',
    'MTScatterContainer':      'widgets.scatter',
    'MTScatterImage':          'widgets.scatter',
    'MTScatterPlane':          'widgets.scatter',
    'MTScatterSvg':            'widgets.scatter',
    'MTScatterWidget':         'widgets.scatter',
    'MTScreenLayout':          'widgets.layout.screenlayout',
    'MTSidePanel':             'widgets.sidepannel',
    'MTSimpleVideo':           'widgets.composed.video',
    'MTSlider':                'widgets.slider',
    'MTSpeechBubble':          'widgets.speechbubble',
    'MTStencilContainer':      'widgets.stencilcontainer',
    'MTSvg':                   'widgets.svg',
    'MTSvgButton':             'widgets.svg',
    'MTTabs':                  'widgets.composed.tabs',
    'MTTextArea':              'widgets.composed.textarea',
    'MTTextInput':             'widgets.composed.textinput',
    'MTToggleButton':          'widgets.button',
    'MTVKeyboard':             'widgets.composed.vkeyboard',
    'MTVectorSlider':          'widgets.slider',
    'MTVideo':                 'widgets.composed.video',
    'MTWidget':                'widgets.widget',
    'MTWindow':                'window',
    'MTXYSlider':              'widgets.slider',
    'XMLWidget':               'widgets.xmlwidget',
}

def import_library(name):
    if name not in modules_import:
        m = 'pymt.ui.%s' % modules[name]
        import sys
        print 'REAL IMPORT', m, len(sys.modules)
        modules_import[name] = __import__(m, globals(), locals(), name)
    return getattr(modules_import[name], name)

class MetaClass(type):
    def __new__(meta, classname, bases, classDict):
        print 'Class Name:', classname
        print 'Bases:', bases
        print 'Class Attributes', classDict
        return type.__new__(meta, classname, bases, classDict)

class _WidgetAutoLoad(object):
    #__metaclass__ = MetaClass
    def __init__(self, modname):
        self.__dict__['__name__'] = modname
        modules_instances[self] = modname

    def __call__(self, *largs, **kwargs):
        print '__call__', self.__name__
        m = import_library(self.__name__)
        return m(*largs, **kwargs)

    def __getattr__(self, key):
        print '__getattr__', self.__name__, key
        m = import_library(self.__name__)
        return getattr(m, key)

    def __setattr(self, key, val):
        print '__setattr__', self.__name__, key, val
        m = import_library(self.__name__)
        return setattr(m, key, val)

    def __new__(cls, *largs):
        if not real_import:
            return object.__new__(_WidgetAutoLoad)

        # already imported
        if cls in modules_import:
            return cls.__new__(*largs)

        # first import
        name, bases, dicts = largs

        newbases = []
        for base in bases:
            # search base in our instances
            if base in modules_instances:
                basename = modules_instances[base]
                # load too !
                newbases.append(import_library(basename))
            else:
                newbases.append(base)

        return type.__new__(type, name, tuple(newbases), dicts)



for name, lib in modules.items():
    globals()[name] = _WidgetAutoLoad(name)
    __all__.append(name)

real_import = True
