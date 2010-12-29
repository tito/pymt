# Text area (multiline text input)
from pymt import *

text = '''Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin cursus bibendum blandit. Morbi semper elit eu urna sagittis id sagittis lorem viverra. Duis ac nulla nisl. Aliquam erat volutpat. Morbi sit amet nunc mi. Ut id lectus sed ipsum suscipit tincidunt vitae in leo. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Praesent consectetur elit ac nunc mattis commodo. Sed pharetra tellus vel nibh sollicitudin tincidunt. Integer sed felis faucibus sapien dictum imperdiet eget quis ipsum. Nunc ut quam justo, sit amet egestas lacus.

Donec et sem in libero luctus viverra. Phasellus nec libero diam, ac ullamcorper arcu. Maecenas vitae mi diam. Pellentesque imperdiet mauris non ipsum hendrerit bibendum. Aliquam erat volutpat. Nulla vel hendrerit risus.'''

wid = MTTextArea(size=(500, 500), padding=10, label=text, font_size=10)
wid.center = getWindow().center

@wid.event
def on_text_validate():
    print 'Text have been validated:', wid.value

@wid.event
def on_text_change(text):
    print 'Text have been changed (not validated):', text

runTouchApp(wid)

