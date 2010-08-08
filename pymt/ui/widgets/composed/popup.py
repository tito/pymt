'''
Popup: tiny popup with customizable content
'''

__all__ = ('MTPopup', )

from pymt.graphx import set_color, drawCSSRectangle
from pymt.utils import curry
from pymt.ui.widgets.button import MTButton
from pymt.ui.widgets.label import MTLabel
from pymt.ui.widgets.scatter import MTScatterWidget
from pymt.ui.widgets.layout import MTBoxLayout


class MTPopup(MTScatterWidget):
    '''Popup with customizable content.

    :Parameters:
        `show_cancel`: bool, default to True
            Show/hide the cancel button
        `label_cancel`: str, default to 'Cancel'
            Change the label of cancel button
        `label_submit`: str, default to 'Ok'
            Change the label of submit button
        `title`: str, default to 'PyMT popup'
            Title of the popup (if None, no title will be added.)
        `exit_on_submit`: bool, default to 'True'
            Title of the popup (if None, no title will be added.)

    :Events:
        `on_submit`
            Fired when the popup submit button is pressed.
            In default behavior, the widget remove himself from parent.
        `on_cancel`
            Fired when the popup cancel button is pressed.
            In default behavior, the widget remove himself from parent.
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('do_scale', False)
        kwargs.setdefault('size', (400, 400))
        kwargs.setdefault('show_cancel', True)
        kwargs.setdefault('label_cancel', 'Cancel')
        kwargs.setdefault('label_submit', 'Ok')
        kwargs.setdefault('title', 'PyMT popup')
        kwargs.setdefault('exit_on_submit', True)
        super(MTPopup, self).__init__(**kwargs)

        self.register_event_type('on_submit')
        self.register_event_type('on_cancel')

        self.exit_on_submit = kwargs.get('exit_on_submit')

        # Create layouts
        self.layout = MTBoxLayout(size=self.size,  orientation='vertical')
        self.l_content = MTBoxLayout(orientation='vertical')
        self.l_buttons = MTBoxLayout(size_hint=(1, None),
                                     orientation='horizontal')

        # Titles
        if kwargs.get('title'):
            self.w_title = MTLabel(label=kwargs.get('title'),
                                   autosize=True, cls='popup-title')

        # Buttons
        self.w_submit = MTButton(label=kwargs.get('label_submit'),
                                 size_hint=(0.5, None), height=40,
                                 cls='popup-button')
        self.w_submit.push_handlers(on_release=curry(
            self._dispatch_event, 'on_submit'))
        self.l_buttons.add_widget(self.w_submit)
        if kwargs.get('show_cancel'):
            self.w_cancel = MTButton(label=kwargs.get('label_cancel'),
                                     size_hint=(0.5, None), height=40,
                                     cls='popup-button')
            self.w_cancel.push_handlers(on_release=curry(
                self._dispatch_event, 'on_cancel'))
            self.l_buttons.add_widget(self.w_cancel)

        # Connect
        if kwargs.get('title'):
            self.layout.add_widget(self.w_title)
        self.layout.add_widget(self.l_content)
        self.layout.add_widget(self.l_buttons)
        super(MTPopup, self).add_widget(self.layout)

    def _ensure_layout(self, force=False):
        while force or (self.size != self.layout.size):
            self.layout.do_layout()
            self.size = self.layout.size
            force = False

    def add_widget(self, widget, force=False):
        self.l_content.add_widget(widget)
        self._ensure_layout(force)

    def remove_widget(self, widget, force=False):
        self.l_content.remove_widget(widget)
        self._ensure_layout(force)

    def close(self):
        if self.exit_on_submit:
            self.parent.remove_widget(self)
        else:
            self.hide()

    def on_submit(self):
        self.close()

    def on_cancel(self):
        self.close()

    def _dispatch_event(self, event, *largs):
        self.dispatch_event(event)

    def draw(self):
        # draw background
        set_color(*self.style['bg-color'])
        drawCSSRectangle(size=self.size, style=self.style)
