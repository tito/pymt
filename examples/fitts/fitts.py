from pymt import *

image_file = pyglet.image.load('fitts.png')
image_sprite = pyglet.sprite.Sprite(image_file, x=50, y=50)
image_sprite.scale=0.1

image_file = pyglet.image.load('fitts_target.png')
image_target = pyglet.sprite.Sprite(image_file, x=200, y=400)
image_target.scale=0.1




class FittsWindow(TouchWindow):
	def __init__(self):
		config = Config(sample_buffers=1, samples=4, depth_size=16, double_buffer=True, vsync=0)
		TouchWindow.__init__(self, config)
		#self.set_fullscreen()
		self.mode = 'selecting'

		
	def on_draw(self):		
		self.clear()
		image_target.draw()
		image_sprite.draw()


	def on_touch_down(self, touches, touchID, x, y):
		if self.mode == 'selecting':
			print x,y, image_sprite.x, image_sprite.y, image_sprite.x + image_sprite.width
			if  ( x > image_sprite.x  and x < image_sprite.x + image_sprite.width
			  and y > image_sprite.y  and y < image_sprite.y + image_sprite.height ):
				self.mode = 'dragging'

		
	def on_touch_move(self, touches, touchID, x, y):
		if self.mode == 'dragging':
			image_sprite.x = x - image_sprite.width/2
			image_sprite.y = y - image_sprite.height/2
			if  ( x > image_sprite.x  and x < image_sprite.x + image_sprite.width
			  and y > image_sprite.y  and y < image_sprite.y + image_sprite.height ):
				self.mode = 'done'
				'start timer'

	def on_touch_up(self, touches, touchID, x, y):
		if self.mode == 'selecting':
			pass #record selection error
		if self.mode == 'dragging':
			self.mode = 'selecting'
			pass #record drag error
		pass
		

	
	
w = FittsWindow()
runTouchApp()
