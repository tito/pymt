IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Explosions in the Sky'
PLUGIN_AUTHOR = 'Riley Dutton and Sharath Patali'
PLUGIN_EMAIL = 'riley@newspringmedia.com and sharath.patali@gmail.com'
PLUGIN_DESCRIPTION = 'A fun explosions game, with modes for both whack a mole and chain reaction fun!'

from pymt import *
from pyglet.media import *
from pyglet.gl import *
import random
import rabbyt.collisions

pyglet.resource.path=['../bloop/music']
pyglet.resource.reindex()

def showfps(arg):
    print "FPS:", pyglet.clock.get_fps()

class PlayArea(MTWidget):
    def __init__(self, pos=(0,0), size=(500,400), scale = 1.0, **kargs):
        MTWidget.__init__(self, pos=pos, size=size)
        self.num_bloops = 1
        self.bloop_points = 1
        self.bonus_points = 0
        self.bonus_points_snapshot = 0
        self.required_points = 2
        self.levelended = False
        self.time_left = 80
        
        self.score = ScoreZone(self)
        self.bonusalert = BonusText(self)
        self.notifications = NotificationText(self)
        
        self.add_widget(self.bonusalert)
        self.add_widget(self.score)
        self.add_widget(self.notifications)
        
        self.exploding = False
        self.collisionobjects = [] #Keep track of our objects that can be collided.
        self.blooplength = 8.0 #Set this high for a chain-reaction game, low for the original Bloop experience!
        self.level = 1
        self.prepLevel(level=self.level)

    def timerTick(self, dt):
        #Ticks our timer.
        self.time_left = self.time_left - 1
        if self.time_left < 1:
            self.endLevel()
        
    def prepLevel(self, dt=0, level=0):
        self.score.showing = False
        self.notifications.new_notification(0, text="Level " + str(level))
        pyglet.clock.schedule_once(self.notifications.new_notification, 3.0, text="Get ready!")
        pyglet.clock.schedule_once(self.startLevel, 6.0, level=level)
    def startLevel(self, dt=0, level=0):
        
        self.bloop_points = 1
        self.num_bloops = 1
        self.bonus_points = 0
        self.bonus_points_snapshot = 0
        self.exploding = False
        self.collisionobjects = []
        self.level = level

        if(level == 1):
            self.blooplength = 8.0
            self.bloop_freq = 0.5
            self.required_points = 200
            self.timelimit = 90
        elif(level == 2):
            self.blooplength = 6.0
            self.bloop_freq = 0.6
            self.required_points = 250
            self.timelimit = 90
        elif(level == 3):
            self.blooplength = 5.0
            self.bloop_freq = 0.6
            self.required_points = 300
            self.timelimit = 120

        self.levelended = False
        self.time_left = self.timelimit
        self.score.showing = True
        #self.notifications.new_notification(0, text="EXPLODE")
        pyglet.clock.schedule_interval(self.timerTick, 1)
        pyglet.clock.schedule_interval(self.generateBloop, self.bloop_freq)

    def endLevel(self):
        if not self.levelended:
            print("Ending level!")
            pyglet.clock.unschedule(self.generateBloop)
            pyglet.clock.unschedule(self.timerTick)
            for obj in self.collisionobjects:
                self.remove_widget(obj)
            if((self.bloop_points + self.bonus_points) >= self.required_points):
                self.notifications.new_notification(0, text="Level Complete", color="green", speed=5.0)
            else:
                self.notifications.new_notification(0, text="Level Failed", color="red", speed=5.0)
                self.level = self.level - 1 #Repeat the level
    
            pyglet.clock.schedule_once(self.prepLevel, 5.0, level=self.level+1)
            self.levelended = True
        
        
    def generateBloop(self,dt):
        self.num_bloops = self.num_bloops + 1
        self.redpt = random.uniform(0, 1)
        self.greenpt = random.uniform(0, 1)
        self.bluept = random.uniform(0, 1)
        self.newx = int(random.uniform(100, w.width-100))
        self.newy = int(random.uniform(100, w.height-100))
        self.b = bloop(self,music_file=random.choice('ABCDEFG')+str(random.randint(1, 3))+".mp3",score_text=self.score,pos=(self.newx,self.newy),color=(self.redpt,self.greenpt,self.bluept,1), expiretime = self.blooplength)
        self.add_widget(self.b)
        self.collisionobjects.append(self.b)

    def show_num_bloops(self):
        return str(self.num_bloops)
    
    def show_bloop_points(self):
        return str(self.bloop_points)
    def show_bonus_points(self):
        return str(self.bonus_points)
    def show_total_points(self):
        return str(self.bloop_points + self.bonus_points)
    def show_needed_points(self):
        return str(self.required_points - self.bloop_points - self.bonus_points)
    def show_required_points(self):
        return str(self.required_points)
    def show_time_left(self):
        self.min_left = self.time_left / 60
        self.sec_left = self.time_left - (self.min_left * 60)
        if(self.sec_left < 10):
            self.sec_left_str = "0" + str(self.sec_left)
        else:
            self.sec_left_str = str(self.sec_left)
        return str(self.min_left) + ":" + str(self.sec_left_str)

    def draw(self):
        
        #Check for collisions!
        chainactive = False
        bonus = 0
        if self.exploding:
            for collisions in rabbyt.collisions.rdc(self.collisionobjects):
                #Check to make sure at least one of these is already exploding (chain reaction!)
                chainreaction = False
                for obj in collisions:
                    if obj.exploded == True:
                        chainreaction = True
                if chainreaction:
                    for collision in collisions:
                       #print collision
                        if collision.exploded == False:
                           bonus = bonus + 1 #Bonus for chaining together multiple explosions at once.
                           self.bonus_x = collision.x
                           self.bonus_y = collision.y
                           collision.explode()
                        chainactive = True #Even if hte object is already exploded, if there are any collisions still ocurring, we keep the chain active.
                    self.bonus_points = self.bonus_points + bonus
            if not chainactive:
                if self.bonus_points - self.bonus_points_snapshot > 0:
                    self.bonusalert.new_bonus((self.bonus_points - self.bonus_points_snapshot) + 1, self.bonus_x, self.bonus_y)
                self.bonus_points_snapshot = self.bonus_points
                self.exploding = False
            

    def on_touch_down(self, touches, touchID, x,y):
        if self.collide_point(x,y):
            #Find any points that are directly underneath this point.
            for obj in self.collisionobjects:
                if obj.collide_point(x, y):
                    obj.explode()
                    self.exploding = True
            
        
class bloop(MTButton):
    def __init__(self,parent=None,music_file=None,score_text=None,pos=(50,50), size=(100,100), scale = 1.0, color=(0.2,0.2,0.2,0.8), expiretime = 2.0, **kargs):
        MTButton.__init__(self, pos=pos, size=size, label="test")
        self.parent = parent
        self.music_file = music_file
        self.music = pyglet.resource.media(self.music_file, streaming=False)
        self.radius = int(self.width/2)
        self.alpha = 0.00
        self.red = color[0]
        self.green = color[1]
        self.blue = color[2]
        self.score_text = score_text
        self.bounding_radius = 0
        self.bounding_radius_squared = 0
        self.exploded = False
        self.expiretime = expiretime
        
        self.highlightred = self.red * 1.25
        if(self.highlightred > 1):
            self.highlightred = 1

        self.highlightblue = self.blue * 1.25
        if(self.highlightblue > 1):
            self.highlightblue = 1

        self.highlightgreen = self.green * 1.25
        if(self.highlightgreen > 1):
            self.highlightgreen = 1
        
        anim = self.add_animation('fadein','alpha', 1.00, 1.0/60, 0.5)
        self.start_animations('fadein')
        self.showing = True
        self.highlight = False
        
        pyglet.clock.schedule_once(self.BloopHide, self.expiretime)
        
        anim = self.add_animation('fadeout','radius', self.width+10, 1.0/60, 1.0)
        anim = self.add_animation('fadeout','alpha', 0.00, 1.0/60, 0.5)
        
    def explode(self):
        self.parent.bloop_points = self.parent.bloop_points+1
        self.music.play()
        self.highlight = True
        self.red = self.highlightred
        self.green = self.highlightgreen
        self.blue = self.highlightblue            
        self.showing = False
        self.exploded = True
        self.start_animations('fadeout')

    def update(self):
        #We need these two values for rabbyt's collision detection functions.
        self.bounding_radius = self.radius
        self.bounding_radius_squared = int(self.radius) ** 2
        #print(self, self.x, self.y, self.bounding_radius, self.bounding_radius_squared)
            
    def draw(self):
        self.update()
        glPushMatrix()
        enable_blending()
        if self.highlight:
            self.highlightalpha = self.alpha * 1.25
            if(self.highlightalpha > 1):
               self.highlightalpha = 1
            glColor4f(self.highlightred, self.highlightgreen, self.highlightblue, self.highlightalpha)
            drawCircle(pos=(self.x + self.width/2,self.y + self.height/2),radius=(self.radius*1.25))

        glColor4f(self.red,self.green,self.blue,self.alpha)
        drawCircle(pos=(self.x + self.width/2,self.y + self.height/2),radius=self.radius)
        glPopMatrix()
        
    def BloopHide(self,dt):
        self.start_animations('fadeout')
        self.showing = False
               
    def on_animation_complete(self, anim):
        if self.showing == False:
            self.parent.remove_widget(self)
            if self in self.parent.collisionobjects:
                self.parent.collisionobjects.remove(self)

class BonusText(MTWidget):
    def __init__(self, parent, size=(200, 100)):
        MTWidget.__init__(self, pos=(0, 0), size=size)
        self.parent = parent
        self.expiretime = 2.0
        self.alpha = 0.00
        self.text = ""
        self.x = 0
        self.y = 0
        self.text_scale = 0.3
        self.text_red = 100
        
        anim = self.add_animation('grow', 'text_scale', 1.5, 1.0/30, 0.5)
        anim = self.add_animation('appear', 'alpha', 0.00, 1.0/30, 2.0)

    def draw(self):
        #glColor4f(1,0,0,1)
        if(self.alpha > 0):
            #Attempt to adjust for scaling, and also keep the bonus text within the screen boundries..
            self.adjx = (self.x - (self.text_scale * w.width * 0.05))
            self.adjy = (self.y - (self.text_scale * w.height * 0.20))
            drawLabel(self.text, (self.adjx, self.adjy), False, int(self.alpha*100), self.text_scale,red=self.text_red, green=0, blue=0)

    def new_bonus(self, text, x, y):
        self.text = str(text)
        self.x = x
        self.y = y
        self.alpha = 1.00
        self.text_red = int(25 * text) #The bigger teh bonus, the brighter the text...?
        if(self.text_red < 150):
            self.text_red = 150
        if(self.text_red > 255):
            self.text_red = 255
        #print self.text_red
        self.text_scale = 0.3
        self.start_animations('appear')
        self.start_animations('grow')

class NotificationText(MTWidget):
    def __init__(self, parent, size=(200, 100)):
        MTWidget.__init__(self, pos=(0, 0), size=size)
        self.parent = parent
        self.alpha = 0.00
        self.red = 0
        self.green = 0
        self.blue = 0
        self.text = ""
        self.x = 100
        self.y = w.height/2
        self.text_scale = 0.3
        
        #anim = self.add_animation('grow', 'text_scale', 2.0, 1.0/30, 3.0)
        #anim = self.add_animation('appear', 'alpha', 0.00, 1.0/30, 3.0)

    def draw(self):
        #glColor4f(1,0,0,1)
        if(self.alpha > 0):
            #Attempt to adjust for scaling, and also keep the bonus text within the screen boundries..
            self.adjx = (self.x - (self.text_scale * w.width * 0.05))
            self.adjy = (self.y - (self.text_scale * w.height * 0.20))
            drawLabel(self.text, (self.adjx, self.adjy), False, int(self.alpha*100), self.text_scale, red=self.red, green=self.green, blue=self.blue)

    def new_notification(self, dt, text, color="black", speed=3.0):
        self.remove_animation('appear')
        self.remove_animation('grow')
        self.add_animation('appear', 'alpha', 0.00, 1.0/30, speed)
        self.add_animation('grow', 'text_scale', 2.0, 1.0/30, speed)
        self.text = str(text)
        if color == "black":
            self.red = 255
            self.green = 255
            self.blue = 255
        elif color == "red":
            self.red= 255
            self.green = 0
            self.blue = 0
        elif color == "green":
            self.red = 0
            self.green = 255
            self.blue = 0
        
        self.alpha = 1.00
        self.text_scale = 0.3
        self.start_animations('appear')
        self.start_animations('grow')


class ScoreZone(MTWidget):
    def __init__(self, parent = None, pos=(0,0), size=(200,100), scale = 1.0, **kargs):
        MTWidget.__init__(self, pos=pos, size=size)
        self.label = "1/1"
        self.parent = parent
        self.showing = False

    def draw(self):
        self.updateScore()
        glColor4f(1,0,0,1)
        if self.showing:
            drawLabel(self.label,(0,w.height-80),False)

    def updateScore(self):
        self.label = self.parent.show_bloop_points() + " + " + self.parent.show_bonus_points() + " = " + self.parent.show_total_points() +"/"+self.parent.show_required_points()+" in "+self.parent.show_time_left()
def drawLabel(text, pos=(0,0),center=True,alpha = 75,scale=0.3,red=255,green=255,blue=255):
    _standard_label = Label(text='standard Label', font_size=200,bold=True, color=(red,green,blue,alpha))
    _standard_label.anchor_x = 'left'
    _standard_label.anchor_y = 'bottom'
    _standard_label.x = 0
    _standard_label.y = 0
    _standard_label.text = text
    glPushMatrix()
    glTranslated(pos[0], pos[1], 0.0)
    glScaled(scale,scale,1)
    _standard_label.draw()
    glPopMatrix()
    
def pymt_plugin_activate(root, ctx):
    ctx.PA = PlayArea(size=(root.width, root.height))
    pyglet.clock.schedule_interval(showfps, 5.0)
    root.add_widget(ctx.PA)
    

def pymt_plugin_deactivate(root, ctx):
   root.remove_widget(ctx.PA)
    
if __name__ == '__main__':
    w = MTWindow(color=(0,0,0,1), fullscreen=True)
    #print gl_info.get_version()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
