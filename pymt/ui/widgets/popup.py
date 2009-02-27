from modalwindow import MTModalWindow
from form import *
from layout import *
from pymt.ui.factory import MTWidgetFactory

class MTPopup(MTModalWindow):
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
        super(MTPopup, self).__init__(**kwargs)
        self.title      = kwargs.get('title')
        self.content    = kwargs.get('content')
        self.window     = None

        self.form = MTForm(layout=MTBoxLayout(
            padding=10, spacing=10, orientation='vertical',
            invert_y=True, uniform_width=True
        ))
        self.submit = MTFormButton(label='OK')
        self.submit.push_handlers(on_release=self.action_close_popup)
        self.form.add_widget(MTFormLabel(label=self.title, halign='left',
                                         font_style='bold', font_size=16))
        self.form.add_widget(MTFormLabel(label=self.content, halign='left',
                                         multiline=True, width=self.width))
        self.form.add_widget(self.submit)
        super(MTPopup, self).add_widget(self.form)

    def action_close_popup(self, touchID, x, y):
        self.parent.remove_widget(self)

    def add_widget(self, widget):
        raise Exception('MTPopup cannot have children')

    def draw(self):
        w = self.get_parent_window()
        if self.form.x == 0:
            x = (w.width - self.form.width) / 2
            y = (w.height - self.form.height) / 2
            self.form.pos = (x, y)
        super(MTPopup, self).draw()


# Register all base widgets
MTWidgetFactory.register('MTPopup', MTPopup)
