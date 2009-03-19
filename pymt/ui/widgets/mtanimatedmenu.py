from __future__ import with_statement

__all__ = [ 'MTMenuItem', 'MTAnimatedMenu' ]

import pyglet
from pyglet.gl import *
from pymt import *
from random import random
import datetime

        
def mix(color1, color2, blend):
    return [c1 * blend + c2 *(1.0 - blend) for c1, c2 in zip (color1, color2)]

class MTMenuItem:
    def __init__(self, name, handler):
        self.name = name
        self.handler = handler
        self.isInMotion = False
        self.isHiding = False
        self.motionStartTime = None
        self.parent = None
        self.direction = (0,-1)
        self.animparent = None      # the top level Animated menu instance to register our cells for dispatch draw
        
        self.pos = ()
        self.size = ()
        
        self.isFlashing = False
        self.flashStartTime = None
        self.hideStartTime = None
        self.isExpanded = False
        self.label = pyglet.text.Label(self.name,
                          font_name='Arial',
                          font_size=14,
                          anchor_x='center', anchor_y='center')
        self.children =[]
        
    def add (self, newitem):
        '''Add a child menu item to the current menu item'''
        newitem.parent = self
        newitem.animparent = self.animparent
        self.children.append (newitem)
        
    def drawKnown(self):
        self.draw (self.pos, self.size)
        
    def draw(self, p, s, blendoverride = 1):
        '''Renders the menu in its current state'''        
        glPushAttrib (GL_ENABLE_BIT)
        glEnable(GL_BLEND)
        glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        bgcolor_normal = (1.0, 1.0, 1.0, 0.2 * blendoverride)
        textcolor_normal = (1.0, 1.0, 1.0, 1.0 * blendoverride)
        bordercolor_normal = (1.0, 1.0, 1.0, 1.0 * blendoverride)

        bgcolor_selected = (1.0, 1.0, 1.0, 0.6 * blendoverride)
        textcolor_selected = (1.0, 1.0, 1.0, 1.0 * blendoverride)
        bordercolor_selected = (1.0, 1.0, 1.0, 1.0 * blendoverride)

        
        flashduration = 200000 # microseconds
        animduration = 200000  # microseconds
        hidingduration = 200000 # microseconds
        
        bgcolor = bgcolor_normal
        textcolor = textcolor_normal
        bordercolor = bordercolor_normal
        
        if self.isFlashing:
            td = datetime.datetime.now () - self.flashStartTime
            if td.microseconds < flashduration:
                bo = td.microseconds / float(flashduration)
                bo = bo * bo * bo * bo
                if self.isExpanded:
                    bo = 1.0 - bo
                # blend colors to selected or the other way around
                bgcolor = mix (bgcolor_normal, bgcolor_selected, bo)
                textcolor = mix (textcolor_normal, textcolor_selected, bo)
                bordercolor = mix (bordercolor_normal, bordercolor_selected, bo)
            else:
                self.isFlashing = False
        
        if self.isExpanded and not self.isFlashing:
            bgcolor = bgcolor_selected
            textcolor = textcolor_selected
            bordercolor = bordercolor_selected
        
        if self.isInMotion:
            td = datetime.datetime.now () - self.motionStartTime
            if td.microseconds < animduration:
                bo = td.microseconds / float(animduration)
                bo = bo*bo*bo*bo
                if not self.isExpanded:
                    bo = 1.0 - bo
                    
                self.drawChildren(p, s, self.direction, bo)
            else:
                self.isInMotion = False
                # the menu has been expanded or collapsed, update the size and position info
                # of the subitems so that they know where they are when the time to hittest comes
                #
                bo = [0.0, 1.0][self.isExpanded]
                self.updateChildrenPositions(p, s, self.direction, bo)
            
        
        if self.isExpanded and not self.isInMotion:
            self.drawChildren(p, s, self.direction, blendoverride)
        
        if self.isHiding:
            td = datetime.datetime.now () - self.hideStartTime
            if td.microseconds < hidingduration:
                bo = td.microseconds / float(hidingduration)
                bo = 1.0 - bo*bo*bo*bo
                bgcolor = mix(bgcolor_selected, (bgcolor_selected[0], bgcolor_selected[1], bgcolor_selected[2], 0.0), bo)
                textcolor = mix(textcolor_selected, (textcolor_selected[0], textcolor_selected[1], textcolor_selected[2], 0.0), bo)
                bordercolor = mix(bordercolor_selected, (bordercolor_selected[0], bordercolor_selected[1], bordercolor_selected[2], 0.0), bo)
            else:
                self.isHiding = False
                self.animparent.removeDrawRequestor (self)
                self.triggerLaunch = True
                
                self.animparent.addTrigger (self)
                return # we don't want the cell drawn anymore
                
        # finally draw ourselves
        #
        set_color(*bgcolor)
        
        drawRoundedRectangle (pos=p, size=s)

        set_color(*bordercolor)
        drawRoundedRectangle (pos=p, size=s, linewidth=1, style=GL_LINE_LOOP)
        self.label.color = (int(textcolor[0] * 255.0), int(textcolor[1] * 255.0), 
                            int(textcolor[2] * 255.0), int(textcolor[3] * 255.0))
        self.label.x, self.label.y = p[0] + s[0] / 2, p[1] + s[1] / 2
        self.label.draw()
            
        glPopAttrib()
            
    def updateChildrenPositions(self, p, s, d, bo):
        for i,c in enumerate (self.children):
            pos = (p[0] + 10 * d[0] + (s[0] + 5) * (i + 1) * d[0] * bo, p[1] + 10 * d[1] + (s[1] + 5) * (i + 1) * d[1] * bo)
            c.pos = pos
            c.size = s
            if d == (0, -1):
                c.direction = (1, 0)
            else:
                c.direction = (0, -1) 
        
    def drawChildren(self, p, s, d, bo = 1):
        for i,c in enumerate (self.children):
            pos = (p[0] + 10 * d[0] + (s[0] + 5) * (i + 1) * d[0] * bo, p[1] + 10 * d[1] + (s[1] + 5) * (i + 1) * d[1] * bo)
            c.draw (pos, s, bo)

    def hittest (self, p):
        if p[0] > self.pos[0] and p[0] < self.pos [0] + self.size [0] and p[1] > self.pos[1] and p [1] < self.pos[1] + self.size [1]:
            return self;
        elif self.isExpanded:
            for c in self.children:
                r = c.hittest (p)
                if r:
                    return r
            return None
        return None
        
    def toggle(self):
        if self.parent:
            self.parent.checkHideActive(self)
                
        if self.children:
            self.isExpanded = not self.isExpanded
            self.isFlashing = True;
            self.isInMotion = True;
            self.flashStartTime = self.motionStartTime = datetime.datetime.now ()
        else:
            # no child options, this is the terminal
            self.isHiding = True
            self.hideStartTime = datetime.datetime.now()
            self.animparent.addDrawRequestor (self)
            self.dismissMenu ()
            
    def checkHideActive(self, o):
        for c in self.children:
            if c.isExpanded and c != o:
                c.isExpanded = not self.isExpanded
                
            
    def dismissMenu(self):
        if self.parent:
            self.parent.isExpanded = False
            self.parent.dismissMenu();
            
    def setAnimParent (self, parent):
        self.animparent = parent
        for c in self.children:
            c.setAnimParent (parent)
             
            
        
class MTAnimatedMenu:
    def __init__(self, menu, pos=(50,800), size=(200,50)):
        self.menu = self._parseMenu(menu)
        self.pos = pos
        self.size = size
        
        # set size and dimensions for the top level menu item
        self.menu.pos = pos
        self.menu.size = size
        self.menu.setAnimParent (self)
        self.regchildren = []
        self.triggeredChildren = []
        
    def _parseMenu(self, menu):
        if type(menu) == dict:   # top level menu item should always be a single item
            return self._getAsMenuItem(menu)[0]
        else:
            return menu
        
    def _getAsMenuItem (self, menu):
        mt = []
        for k, v in menu.items():
            if type(v) == dict:
                m = MTMenuItem (k, None)
                for nm in self._getAsMenuItem(v):
                    m.add (nm)
            else:
                m = MTMenuItem (k, v)
            mt.append (m)
        return mt
    
    def _performDispatches(self):
        for i, k in enumerate(self.triggeredChildren):
            c, count = k
            del self.triggeredChildren[i]
            if count:
                self.triggeredChildren.append ((c, count - 1))
            else:
                if c.handler:
                    c.handler ()
            
        
    def draw(self):
        '''Renders the menu in its current state'''
        self.menu.draw(self.pos, self.size)
        for c in self.regchildren:
            c.drawKnown ();
            
        self._performDispatches()
        
    def handle(self, pos):
        '''Handle a notification event, we need to be able to determine which item was tapped'''
        item = self.hittest (pos)
        if item:
            item.toggle()
        
    def hittest(self, pos):
        return self.menu.hittest(pos); 
    
    def addDrawRequestor(self,c):
        self.regchildren.append (c)
        
    def removeDrawRequestor(self,c):
        self.regchildren.remove(c)
        
    def addTrigger(self, c):
        # 2 frame before we call this handler, 
        # this is done to make sure that our menu is not visible when dispatch happens
        self.triggeredChildren.append ((c, 2))  
