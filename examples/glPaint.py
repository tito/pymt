from pymt import *
from pyglet import *
from pyglet.gl import *



class PaintWindow(TouchWindow):
    def __init__(self):
        config = Config(sample_buffers=1, samples=4, depth_size=16, double_buffer=True, vsync=0)
        TouchWindow.__init__(self, config)
	self.set_fullscreen()
        self.touch_positions = {}
	self.color_picker = ColorPicker(height=self.height)
        
    def on_draw(self):  	
	for p in self.touch_positions:
		x,y = self.touch_positions[p][0][0],self.touch_positions[p][0][1]
		for pos in self.touch_positions[p][1:]:
			drawLine( [(x, y), (pos[0],pos[1])] ,pos[2])
			x, y = pos[0],pos[1]

	self.color_picker.draw()
            
    def on_touch_down(self, touches, touchID, x, y):
		col = self.color_picker.getColorForPoint(x,y)
        self.touch_positions[touchID] = [(x,y, col)]

        
    def on_touch_move(self, touches, touchID, x, y):
		col = self.color_picker.getColorForPoint(x,y)
        self.touch_positions[touchID].append((x,y,col))

        
    def on_touch_up(self, touches, touchID, x, y):
        del self.touch_positions[touchID]
        

    
    
w = PaintWindow()
runTouchApp()
