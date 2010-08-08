'''
SpellVKeyboard: Virtual keyboard that provides spelling
                suggestions/corrections as you type.
'''

__all__ = ('MTSpellVKeyboard', )

from pymt.core.spelling import Spelling
from pymt.ui.factory import MTWidgetFactory
from pymt.ui.widgets.button import MTButton
from pymt.ui.widgets.layout import MTBoxLayout
from pymt.ui.widgets.composed.vkeyboard import MTVKeyboard
from pymt.utils import curry

class MTSpellVKeyboardLabel(MTButton):
    def __init__(self, **kwargs):
        super(MTSpellVKeyboardLabel, self).__init__(**kwargs)
        self.label_obj.color = (0, 0, 0, 1)
        self.size = self.label_obj.content_width, self.label_obj.content_height

class MTSpellVKeyboard(MTVKeyboard):
    '''
    The MTSpellVKeyboard augments the ordinary MTVKeyboard with spelling suggestions.
    You can use it instead of the MTVKeyboard. The only difference are the spelling
    suggestions that are shown on top of the widget. As you type, these are populated
    by suggestions from the system. To use a suggestion, simply tap it.

    :Parameters:
        `spelling` : Spelling object
            If provided, the keyboard uses this spelling instance (can be used to
            indicate which language should be used for spelling). If not provided,
            a fallback spelling instance will be created that uses the first language
            available.
    '''

    def __init__(self, **kwargs):
        super(MTSpellVKeyboard, self).__init__(**kwargs)
        self.last_word = ''
        self.spelling = kwargs.get('spelling', Spelling())
        self.suggests = []
        self.buttons = []
        self.slayout = MTBoxLayout(orientation='horizontal', spacing=10)
        self.add_widget(self.slayout)

    def _clear_suggestions(self):
        self.slayout.children.clear()

    def _add_suggestion(self, word):
        k = {'autoheight': True, 'font_size': 16}
        label = MTSpellVKeyboardLabel(label=' %s ' % word, **k)
        label.connect('on_press', curry(self._press_suggestion, word))
        self.slayout.add_widget(label)

    def _press_suggestion(self, word, *largs):
        l = len(self.last_word)
        if not l:
            return
        self.text = self.text[0:-l] + word
        self._clear_suggestions()

    def on_touch_down(self, touch):
        x, y = self.to_local(touch.x, touch.y)
        touch.push('xy')
        touch.x, touch.y = x, y
        if self.slayout.dispatch_event('on_touch_down', touch):
            touch.pop()
            return True
        touch.pop()
        return super(MTSpellVKeyboard, self).on_touch_down(touch)

    def on_text_change(self, text):
        self._clear_suggestions()
        if len(text) == 0:
            return

        l = text.replace('\r\n,.:; ', ' ')
        self.last_word = l.split(' ')[-1]
        if self.last_word == '':
            return

        self._add_suggestion(self.last_word)

        self.suggests = self.spelling.suggest(self.last_word)[:10]
        for word in self.suggests:
            self._add_suggestion(word)

    def on_update(self):
        # ensure the layout position
        self.slayout.pos = (5, self.height + 5)
        super(MTSpellVKeyboard, self).on_update()


MTWidgetFactory.register('MTSpellVKeyboard', MTSpellVKeyboard)

