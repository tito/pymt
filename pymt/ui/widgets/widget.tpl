'''
CustomWidget: A line description for your widget or the package

You can explain the purpose of your widget, and write a simple
example. Document only the new function provided by your widget.
For example, don't add documentation for function like draw(),
or add_widget().
'''

__all__ = ['MTCustomWidget']

from widget import MTWidget
from ..factory import MTWidgetFactory

class MTCustomWidget(MTWidget):
    '''Description of the widget. You can explain the purpose,
    the default behavior, and write some examples if appropriate.
    Example must start with double-dash like ::

        from pymt import *
        w = MTCustomWidget(param1="title")


    :Parameters:
        `param1` : type, default is "defaultstringvalue"
            Description of param1
        `param2` : type, default is 0
            Description of param2

    :Styles:
        `cw-background` : type
            Description of css attribute

    :Events:
        `on_event1`
            Description of event1
	'''
    def __init__(self, **kwargs):
        # 1: set default value for your param
        kwargs.setdefault('param1', 'defaultstringvalue')
        kwargs.setdefault('param2', 0)

        # 2: call the parent initializer
        super(MTCustomWidget, self).__init__(**kwargs)

        # 3: save own param
        self.param1 = kwargs.get('param1')
        self.param2 = kwargs.get('param2')

        # 4: register event
        self.register_event_type('on_event1')

    def apply_css(self, styles):
        if 'cw-background' in styles:
            self.background = styles.get('cw-background')
        super(MTCustomWidget, self).apply_css(styles)


# Register all base widgets
MTWidgetFactory.register('MTCustomWidget', MTCustomWidget)
