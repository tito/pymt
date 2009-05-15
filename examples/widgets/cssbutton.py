from pymt import *

additional_css = '''
.simple {
	draw-alpha-background: 1;
	draw-border: 1;
	draw-slider-alpha-background: 1;
	draw-slider-border: 1;
	draw-text-shadow: 1;
}

.colored {
	bg-color: #ff5c00;
	border-radius: 20;
	border-radius-precision: .1;
	font-size: 16;
	slider-border-radius-precision: .1;
	slider-border-radius: 20;
}

boundaryslider.colored,
xyslider.colored,
slider.colored {
	bg-color: #222222;
}
'''

css_add_sheet(additional_css)

m = MTWindow()

h = MTBoxLayout(padding=20, spacing=20)

v = MTBoxLayout(orientation='vertical', padding=20, spacing=20)
v.add_widget(MTButton(label='Coucou'))
v.add_widget(MTButton(label='Coucou', cls='simple'))
v.add_widget(MTButton(label='Coucou', cls=('simple', 'colored')))
h.add_widget(v)
v2 = MTBoxLayout(orientation='vertical', padding=20, spacing=20)
v2.add_widget(MTSlider(orientation='horizontal', value=50))
v2.add_widget(MTSlider(cls=('simple', 'colored'), orientation='horizontal', value=50))
v2.add_widget(MTBoundarySlider(orientation='horizontal', value=50))
v2.add_widget(MTBoundarySlider(cls=('simple', 'colored'), orientation='horizontal', value=50))
v2.add_widget(MTXYSlider(cls=('simple', 'colored')))
h.add_widget(v2)

m.add_widget(h)
runTouchApp()
