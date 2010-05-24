from pymt import *

# TODO:
#       1. integrate this into vkeyboard.py???
#       2. don't hardcode 'en' language
#       3. maybe make keys that are less likely as next key darker?


css_spell_vkeyboard_label = '''
spellvkeyboardlabel {
    -bg-color: rgba(208, 208, 208, 255);
    draw-border: 1;
    border-radius: 5;
    draw-alpha-background: 1;
    alpha-background: 1 1 .1 .1;
    border-radius-precision: .25;
}
'''

css_add_sheet(css_spell_vkeyboard_label)

class MTSpellVKeyboardLabel(MTButton):
    def __init__(self, **kwargs):
        super(MTSpellVKeyboardLabel, self).__init__(**kwargs)
        self.label_obj.color = (0, 0, 0, 1)
        self.size = self.label_obj.content_width, self.label_obj.content_height

class MTSpellVKeyboard(MTVKeyboard):
    def __init__(self, **kwargs):
        super(MTSpellVKeyboard, self).__init__(**kwargs)
        self.last_word = ''
        # XXX Make this a config option!
        self.spelling = Spelling('en')
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


if __name__ == '__main__':
    m = MTTextInput(keyboard=MTSpellVKeyboard(), font_size=42)
    runTouchApp(m)
