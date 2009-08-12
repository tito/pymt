from pymt import *

c = MTWidget()

for i in range (20):
        img_src = 'bilder/testpic'+str(i+1)+'.jpg'
        x , y =  i/5*300+150, i%5*200+100
        b = MTImageButton(filename = img_src, scale=0.16, pos = (x,y))
        b.status = 'not zoomed'

        anim = b.add_animation('zoom','x', 400, 1.0/60, .2)
        anim = b.add_animation('zoom','y', 300, 1.0/60, .2)
        anim = b.add_animation('zoom','scale', 1.0, 1.0/60, .2)

        anim = b.add_animation('shrink','x', x, 1.0/60, .2)
        anim = b.add_animation('shrink','y', y, 1.0/60, .2)
        anim = b.add_animation('shrink','scale', 0.24, 1.0/60, .2)

        def click(w, touch):
            if w.status == 'zoomed':
                w.start_animations('shrink')
                w.status = 'not_zoomed'
            else:
                w.bring_to_front()
                w.start_animations('zoom')
                w.status = 'zoomed'

        b.push_handlers(on_release=curry(click,b)  )
        c.add_widget(b)

w = MTWindow()
w.add_widget(c)
runTouchApp()
