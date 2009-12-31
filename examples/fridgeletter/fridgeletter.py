from pymt import *
from random import randint

# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Fridge letter'
PLUGIN_AUTHOR = 'Mathieu Virbel'
PLUGIN_DESCRIPTION = 'Original idea from leijou (see README for more info.)'

class FridgeLetterAtomic(MTDragable):
    def __init__(self, **kwargs):
        kwargs.setdefault('letter', 'A')
        kwargs.setdefault('color', (1, 0, 0, 1))
        super(FridgeLetterAtomic, self).__init__(**kwargs)

        self.letter = Label(
            font_name = 'AlphaFridgeMagnets.ttf',
            font_size = 48,
            bold = True,
            anchor_x = 'left',
            anchor_y = 'bottom',
            multiline = False,
            halign = 'top',
            color = kwargs.get('color'),
            label = kwargs.get('letter')
        )
        self.size = self.letter.content_width, self.letter.content_height

    def draw(self):
        self.letter.x, self.letter.y = self.pos
        self.letter.draw()

class FridgeLetter(MTWidget):
    def __init__(self, **kwargs):
        super(FridgeLetter, self).__init__(**kwargs)
        self.do_randomize = 1
        self.btn_clear = MTButton(label='Clear Fridge')
        self.btn_clear.push_handlers(on_press=self.clear)
        self.btn_more = MTButton(label='More letters')
        self.btn_more.push_handlers(on_press=self.createletters)
        self.btn_boum = MTButton(label='Boum !')
        self.btn_boum.push_handlers(on_press=self.randomize)
        self.buttons = MTBoxLayout()
        self.buttons.add_widget(self.btn_clear)
        self.buttons.add_widget(self.btn_more)
        self.buttons.add_widget(self.btn_boum)
        self.add_widget(self.buttons)
        self.createletters()

    def createletters(self, *largs):
        w = self.get_parent_window()
        for c in xrange(65, 91): # A-Z
            count = 1
            if chr(c) in 'AEUIO':
                count = 4
            for i in xrange(0, count):
                color = map(lambda x: x/255., (randint(100,255), randint(100,255), randint(100,255), 255))
                l = FridgeLetterAtomic(letter=chr(c), color=color)
                if w:
                    l.pos = randint(0, w.width), randint(0, w.height)
                self.add_widget(l)

    def clear(self, *largs):
        self.children.clear()
        self.add_widget(self.buttons)
        self.createletters()

    def randomize(self, *largs):
        w = self.get_parent_window()
        for letter in self.children:
            if letter == self.buttons:
                continue
            letter.pos = randint(0, w.width), randint(0, w.height)

    def draw(self):
        if self.do_randomize:
            self.randomize();
            self.do_randomize = 0

def pymt_plugin_activate(w, ctx):
    fl = FridgeLetter()
    w.add_widget(fl)

def pymt_plugin_deactivate(w, ctx):
    pass

if __name__ == '__main__':
    w = MTWindow()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
