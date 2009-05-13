from pymt import *

additional_css = '''
button.btnA {
	draw-text-shadow: 1;
	draw-alpha-background: 1;
	bg-color: #ff5c00;
	draw-border: 1;
	border-radius: 20;
	font-size: 16;
	border-precision: .1;
}
'''

css_add_sheet(additional_css)

m = MTWindow()
m.add_widget(MTButton(label='Coucou', pos=(100, 100)))
m.add_widget(MTButton(label='Coucou', cls='btnA', pos=(100, 210)))
#m.add_widget(MTButton(label='Coucou', pos=(100, 320)))
runTouchApp()
