'''
Factory: all widgets are registered through this factory

It is needed for external instance, like XMLWidget.
'''

__all__ = ('MTWidgetFactory', )

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


