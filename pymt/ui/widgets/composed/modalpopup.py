'''
ModalPopup: a simple popup that use modal window
'''

__all__ = ['MTModalPopup']

from ..modalwindow import MTModalWindow
from ..form.form import MTForm
from ..form.button import MTFormButton
from ..form.label import MTFormLabel
from ..layout.boxlayout import MTBoxLayout
from ...factory import MTWidgetFactory

class MTModalPopup(MTModalWindow):
    '''A simple implementation of a popup.

    :Parameters:
        `title` : str, default is 'Information'
            Title of popup
        `content` : str, default is ''
            Content of popup
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('title', 'Information')
        kwargs.setdefault('content', '')
        super(MTModalPopup, self).__init__(**kwargs)
        self.title      = kwargs.get('title')
        self.content    = kwargs.get('content')

        self.form = MTForm(layout=MTBoxLayout(
            padding=10, spacing=10, orientation='vertical',
            invert_y=True, uniform_width=True
        ))
        self.submit = MTFormButton(label='OK', cls='popup-submit')
        self.submit.push_handlers(on_release=self.action_close_popup)
        self.form.add_widget(MTFormLabel(label=self.title, cls='popup-title'))
        self.form.add_widget(MTFormLabel(label=self.content, cls='popup-content'))
        self.form.add_widget(self.submit)
        super(MTModalPopup, self).add_widget(self.form)

    def action_close_popup(self, *largs):
        self.parent.remove_widget(self)

    def add_widget(self, widget):
        raise Exception('MTModalPopup cannot have children')

    def draw(self):
        w = self.get_parent_window()
        if self.form.x == 0:
            x = (w.width - self.form.width) / 2
            y = (w.height - self.form.height) / 2
            self.form.pos = (x, y)
        super(MTModalPopup, self).draw()


# Register all base widgets
MTWidgetFactory.register('MTModalPopup', MTModalPopup)
