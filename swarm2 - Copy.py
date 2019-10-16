from psyco.classes import *
from heapq import heappush, heappop
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
HEIGHT = 600

LEFT = 1
RIGHT = 2
UP = 3
DOWN = 4

# TOWER TYPES
SLOW_TOWER = 1
FAST_TOWER = 2

# DISPLAY LISTS
GRID_DL = 1
TOWER_BASE_DL = 5
TOWER_SLOW_DL = 10
TOWER_FAST_DL = 20

ENEMY_NORMAL_DL = 200

PROJ_BULLET_DL = 300


# OBJECT ID
ID_NOTHING = 99999
ID_MAP = 1
ID_TOWER = 2


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
		self.map_z=0
		self.lmb_down = False
		self.lmb_up = False
		self.lmb_clicked = False
		self.over = 0

class aCell:
	def __init__ (self):
		self.entities = []
		self.passable=True
		
		# debug - random maze
		if random.random() > 0.99:
			self.passable=False

class aMap:
	def __init__ (self, x, y, game):
		# create 2d array of Cells
		self.cell = []
		self.paths = []	# global map of grid cells used for any pathing
		self.width = x
		self.height = y
		self.whichlist = []	#used for a*
		self.onclosedlist = 2
		self.onopenlist = 1
		
		# create map
		for a in xrange(0,x):
			row=[]
			for b in xrange(0,y):
				row.append ( aCell() )
			self.cell.append ( row )
			
		# create whichlist for a* pathing	
		for a in xrange(0,x):
			row=[]
			for b in xrange(0,y):
				row.append ( 0 )
			self.whichlist.append ( row )
			
		# create global map of where a* paths have been created (via counters)	
		for a in xrange(0,x):
			row=[]
			for b in xrange(0,y):
				row.append ( 0 )
			self.paths.append ( row )
		
		self.create_display_list(game)
			
	def create_display_list (self, game):
		glNewList(1,GL_COMPILE)
		# QUAD
		glColor4f (0.6,0.6,1,0.1)
		glBegin (GL_QUADS)
		glVertex3f (0,0,-0.001)
		glVertex3f (self.width,0,-0.001)
		glVertex3f (self.width,self.height,-0.001)
		glVertex3f (0,self.height,-0.001)
		glEnd()
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
		glColor4f (1,1,1,0.1)
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
		
	def get_neighbours (self, pos):
		l=[]
		if pos[0]>0 and self.cell[pos[0]-1][pos[1]].passable:
			l.append ([pos[0]-1,pos[1]])
		if pos[0]<self.width-1 and self.cell[pos[0]+1][pos[1]].passable:
			l.append ([pos[0]+1,pos[1]])
		if pos[1]>0 and self.cell[pos[0]][pos[1]-1].passable:
			l.append ([pos[0],pos[1]-1])
		if pos[1]<self.height-1 and self.cell[pos[0]][pos[1]+1].passable:
			l.append ([pos[0],pos[1]+1])
		return l
		

class slowTower:
	def __init__ (self, position):
		self.pos = position
		self.direction = 0
		self.active = True
		self.target = None
		self.range = 56
		self.time_between_shots = 2
		self.time_since_last_shot = 3
		
		
	def update (self,dt):
		self.time_since_last_shot+=dt
		if not self.target:
			#find a target
			for enemy in game.enemies:
				# get squared distance
				sd = (self.pos[0]-enemy.pos[0])**2 + (self.pos[1]-enemy.pos[1])**2
				if sd < self.range:
					# got ourselves a target
					self.target = enemy
					break
		elif self.target.alive:
			# if target also still alive
			# check target is still in range
			sd = (self.pos[0]-self.target.pos[0])**2 + (self.pos[1]-self.target.pos[1])**2
			if sd < self.range:
				# have target, can we fire?
				if self.time_since_last_shot > self.time_between_shots:
					# yes we can
					print "BANG!"
					game.projectiles.append (slowBullet (copy.copy(self.pos), self.target, 10))
					self.time_since_last_shot=0
				# turn turret to face target
				# get angle in degrees from turret to target
				dx = self.pos[0] - self.target.pos[0]
				dy = self.pos[1] - self.target.pos[1]
				self.direction = math.atan2 (dy, -dx) * 57.2957795 + 90
			else:
				# old target left range
				self.target = None
		else:
			self.target = None
			
		
		
		
	def draw (self):
		glColor4f (0.2,1,0.2,1)
		glPushMatrix()
		glTranslatef (self.pos[0], self.pos[1], 0)
		glCallList (TOWER_BASE_DL)
		glRotatef (-self.direction, 0, 0, 1)
		glCallList (TOWER_SLOW_DL)
		glPopMatrix()
		glPopMatrix()
		
	def draw_selection (self):
		glPushMatrix()
		glTranslatef (self.pos[0], self.pos[1], 0)
		glBegin (GL_QUADS)
		glVertex2f (-1,-1)
		glVertex2f (1,-1)
		glVertex2f (1,1)
		glVertex2f (-1,1)
		glEnd()
		glPopMatrix()


		
class aaBullet:
	def __init__ (self, pos, target, damage):
		self.pos=pos
		self.target=target
		self.damage=damage
		self.speed = 1
		dx = target.pos[0]-pos[0]
		dy = target.pos[1]-pos[1]
		length = math.sqrt (dx**2 + dy**2)
		if dx==0:
			self.direction=[0,self.speed*dy]
		elif dy==0:
			self.direction=[self.speed*dx,0]
		else:
			self.direction = [ self.speed*(dx/length), self.speed*(dy/length) ]
		
	def draw (self):
		glPushMatrix()
		glTranslatef (self.pos[0], self.pos[1], 0)
		glCallList (PROJ_BULLET_DL)
		glPopMatrix()
		
	def update (self, tick):
		if self.target.alive:
			dx = self.target.pos[0]-self.pos[0]
			dy = self.target.pos[1]-self.pos[1]
			if abs(dx) < 0.5 and abs(dy) < 0.5:
				# HIT TARGET
				game.projectiles.remove (self)
				self.target.health -= self.damage
			else:
				self.pos[0] += self.direction[0]
				self.pos[1] += self.direction[1]
		
		
		
class slowBullet:
	def __init__ (self, pos, target, damage):
		self.pos=pos
		self.oldpos=copy.copy(pos)
		self.reallyoldpos=copy.copy(pos)
		self.target=target
		self.damage=damage
		self.speed = 0.2
		dx = target.pos[0]-pos[0]
		dy = target.pos[1]-pos[1]
		length = math.sqrt (dx**2 + dy**2)
		if dx==0:
			self.direction=[0,self.speed*dy]
		elif dy==0:
			self.direction=[self.speed*dx,0]
		else:
			self.direction = [ self.speed*(dx/length), self.speed*(dy/length) ]
		
	def draw (self):
		glColor4f (0.2, 1.0, 0.2, 0.2)
		glPushMatrix()
		glTranslatef (self.reallyoldpos[0], self.reallyoldpos[1], 0)
		glCallList (PROJ_BULLET_DL)
		glPopMatrix()
		glColor4f (0.2, 1.0, 0.2, 0.4)
		glPushMatrix()
		glTranslatef (self.oldpos[0], self.oldpos[1], 0)
		glCallList (PROJ_BULLET_DL)
		glPopMatrix()
		glColor4f (0.2, 1.0, 0.2, 1)
		glPushMatrix()
		glTranslatef (self.pos[0], self.pos[1], 0)
		glCallList (PROJ_BULLET_DL)
		glPopMatrix()
		
	def update (self, tick):
		if self.target.alive:
			dx = self.target.pos[0]-self.pos[0]
			dy = self.target.pos[1]-self.pos[1]
			if abs(dx) < 0.5 and abs(dy) < 0.5:
				# HIT TARGET
				game.projectiles.remove (self)
				self.target.health -= self.damage
			else:
				self.reallyoldpos=copy.copy(self.oldpos)
				self.oldpos=copy.copy(self.pos)
				if dx==0:
					self.direction=[0,self.speed*dy]
				elif dy==0:
					self.direction=[self.speed*dx,0]
				else:
					length = math.sqrt (dx**2 + dy**2)
					self.direction = [ self.speed*(dx/length), self.speed*(dy/length) ]
					self.pos[0] += self.direction[0]
					self.pos[1] += self.direction[1]
		else:
			# target gone - just remove projectile once out of range / off map
			if self.pos[0]<0 or self.pos[0]>game.map.width or self.pos[1]<0 or self.pos[1]>game.map.height:
				game.projectiles.remove (self)
				return 1
			self.reallyoldpos=copy.copy(self.oldpos)
			self.oldpos=copy.copy(self.pos)
			self.pos[0] += self.direction[0]
			self.pos[1] += self.direction[1]
					

				
				
class normalEnemy:
	""" pass start point and goal point optionally """
	def __init__ (self, start=[0,8], goal=[30,8]):
		self.pos = [0,0]
		self.pos[0]=start[0]+0.5
		self.pos[1]=start[1]+0.5
		self.path_position=0
		
		self.health = 100
		self.alive = True
		self.dir = RIGHT
		self.speed = 2
		self.mypath = aPath(start,goal)
		self.mypath.calc(game.map)
		#print self.mypath.path
		self.next_position = [0.5+x for x in self.mypath.path[0]]
		
	def draw (self):
		self.mypath.draw()
		glPushMatrix()
		glTranslatef (self.pos[0], self.pos[1], 0.1)
		glCallList (ENEMY_NORMAL_DL)
		glPopMatrix()

	def update (self, tick):
		if self.health<0:
			# I`m dead
			self.alive = False
			game.enemies.remove (self)
			return 0
		if abs(self.pos[0]-self.next_position[0]) < 0.1 and abs(self.pos[1]-self.next_position[1]) < 0.1:
			# ready for next path step
			removed_path_position = self.mypath.path.pop(0)
			# also, reduce path counter in global path map
			game.map.paths[removed_path_position[0]][removed_path_position[1]] -= 1
			# check if at end of path
			if self.mypath.path:
				# path not finished yet - get next position
				self.next_position = [0.5+x for x in self.mypath.path[0]]
			else:
				# job done - update all
				self.alive = False
				game.enemies.remove (self)
			
			
			
			
		if self.pos[0] > self.next_position[0]+0.1:
			self.pos[0] -= tick * self.speed
		elif self.pos[0] < self.next_position[0]-0.1:
			self.pos[0] += tick * self.speed
		if self.pos[1] > self.next_position[1]+0.1:
			self.pos[1] -= tick * self.speed
		elif self.pos[1] < self.next_position[1]-0.1:
			self.pos[1] += tick * self.speed
		
		
		

class aNode:
	""" a* node """
	def __init__ (self, pos=[0,0]):
		self.pos=pos
		self.g = 0
		self.h = 0
		self.f = 0
		self.parent=None
		
	def __cmp__(self, other):
		return cmp(self.f, other.f)

		
def manhattan (a, b):
	return abs(a[0]-b[0]) + abs(a[1]-b[1])
		
		
class aPath:
	def __init__ (self, start=[0,0], end=[0,0]):
		self.path=[] # list of coordinate tuples
		self.start = start
		self.end = end
		
	def draw (self):
		glColor4f (0.5,0.5,0.8,0.2)
		glBegin (GL_QUADS)
		for coord in self.path:	
			glVertex3f (coord[0], coord[1], 0)
			glVertex3f (coord[0]+1, coord[1], 0)
			glVertex3f (coord[0]+1, coord[1]+1, 0)
			glVertex3f (coord[0], coord[1]+1, 0)
		glEnd()
			
	def calc (self, map):
		#print "Calculating path..."
		map.onclosedlist = map.onclosedlist + 2
		map.onopenlist = map.onclosedlist -1
		onopenlist=map.onopenlist
		onclosedlist=map.onclosedlist
		closedset=[]
		openset=[]	# nb.  maintained as binary heap
		start=aNode(self.start)
		start.h = manhattan (self.start, self.end)
		start.f = start.g + start.h
		openset=[start]
		map.whichlist[self.start[0]][self.start[1]] = onopenlist
		while openset:
			#openset.sort()	# nodes cmp function based on f cost, so item at head of openset has lowest cost
			# find lowest cost node in openset
			n=0
			c=99999
			for i in range(0,len(openset)):
				if openset[i].f<c:
					n=i
					c=openset[i].f
			x = openset[n]
			if x.pos == self.end:
				#print "PATH COMPLETE!!!"
				# reconstruct path
				self.path = []
				while x.parent is not None:
					self.path.append (x.pos)
					x = x.parent
				self.path.reverse()
				return 1
			openset.remove (x)
			closedset.append (x)
			map.whichlist[x.pos[0]][x.pos[1]] = onclosedlist
			# get neighbour list
			for y_pos in map.get_neighbours (x.pos):
				y = aNode (y_pos)
				if map.whichlist[y_pos[0]][y_pos[1]] <> onclosedlist :
					tentative_g_score = x.g + 1
					tentative_is_better = False
					if map.whichlist[y_pos[0]][y_pos[1]] <> onopenlist :
						y.h = manhattan (y.pos, self.end)
						tentative_is_better = True
						openset.append (y)
						map.whichlist[y_pos[0]][y_pos[1]] = onopenlist
					elif tentative_g_score < y.g:
						tentative_is_better = True
					if tentative_is_better:
						y.parent = x
						y.g = tentative_g_score
						y.f = y.g + y.h
		print "NO PATH FOUND"
		return 0
						
			
	
		
			
		
class aGame:
	def __init__ (self):
		self.map = None
		self.create_tower_display_lists()
		self.towers=[]
		self.enemies=[]
		self.projectiles=[]
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
		
		# NORMAL BULLET
		glNewList(PROJ_BULLET_DL, GL_COMPILE)
		glBegin (GL_QUADS)
		glVertex2f (-0.1, -0.1)
		glVertex2f (0.1, -0.1)
		glVertex2f (0.1, 0.1)
		glVertex2f (-0.1, 0.1)
		glEnd ()
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
		self.camera_x = -(x/2.0)-6
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
	glLoadIdentity()
	window.clear()
	do_selection()
	
	# DRAW MAP PLUS ENTITIES
	
	# move camera
	glTranslatef ( game.camera_x, game.camera_y, game.camera_height )
	
	game.map.draw()
	
	glTranslatef (0,0,0.03)
	for enemy in game.enemies:
		enemy.draw()
	
	for tower in game.towers:
		tower.draw()
		
	for proj in game.projectiles:
		proj.draw()
		
	# END DRAW MAP PLUS ENTITIES
	
	# get 3d coords
	model_view = (GLdouble * 16)()
	glGetDoublev(GL_MODELVIEW_MATRIX, model_view)
	projection = (GLdouble * 16)()
	glGetDoublev(GL_PROJECTION_MATRIX, projection)
	viewport = (GLint * 4)(); 
	glGetIntegerv(GL_VIEWPORT, viewport)
	x = (GLdouble)()
	y = (GLdouble)()
	z = (GLdouble)()
	depth = (GLfloat * 2)() # depth glfloat pixel buffer - used below to contain the depth buffer value for the pixel under the cursor
	glReadPixels (mouse.x, mouse.y, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT, depth) #get depth buffer for mouse pixel
	gluUnProject(mouse.x, mouse.y, depth[0], model_view, projection, viewport, x, y, z)
	# convert gl floats to standard python floats
	mouse.map_x = x.value 
	mouse.map_y = y.value 
	mouse.map_z = z.value
	
	
		
	
	
def key_handler ():
	if keybstate.w: 
		print "W pressed"
		keybstate.w=False
		x=int(random.random()*game.map.width)
		y=int(random.random()*game.map.height)
		blah = slowTower([x,y])
		game.towers.append ( blah )
		game.map.cell[x][y].passable=False
		game.map.cell[x-1][y].passable=False
		game.map.cell[x-1][y-1].passable=False
		game.map.cell[x][y-1].passable=False
		for enemy in game.enemies:
			enemy.mypath.start[0] = int(enemy.pos[0])
			enemy.mypath.start[1] = int(enemy.pos[1])
			enemy.mypath.calc(game.map)
			enemy.next_position = [0.5+x for x in enemy.mypath.path[0]]
			enemy.path_position=0
	if keybstate.s: 
		print "S pressed"
		keybstate.s=False
		yadda = normalEnemy([0,6],[game.map.width-1,9])
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
	glEnable (GL_DEPTH_TEST)
	glHint (GL_LINE_SMOOTH_HINT, GL_NICEST)
	glLineWidth(1)
	glLoadIdentity()
	gluPerspective(60., width / float(height), .1, 1000.)
	glMatrixMode(GL_MODELVIEW)
	return pyglet.event.EVENT_HANDLED

def do_selection():
	# set up selection buffer
	glLoadIdentity()
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
	glPushName (999)
	game.map.draw_selection()
	glPopName()
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
		process_hits (select_buffer)
	else:
		mouse.over = 99999	# mouse is over empty space
		

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
	if len(names)==1 and names[0]==999:
		mouse.over = 999	# mouse is over map
		#print "Mouse on map at: ", mouse.map_x, ",", mouse.map_y, ",", mouse.map_z #DEBUG
	else:
		for name in names:
			if name < 999:
				# mouse is over a tower - mouse.over = index in towers list
				mouse.over = name
			if name > 999 and name < 99999:
				# mouse is over a gui element - mouse.over = index in gui list
				mouse.over = name
			

def update(dt):
	for tower in game.towers:
		tower.update (dt)
	for enemy in game.enemies:
		enemy.update(dt)
	for proj in game.projectiles:
		proj.update(dt)
	key_handler()
	#print mouse.over #debug
	

	
# MAIN CODE


game = aGame()
mouse = aMouse()

game.create_level (42,32,game)
	
pyglet.clock.schedule_interval(update,1/60.)	
pyglet.app.run()