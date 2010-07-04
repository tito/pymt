'''
TextInputSpellCheck: One-line textinput widget with added spelling correction
                     and word suggestion features.
'''

__all__ = ['MTTextInputSpellCheck']

from pymt.utils import curry
from pymt.graphx import getLabel, set_color, drawLine, drawLabel
from pymt.core.spelling import Spelling
from pymt.ui.widgets import MTButton
from pymt.ui.widgets.composed import MTTextInput
from pymt.ui.widgets.klist import MTList
from pymt.ui.widgets.layout.boxlayout import MTBoxLayout


class MTTextInputSpellCheck(MTTextInput):
    def __init__(self, spelling=Spelling(), auto_correct=True, **kwargs):
        super(MTTextInputSpellCheck, self).__init__(**kwargs)
        self.spelling = spelling
        self.auto_correct = auto_correct
        self.connect('on_text_change', self.check_text)
        self.words = []
        self.checked = []
        self.widths = []
        self.lines = []
        self._sep_width = 0
        self._sep_height = 0

    def check_text(self, *args):
        if self.password:
            return
        # XXX should be all whitespace chars, no?
        self.words = self.value.split(" ")
        c = self.spelling.check
        self.checked = [c(w) for w in self.words]

        # We're not using a monospace font, hence we need to
        # get the widths of the words to draw red lines below
        # incorrectly spelled words.
        font_size = self.style['font-size']
        sep = getLabel(' ', font_size=font_size, **self.style)
        self._sep_width = sep.width
        self._sep_height = sep.height
        self.widths = [getLabel(w, font_size=font_size, **self.style).width for w in self.words]

        cur_x, y = self.get_text_pos()
        self.lines = []
        for valid, width in zip(self.checked, self.widths):
            if not valid and valid is not None:
                self.lines.append((cur_x, y, cur_x + width, y))
            cur_x += self._sep_width + width

    def get_text_pos(self):
        pos = list(self.center)
        if self.anchor_x == 'left':
            pos[0] = self.x
        elif self.anchor_x == 'right':
            pos[0] = self.x + self.width
        if self.anchor_y == 'top':
            pos[1] = self.y + self.height
        elif self.anchor_y == 'bottom':
            pos[1] = self.y

        x, y = pos
        y -= self._sep_height / 2
        return x, y

    def on_touch_down(self, touch):
        # XXX missing self.collide_point
        touch.userdata[MTTextInputSpellCheck] = self
        super(MTTextInputSpellCheck, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        # XXX missing self.collide_point
        was_in = touch.userdata.get(MTTextInputSpellCheck) is self
        if was_in:
            # Calculate the word that was tapped
            x, y = touch.pos
            tx, ty = self.get_text_pos()
            if ty <= y <= ty + self._sep_height and \
               tx <= x <= sum(self.widths) + (len(self.widths)-1) * self._sep_width:
                cur_x = tx
                for index, width in enumerate(self.widths):
                    cur_x += width
                    if x <= cur_x:
                        # Found what we're looking for.
                        break
                    cur_x += self._sep_width

                # OK, set up the list of word suggestions!
                layout = MTBoxLayout(orientation='vertical')
                suggestions = self.spelling.suggest(self.words[index])
                btns = [MTButton(label=s, auto_height=True) for s in suggestions]
                layout.add_widgets(*btns)
                print btns
                lst = MTList(pos=(200, 200), size=(200, 500), do_y=True)
                lst.add_widget(layout)
                for btn in btns:
                    btn.connect('on_press', curry(self.replace_word, index, btn.label, lst))
                self.add_widget(lst)
            return True
        super(MTTextInputSpellCheck, self).on_touch_up(touch)

    def replace_word(self, *args):
        print args

    def draw(self):
        super(MTTextInputSpellCheck, self).draw()
        set_color(1, 0, 0)
        for line in self.lines:
            drawLine(line)


if __name__ == '__main__':
    from pymt import runTouchApp
    ti = MTTextInputSpellCheck()
    runTouchApp(ti)

