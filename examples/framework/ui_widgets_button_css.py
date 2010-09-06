from pymt import *

# Create a CSS with 2 rules
additional_css = '''
.simple {
	draw-alpha-background: 0;
	draw-border: 0;
	draw-text-shadow: 1;
}

.colored {
	bg-color: rgb(68, 170, 0);
	border-radius: 20;
	border-radius-precision: .1;
	font-size: 16;
}
'''

# Add the CSS into PyMT
css_add_sheet(additional_css)

# Create different button, with one or 2 rules at the same time
v = MTBoxLayout(orientation='vertical', padding=20, spacing=20)
v.add_widget(MTButton(label='Coucou'))
v.add_widget(MTButton(label='Coucou', cls='simple'))
v.add_widget(MTButton(label='Coucou', cls='colored'))
v.add_widget(MTButton(label='Coucou', cls=('simple', 'colored')))

runTouchApp(v)
