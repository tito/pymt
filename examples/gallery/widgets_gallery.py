from pymt import *

# Decoration to autodeclare screens
l_screens = []
def registerscreen(title):
    def wrap(f):
        global l_screens
        l_screens.append((title, f))
        return f
    return wrap

@registerscreen('Buttons')
def screen_button(w):
    btn = MTButton(label='Normal')
    w.add_widget(btn)

    btn = MTButton(label='Down')
    btn.state = 'down'
    w.add_widget(btn)

    btn = MTToggleButton(label='Toggle')
    w.add_widget(btn)

    btn = MTToggleButton(label='Toggle')
    btn.state = 'down'
    w.add_widget(btn)


@registerscreen('Buttons Matrix')
def screen_buttonmatrix(w):
    bmx = MTButtonMatrix(matrix_size=(10,10), size=(500, 500))
    w.add_widget(bmx)


@registerscreen('File Browser')
def screen_filebrowser(w):
    fb = MTFileBrowser()
    w.add_widget(fb)


@registerscreen('Color Picker')
def screen_colorpicker(w):
    cp = MTColorPicker()
    w.add_widget(cp)


@registerscreen('Sliders')
def screen_slider(w):
    sl = MTSlider(orientation='horizontal', value=1, size=(100, 30))
    w.add_widget(sl)

    sl = MTSlider(orientation='horizontal', value=50, size=(100, 30))
    w.add_widget(sl)

    sl = MTSlider(orientation='horizontal', value=100, size=(100, 30))
    w.add_widget(sl)

    sl = MTSlider(orientation='horizontal', value=50, value_show=True, size=(100, 30))
    w.add_widget(sl)

    sl = MTBoundarySlider(orientation='horizontal', value_min=25, value_max=75, size=(100, 30))
    w.add_widget(sl)


@registerscreen('Sliders - Multi')
def screen_multisliders(w):
    sl = MTMultiSlider()
    w.add_widget(sl)


@registerscreen('Sliders - XY')
def screen_xyslider(w):
    sl = MTXYSlider(size=(300, 300))
    w.add_widget(sl)


@registerscreen('Slider - Circular')
def screen_circularslider(w):
    sl = MTCircularSlider()
    w.add_widget(sl)


@registerscreen('Slider - Vector')
def screen_circularslider(w):
    sl = MTVectorSlider()
    w.add_widget(sl)


@registerscreen('Modal Window')
def screen_modalwindow(w):
    m = MTModalWindow()
    def close_modal(*largs):
        w.remove_widget(m)
    anchor = MTAnchorLayout()
    m.connect('on_resize', anchor, 'size')
    btn = MTButton(label='Close')
    btn.connect('on_press', close_modal)
    anchor.add_widget(btn)
    m.add_widget(anchor)
    w.add_widget(m)


@registerscreen('Modal Popup')
def screen_modalpopup(w):
    m = MTModalPopup(
        content='Here is the modal popup, with a very very long long line.',
        size=(300, 300))
    w.add_widget(m)


@registerscreen('Speech Bubble')
def screen_speechbubble(w):
    m = MTSpeechBubble(label='Hello world')
    w.add_widget(m)


@registerscreen('Kinetic List')
def screen_kineticlist(w):
    m = MTKineticList(size=(210, 200))
    for x in xrange(20):
        m.add_widget(MTKineticItem(label=str(x)))
    w.add_widget(m)

    m = MTKineticList(size=(210, 200), searchable=False, deletable=False)
    for x in xrange(20):
        m.add_widget(MTKineticItem(label=str(x)))
    w.add_widget(m)

    m = MTKineticList(size=(230, 200), searchable=False, deletable=False,
                      title=None, w_limit=2)
    for x in xrange(20):
        m.add_widget(MTKineticItem(label=str(x)))
    w.add_widget(m)


@registerscreen('Tabs')
def screen_tabs(w):
    tabs = MTTabs()
    tabs.add_widget(MTButton(label="Hello"), tab='Tab1')
    tabs.add_widget(MTButton(label="World"), tab='Tab2')
    tabs.select('Tab2')
    w.add_widget(tabs)

@registerscreen('Side Panel')
def screen_sidepanel(w):
    w = getWindow()

    panel = MTSidePanel(side='left', size=(500, 100))
    for x in xrange(5):
        panel.add_widget(MTButton(label=str(x)))
    w.add_widget(panel)

    panel = MTSidePanel(side='right', size=(500, 100))
    for x in xrange(5):
        panel.add_widget(MTButton(label=str(x)))
    w.add_widget(panel)

    panel = MTSidePanel(side='top', size=(500, 100))
    for x in xrange(5):
        panel.add_widget(MTButton(label=str(x)))
    w.add_widget(panel)

    panel = MTSidePanel(side='bottom', size=(500, 100))
    for x in xrange(5):
        panel.add_widget(MTButton(label=str(x)))
    w.add_widget(panel)

@registerscreen('Text Input')
def screen_textinput(w):
    txt = MTTextInput()
    w.add_widget(txt)

    txt = MTTextInput(size=(300, 40), padding_x=10)
    txt.value = 'Type your text here'
    w.add_widget(txt)


@registerscreen('VKeyboard')
def screen_vkeyboard(w):
    k = MTVKeyboard()
    getWindow().add_widget(k)

@registerscreen('Spell VKeyboard')
def screen_vkeyboard(w):
    k = MTSpellVKeyboard()
    getWindow().add_widget(k)



if __name__ == '__main__':
    lbox = MTBoxLayout(orientation='vertical', spacing=5, padding=5)

    current = None
    def select_screen(callback, *largs):
        w = getWindow()
        w.children = []
        w.add_widget(lbox)

        anchor = MTAnchorLayout(pos=(150, 0))
        grid = MTGridLayout(cols=3, spacing=30)
        anchor.add_widget(grid)
        w.add_widget(anchor)
        anchor.size = w.width - 150, w.height
        callback(grid)

    for name, callback in l_screens:
        btn = MTButton(label=name, size=(140, 30))
        lbox.add_widget(btn)
        btn.connect('on_press', curry(select_screen, callback))

    getWindow().add_widget(lbox)
    runTouchApp()
