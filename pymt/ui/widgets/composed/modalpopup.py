'''
ModalPopup: a simple popup that use modal window
'''

__all__ = ('MTModalPopup', )

from pymt.ui.widgets.xmlwidget import XMLWidget
from pymt.ui.widgets.modalwindow import MTModalWindow
from pymt.graphx import set_color, drawCSSRectangle
from pymt.vector import Vector

def escape(s):
    return s.replace('"', '\\&quot;').replace('\'', '\\&quot;').replace('<', '&lt;').replace('>', '&gt;')

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
        kwargs.setdefault('size_hint', (1, 1))
        super(MTModalPopup, self).__init__(**kwargs)
        self.title      = kwargs.get('title')
        self.content    = kwargs.get('content')

        layout = '''
            <MTBoxLayout id='"popup"' orientation='"vertical"'
                size='%s' size_hint='(None, None)'>
                <MTLabel id='"popuptitle"' cls='"modalpopup-title"' label='"%s"'
                    size_hint='(1,None)' autosize='False' autowidth='False'
                    autoheight='False' halign='"center"' valign='"center"'
                    anchor_y='"center"' height='40'/>
                <MTLabel id='"popupcontent"' cls='"modalpopup-content"' label='"%s"'
                    size_hint='(1,1)' autosize='False' autowidth='False'
                    multiline='True'
                    autoheight='False' halign='"center"' anchor_y='"center"'/>
                <MTButton id='"popupsubmit"' cls='"modalpopup-submit"' label='"OK"'
                    size_hint='(1,None)' height='40' valign='"center"'
                    halign='"center"'/>
            </MTBoxLayout>
        ''' % (str(self.size),
               escape(self.title),
               escape(self.content))

        xml = XMLWidget(xml=layout)
        super(MTModalPopup, self).add_widget(xml.root)
        xml.autoconnect(self)
        self._xml = xml

    def on_popup_draw(self):
        self._xml.root.center = self.get_parent_window().center
        popup = self._xml.getById('popup')
        set_color(*self.style.get('bg-color-full'))
        drawCSSRectangle(
            pos=Vector(popup.pos) - (10, 10),
            size=Vector(popup.size) + (20, 20),
            style=self.style)

    def on_popupsubmit_release(self, *largs):
        self.parent.remove_widget(self)

    def add_widget(self, widget):
        raise Exception('MTModalPopup cannot have children')
