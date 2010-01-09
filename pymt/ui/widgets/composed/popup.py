'''
Popup: tiny popup with customizable content
'''

from ....graphx import set_color, drawCSSRectangle
from ....utils import curry
from ...factory import MTWidgetFactory
from ..widget import MTWidget
from ..button import MTButton
from ..label import MTLabel
from ..scatter import MTScatterWidget
from ..layout import MTBoxLayout


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
        self.layout = MTBoxLayout(orientation='vertical', padding=5, spacing=5)
        self.l_title = MTBoxLayout(orientation='vertical', invert_y=True, padding=5)
        self.l_content = MTBoxLayout(orientation='vertical', invert_y=True)
        self.l_buttons = MTBoxLayout(orientation='horizontal', spacing=5)

        # Titles
        if kwargs.get('title') is not None:
            self.w_title = MTLabel(label=kwargs.get('title'), font_size=10, bold=False, autoheight=True)
            self.l_title.add_widget(self.w_title)

        # Buttons
        self.w_submit = MTButton(label=kwargs.get('label_submit'), size=(100, 40),
                cls=['popup-button', 'popup-button-submit'])
        self.w_submit.push_handlers(on_release=curry(self._dispatch_event, 'on_submit'))
        self.l_buttons.add_widget(self.w_submit)
        if kwargs.get('show_cancel'):
            self.w_cancel = MTButton(label=kwargs.get('label_cancel'), size=(100, 40),
                cls=['popup-button', 'popup-button-cancel'])
            self.w_cancel.push_handlers(on_release=curry(self._dispatch_event, 'on_cancel'))
            self.l_buttons.add_widget(self.w_cancel)

        # Connect
        self.layout.add_widget(self.l_buttons)
        self.layout.add_widget(self.l_content)
        if kwargs.get('title') is not None:
            self.layout.add_widget(self.l_title)
        super(MTPopup, self).add_widget(self.layout)

    def _ensure_layout(self, force=False):
        while force or (self.size != self.layout.size):
            self.size = self.layout.size
            self.layout.do_layout()
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

MTWidgetFactory.register('MTPopup', MTPopup)
