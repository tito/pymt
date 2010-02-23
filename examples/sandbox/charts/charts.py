from __future__ import with_statement
from pymt import *
from pymt.graphxcss import *



css_add_sheet('''
.simple {
	draw-alpha-background: 1;
	draw-border: 1;
}

.colored {
	bg-color: #555555;
	border-radius: 5;
	border-radius-precision: .1;
	font-size: 16;
	axis-width: 2;
	axis-color: #cccccc;
	padding: 5;
}

''')







class MTChart(MTWidget):

   def __init__(self, **kwargs):
      kwargs.setdefault('data',{})
      self.data = kwargs['data']
      super(MTChart, self).__init__(**kwargs)
      self.display_list = GlDisplayList()
      self.needs_redraw = True


   def on_draw(self):
      if self.needs_redraw:
         with self.display_list:
            self.draw()
            self.needs_redraw = False

      if self.visible:
         self.display_list.draw()



   def add_data(self, label, data):
      if self.data.has_key(label):
         self.data[label].extend(data)
      else:
         self.data[label] = data

      self.needs_redraw = True






class MTLineChart(MTChart):
   def draw(self):
      #draw background
      set_color(*self.style['bg-color'])
      drawCSSRectangle(pos=self.pos, size=self.size, style=self.style)

      #draw axis
      p = self.style['padding']
      #set_color(*self.style['axis-color'])
      set_color(1,1,1)
      l,r =  self.x+p, self.x+self.width-p
      b,t =  self.y+p, self.y+self.height-p
      drawLine((l,t,l,b,r,b),int(self.style['axis-width']))

      #draw data lines
      for line_name in self.data:
         lx,ly = (l,b)
         max_x, max_y = max(self.data[line_name].keys()), max(self.data[line_name].values())
         print line_name
         for i in self.data[line_name]:
            x = float(i)/max_x * (self.width-2*p) + p
            y = float(self.data[line_name][i])/max_y * (self.height-2*p) + p
            drawLine((lx,ly,x,y),2)
            lx,ly = x,y




#some tests
if __name__ == "__main__":

   data = {'line 1': {0:10, 1:15, 2:20, 3:13, 4:17, 5:22 }}
   c = MTLineChart(data=data, cls=('simple', 'colored'))

   w = MTWindow()
   t = MTScatterWidget()
   t.add_widget(c)
   w.add_widget(t)
   runTouchApp()
