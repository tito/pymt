from pymt import *

w = MTWindow()
scat =  MTScatterWidget(pos=(300,300), size=(100,50))
sq = MTRectangularWidget(pos=(10,10),size=(10,10))
scat.add_widget(sq)
w.add_widget(scat)

#anim = Animation(duration=1.0, rotation=360) & Animation(duration=1.0, center=(w.center[0],400))
#anim = Repeat(Animation(duration=1.0, rotation=360) & Animation(duration=1.0, center=(w.center[0],400)), times=5)
#anim = Repeat(Animation(duration=1.0, rotation=360), times=5)
anim = Animation(duration=0.5, center=(scat.center[0]+200,200))  +  Animation(duration=1.0, center=(w.center[0],400))

@anim.event
def on_start(*largs):
    print "started"

@anim.event
def on_complete(*largs):
    print "completed"

@anim.event
def on_repeat(widget, count):
    print count

@scat.event
def on_animation_complete(*largs):
    print "on_completed: ",scat.rotation
    
but  = MTButton(label="lick")
w.add_widget(but)
@but.event
def on_press(*largs):
    scat.do(anim)
runTouchApp()