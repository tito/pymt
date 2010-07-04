'''
TextInputSpellCheck: One-line textinput widget with added spelling correction
                     and word suggestion features.
'''

__all__ = ['MTTextInputSpellCheck']

from pymt.graphx import getLabel, set_color, drawLine, drawLabel
from pymt.core.spelling import Spelling
from pymt.ui.widgets.composed import MTTextInput


class MTTextInputSpellCheck(MTTextInput):
    def __init__(self, spelling=Spelling(), auto_correct=True, **kwargs):
        super(MTTextInputSpellCheck, self).__init__(**kwargs)
        self.spelling = spelling
        self.auto_correct = auto_correct
        self.connect('on_text_change', self.check_text)
        self.checked = []
        self.widths = []
        self.lines = []
        self._sep_width = 0
        self._sep_height = 0

    def check_text(self, *args):
        if self.password:
            return
        # XXX should be all whitespace chars, no?
        words = self.value.split(" ")
        c = self.spelling.check
        self.checked = [c(w) for w in words]

        # We're not using a monospace font, hence we need to
        # get the widths of the words to draw red lines below
        # incorrectly spelled words.
        font_size = self.style['font-size']
        sep = getLabel(' ', font_size=font_size, **self.style)
        self._sep_width = sep.width
        self._sep_height = sep.height
        self.widths = [getLabel(w, font_size=font_size, **self.style).width for w in words]

        pos = list(self.center)
        if self.anchor_x == 'left':
            pos[0] = self.x
        elif self.anchor_x == 'right':
            pos[0] = self.x + self.width
        if self.anchor_y == 'top':
            pos[1] = self.y + self.height
        elif self.anchor_y == 'bottom':
            pos[1] = self.y

        cur_x, y = pos
        y -= self._sep_height / 2
        self.lines = []
        for valid, width in zip(self.checked, self.widths):
            if not valid and valid is not None:
                self.lines.append((cur_x, y, cur_x + width, y))
            cur_x += self._sep_width + width

    def draw(self):
        super(MTTextInputSpellCheck, self).draw()
        set_color(1, 0, 0)
        for line in self.lines:
            drawLine(line)


if __name__ == '__main__':
    from pymt import runTouchApp
    ti = MTTextInputSpellCheck()
    runTouchApp(ti)

