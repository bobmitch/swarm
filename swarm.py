from psyco.classes import *
import math
import operator
import pyglet
pyglet.options['debug_gl'] = False	# TURN ON FOR DEBUGGIN GL!!!
import random
from pyglet.window import key
from pyglet.window import mouse
from pyglet.gl import *
from pyglet import clock
import copy

# GLOBALS
WIDTH = 800
HEIGHT = 500

# TOWER TYPES
SLOW_TOWER = 1
FAST_TOWER = 2

# DISPLAY LISTS
GRID_DL = 1
TOWER_BASE_DL = 5
TOWER_SLOW_DL = 10
TOWER_FAST_DL = 20
ENEMY_NORMAL_DL = 200


# WINDOW SETUP
window = pyglet.window.Window(WIDTH,HEIGHT,"sc",True)
window.set_vsync (False)
#window.set_fullscreen(True)
#window.set_exclusive_mouse()
#window.set_mouse_visible (False)

class aMouse:
	def __init__ (self):
		self.x=0
		self.y=0
		self.map_x=0
		self.map_y=0
		self.lmb_down = False
		self.lmb_up = False
		self.lmb_clicked = False

class aCell:
	def __init__ (self):
		self.entities = []
		self.passable=True
		
		# debug - random maze
		if random.random() > 0.9:
			self.passable=False

class aMap:
	def __init__ (self, x, y, game):
		# create 2d array of Cells
		self.cell = []
		self.width = x
		self.height = y
		for a in xrange(0,x):
			row=[]
			for b in xrange(0,y):
				row.append ( aCell() )
			self.cell.append ( row )
		self.create_display_list(game)
			
	def create_display_list (self, game):
		glNewList(1,GL_COMPILE)
		# GRID
		glColor4f (1,1,1,0.05)
		glLineWidth(1)
		glBegin (GL_LINES)
		for x in range (0,self.width+1):
			glVertex2f (x,0)
			glVertex2f (x,self.height)
		for y in range (0,self.height+1):
			glVertex2f (0,y)
			glVertex2f (self.width,y)
		glEnd()
		# WALLS
		glColor4f (1,1,1,1)
		glBegin (GL_QUADS)
		for x in range (0,self.width):
			for y in range (0,self.height):
				if self.cell[x][y].passable != True:
					glVertex2f (x,y)
					glVertex2f (x, y+1)
					glVertex2f (x+1, y+1)
					glVertex2f (x+1, y)
		glEnd()
		glEndList()
		
	def draw (self):
		glCallList(1)
		
	def draw_selection (self):
		glBegin (GL_QUADS)
		glVertex2f (0,0)
		glVertex2f (self.width,0)
		glVertex2f (self.width,self.height)
		glVertex2f (0,self.height)
		glEnd()
		

class slowTower:
	def __init__ (self, position):
		self.pos = position
		self.direction = 0
		self.active = True
		
	def update (self,dt):
		self.direction += 4
		
	def draw (self):
		glColor4f (0.2,1,0.2,1)
		glPushMatrix()
		glTranslatef (self.pos[0], self.pos[1], 0)
		glCallList (TOWER_BASE_DL)
		glRotatef (-self.direction, 0, 0, 1)
		glCallList (TOWER_SLOW_DL)
		glPopMatrix()
		glPopMatrix()
		

class normalEnemy:
	def __init__ (self):
		self.pos = [1,7]
		self.dir = 90
		self.speed = 2
		
	def draw (self):
		glPushMatrix()
		glTranslatef (self.pos[0], self.pos[1], 0)
		glCallList (ENEMY_NORMAL_DL)
		glPopMatrix()

	def update (self, tick):
		self.pos[0] = self.pos[0] + (self.speed * tick)
		
		
		
class aGame:
	def __init__ (self):
		self.map = None
		self.create_tower_display_lists()
		self.towers=[]
		self.enemies=[]
		self.camera_x = 0
		self.camera_y = 0
		self.camera_height = 0
		
	def create_tower_display_lists (self):
		# TOWER BASE 1
		glNewList(TOWER_BASE_DL, GL_COMPILE)
		glBegin (GL_LINE_LOOP)
		glVertex2f (-1,-1)
		glVertex2f (1,-1)
		glVertex2f (1,1)
		glVertex2f (-1,1)
		glEnd ()
		glEndList()
		
		# SLOW TOWER LVL 1
		glNewList(TOWER_SLOW_DL,GL_COMPILE)
		glLineWidth(1)
		# turret
		glBegin (GL_LINE_LOOP)
		glVertex2f (-0.3,-0.3)
		glVertex2f (-0.3, 0.3)
		glVertex2f (0.3, 0.3)
		glVertex2f (0.3, -0.3)
		glEnd()
		glBegin (GL_LINES)
		glVertex2f (0, 0)
		glVertex2f (0, 0.5)
		glEnd()
		glEndList()
		
		# NORMAL ENEMY 
		glNewList(ENEMY_NORMAL_DL, GL_COMPILE)
		glColor4f (1.0, 0.2, 0.2, 1)
		glBegin (GL_LINE_LOOP)
		glVertex2f (-0.2, -0.2)
		glVertex2f (0.2, -0.2)
		glVertex2f (0.2, 0.2)
		glVertex2f (-0.2, 0.2)
		glEnd ()
		glEndList()
	
	def create_level (self,x,y,game):
		self.recalc_camera(x,y)
		self.map = aMap(x,y,game)
		
	def recalc_camera (self,x,y):
		self.camera_height = -(max(x, y)) * 0.9
		self.camera_x = -(x/2.0)-8
		self.camera_y = -(y/2.0)

		
		
class aKeybstate:
	def __init__ (self):
		self.w= False
		self.s = False
		self.a = False
		self.d = False
		self.up = False
		self.down = False
		self.left = False
		self.right = False
		self.space = False
		self.shift = False
		self.tab = False
		self.t = False
keybstate = aKeybstate()	# GLOBAL keyboard state 





@window.event
def on_draw():

	window.clear()
	
	do_selection()
	
	# DRAW MAP PLUS ENTITIES
	glPushMatrix()
	glTranslatef ( game.camera_x, game.camera_y, game.camera_height )
	
	for enemy in game.enemies:
		enemy.draw()
	game.map.draw()
	
	for tower in game.towers:
		tower.draw()
		
	# END DRAW MAP PLUS ENTITIES
		
	glPopMatrix()

	
	
def key_handler ():
	if keybstate.w: 
		print "W pressed"
		keybstate.w=False
		blah = slowTower([1,1])
		game.towers.append ( blah )
		yadda = normalEnemy()
		game.enemies.append ( yadda )
	
	
@window.event
def on_key_press (symbol, modifiers):
	global keybstate
	if symbol == key.W:
		keybstate.w = True
	if symbol==key.S:
		keybstate.s = True
	if symbol == key.D:
		keybstate.d = True
	if symbol==key.A:
		keybstate.a = True
	if symbol==key.SPACE:
		keybstate.space = True
	if symbol==key.LEFT:
		keybstate.left = True
	if symbol==key.RIGHT:
		keybstate.right = True
	if symbol==key.UP:
		keybstate.up = True
	if symbol==key.LSHIFT:
		keybstate.shift = True
	if symbol==key.TAB:
		keybstate.tab = True
	if symbol==key.T:
		keybstate.t = True
	

@window.event
def on_key_release (symbol, modifiers):
	global keybstate
	if symbol == key.W:
		keybstate.w = False
	if symbol==key.S:
		keybstate.s = False
	if symbol == key.D:
		keybstate.d = False
	if symbol==key.A:
		keybstate.a = False
	if symbol==key.SPACE:
		keybstate.space = False
	if symbol==key.LEFT:
		keybstate.left = False
	if symbol==key.RIGHT:
		keybstate.right = False
	if symbol==key.UP:
		keybstate.up = False
	if symbol==key.LSHIFT:
		keybstate.shift = False
	if symbol==key.TAB:
		keybstate.tab = False
	if symbol==key.T:
		keybstate.t = False
		global TRACKING
		if TRACKING[0] or SELECTED==[]:
			TRACKING=[False,False]
		else:
			TRACKING=[True,SELECTED[0]]

			
@window.event
def on_mouse_motion (x,y,dx,dy):
	global mouse
	mouse.x = x
	mouse.y = y
		
@window.event
def on_resize(width, height):
    #Override the default on_resize handler to create a 3D projection

	glViewport(0, 0, width, height)
	glEnable (GL_LINE_SMOOTH)
	glMatrixMode(GL_PROJECTION)
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
	glEnable (GL_BLEND)
	glHint (GL_LINE_SMOOTH_HINT, GL_NICEST)
	glLineWidth(1)
	glLoadIdentity()
	gluPerspective(60., width / float(height), .1, 1000.)
	glMatrixMode(GL_MODELVIEW)
	return pyglet.event.EVENT_HANDLED

def do_selection():
	# set up selection buffer
	select_buffer = (GLuint * 1024)()	# make this bigger if necessary - should handle up to 512 selectable items
	glSelectBuffer (len(select_buffer), select_buffer)
	
	# enter selection mode and push a defaul name on the name stack
	glRenderMode (GL_SELECT)
	glInitNames()
		
	# get viewport and projection matrix
	viewport = (GLint * 4) ()
	glGetIntegerv (GL_VIEWPORT, viewport)
	projection = (GLfloat * 16)()
	glGetFloatv (GL_PROJECTION_MATRIX, projection)
	
	# switch to projection transform
	glMatrixMode(GL_PROJECTION)	# select projection matrix
	glPushMatrix()				# push proj matrix
	glLoadIdentity()			# reset matrix

	# restrict picking region to mouse position
	gluPickMatrix (mouse.x, mouse.y, 1, 1, viewport)
	gluPerspective(60., WIDTH / float(HEIGHT), .1, 1000.)
	
	# go back to model view and render selectable objects / things
	glMatrixMode (GL_MODELVIEW)
	# DRAW STUFF TO BE HIT BY MOUSE
	glPushMatrix()
	glTranslatef ( game.camera_x, game.camera_y, game.camera_height )
	game.map.draw_selection()
	for tower in game.towers:
		glPushName (game.towers.index(tower))
		tower.draw_selection()
		glPopName()
	glPopMatrix()
	glMatrixMode (GL_PROJECTION)
	glPopMatrix()
	glMatrixMode (GL_MODELVIEW)
	glLoadIdentity()
	hits = glRenderMode (GL_RENDER)
	if hits>0:
		#print "HIT SOMETHING"
		process_hits (select_buffer)
	else:
		#do nothing
		blah=2	

def process_hits (buffer):
	# takes the gl selection buffer and processes the names / ids of objects within selection range
	# buffer is an array of GLuints (long ints in python) - null char is just 0
	n=buffer[0]
	names=[]
	c=0	# current position in buffer
	
	while n>0:
		names.append((int)(buffer[c+3]))
		c=c+4
		n=buffer[c]
		
	# names is now a list of all names within selection area
	# split into player controlled and enemy entities
	for name in names:
		print "HIT: ", name
			

def update(dt):
	for tower in game.towers:
		tower.update (dt)
	for enemy in game.enemies:
		enemy.update(dt)
	key_handler()
	

	
# MAIN CODE
	
mouse = aMouse()
game = aGame()
game.create_level(44,36,game)
	
pyglet.clock.schedule_interval(update,1/60.)	
pyglet.app.run()