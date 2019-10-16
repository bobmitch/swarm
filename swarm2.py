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

selected=None	# currently selected unit
deploying=None	# unit type selected for deploying

# game modes
MAIN_MENU = 0
IN_GAME = 1
GAME_MODE = IN_GAME


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

# GUI OBEJCT ID
ID_SLOWTOWER = 1000

# WINDOW SETUP
window = pyglet.window.Window(WIDTH,HEIGHT,"sc",True)
window.set_vsync (False)
#window.set_fullscreen(True)
#window.set_exclusive_mouse()
#window.set_mouse_visible (False)

def glEnable2d ():
	glDisable(GL_DEPTH_TEST)
	glMatrixMode (GL_PROJECTION)
	glPushMatrix()
	glLoadIdentity()
	glOrtho (0,window.width,0,window.height,-1,1)
	glMatrixMode (GL_MODELVIEW)
	glPushMatrix()
	glLoadIdentity()
	
def glDisable2d ():
	glEnable(GL_DEPTH_TEST)
	glMatrixMode (GL_MODELVIEW)
	glPopMatrix()
	glMatrixMode (GL_PROJECTION)
	glPopMatrix()

	
def draw_text ():
	# update text
	score_label.text = "Score: " + str(game.score) 
	score_label.y = HEIGHT-30
	
	# draw text
	glEnable2d()
	score_label.draw()
	glDisable2d()

class aGUI:
	def __init__ (self):
		self.mode = 0	# 0=normal, 1=unit selected, 2=deploying
		self.x=game.map.width + 3
		self.y=game.map.height - 3
		
	def draw (self):
		
		# draw slow tower icon
		glColor4f (0.2,1,0.2,1)
		glPushMatrix()
		glTranslatef (self.x, self.y, 0)
		glCallList (TOWER_BASE_DL)
		glCallList (TOWER_SLOW_DL)
		glPopMatrix()
		
	def draw_selection (self):
		glPushName (ID_SLOWTOWER)
		glPushMatrix()
		glTranslatef (self.x, self.y, 0)
		glBegin (GL_QUADS)
		glVertex2f (-1,-1)
		glVertex2f (1,-1)
		glVertex2f (1,1)
		glVertex2f (-1,1)
		glEnd()
		glPopMatrix()
		glPopName()
		
	

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
		self.alpha = 0	# alpha for deployable tower unit
		self.alpha_sin = 0
		self.deployable = False
		
	def update (self, tick):
		self.alpha_sin+=tick*8
		if self.alpha_sin>3.1416:
			self.alpha_sin=0
		self.alpha = (math.sin (self.alpha_sin) + 1) / 2.0
		
	def draw (self):
		# handles drawing of deployable towers
		self.deployable=False # reset before checks later in function
		if deploying:
			x=int(self.map_x+0.5)
			y=int(self.map_y+0.5)
			if amouse.over==999 and x>1 and x<game.map.width-1 and y>1 and y<game.map.height-1:
				# check all cells are passable
				if game.map.cell[x][y].passable and game.map.cell[x-1][y].passable and game.map.cell[x-1][y-1].passable and game.map.cell[x][y-1].passable:
					# check no critters underneath (slow!)
					nothing_underneath=True
					for critter in game.enemies:
						if critter.pos[0] > x-1 and critter.pos[0] < x+1 and critter.pos[1] > y-1 and critter.pos[1] < y+1:
							nothing_underneath=False
							break
					if nothing_underneath:
						self.deployable=True
					else:
						self.deployable=False
					# OK, draw appropraite tower ready for deploying
					if deploying==1:
						if nothing_underneath:
							# slowtower
							glColor4f (0.2,1,0.2, self.alpha)
							glPushMatrix()
							glTranslatef (x, y, 0)
							draw_filled_circle (2,32)
							glCallList (TOWER_BASE_DL)
							glCallList (TOWER_SLOW_DL)
							glPopMatrix()
						else:
							# slowtower - cant build here
							glColor4f (0.2,1,0.2, self.alpha)
							glPushMatrix()
							glTranslatef (x, y, 0)
							glCallList (TOWER_BASE_DL)
							glCallList (TOWER_SLOW_DL)
							glLineWidth(2)
							glColor4f (1,0.2,0.2,1)
							glBegin (GL_LINES)
							glVertex3f (-1,-1,0.01)
							glVertex3f (1,1,0.01)
							glVertex3f (-1,1,0.01)
							glVertex3f (1,-1,0.01)
							glEnd()
							glLineWidth(1)
							glPopMatrix()
				

class aCell:
	def __init__ (self):
		self.entities = []
		self.passable=True
		
		# debug - random maze
		#if random.random() > 0.999:
			#self.passable=False

class aSwarm:
	def __init__(self, type=0, no=10, health=100, time=60):
		
		self.type=type
		self.no=no
		self.count=0
		self.health=health
		self.time=time
		if type==0:
			self.time_between_spawns = 0.5
		self.time_since_last_spawn=0
		
	def update (self, tick):
		self.time -= tick
		self.time_since_last_spawn+=tick
		if self.count < self.no and self.time_since_last_spawn > self.time_between_spawns:
			if self.type == 0:
				# create critter type 0 at start of routes
				for route in game.map.routes:
					if route[0][0]<1:
						# left to right route, adjust random y start
						offset=int(random.random()*6)-3
						newstart=[route[0][0], route[0][1]+offset]
						yadda = normalEnemy(newstart, [route[1][0],route[1][1]+offset ] )
						yadda.health=self.health
					else:
						# top to bottom route, adjust random x start 
						offset = int(random.random()*6)-3
						newstart=[ route[0][0]+offset, route[0][1] ]
						yadda = normalEnemy(newstart, [route[1][0]+offset,route[1][1]])
						yadda.health=self.health
					game.enemies.append ( yadda )
					self.count+=1
					self.time_since_last_spawn=0
		if self.time < 0:
			# do next wave
			print "Next wave..."
			if game.map.swarms:
				# if still have swarms left, pop next from list onto actives
				game.map.active_swarms.append ( game.map.swarms.pop(0) )
			# remove self from active swarm list
			game.map.active_swarms.remove (self)
			
			
		# else do nothing
			
class aMap:
	def __init__ (self, x, y, game):
		# create 2d array of Cells
		self.cell = []
		self.paths = []	# global map of grid cells used for any pathing - each cell contains a counter
		self.width = x
		self.height = y
		self.whichlist = []	#used for a*
		self.closedset = [] #used for a*   nb.  path class uses local openset list
		self.onclosedlist = 2
		self.onopenlist = 1
		self.current_swarm=0
		
		self.routes = [ ([0,14],[x-1,14]) ]	#  list of tuples containing start and end points for swarms
		self.routes.append (  ([x/2,y-1],[x/2,0])  )
		
		# calculate main paths for routes to use in path splicing for individual units
		routepath = aPath (self.routes[0][0],self.routes[0][1])
		self.route_paths = [ routepath ]
		
		self.swarms = []	# type, number of critters, health of each critter, time till next swarm
		self.swarms.append ( aSwarm (0, 10, 10, 20) )
		self.swarms.append ( aSwarm (0, 10, 20, 20) )
		self.swarms.append ( aSwarm (0, 10, 40, 20) )
		self.swarms.append ( aSwarm (0, 10, 70, 20) )
		self.swarms.append ( aSwarm (0, 10, 100, 20) )
		self.swarms.append ( aSwarm (0, 10, 200, 20) )
		self.swarms.append ( aSwarm (0, 30, 1000, 20) )
		self.active_swarms=[ self.swarms.pop(0) ]
		
		
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
		
	def swarm_update (self, tick):
		if self.active_swarms:
			for swarm in self.active_swarms:
				swarm.update(tick)
			
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
		px=pos[0]
		py=pos[1]
		for x in range (pos[0]-1, pos[0]+2):
			for y in range (pos[1]-1,pos[1]+2):
				if x is not -1 and y is not -1 and x is not self.width and y is not self.height:
					# in bounds
					# check if on closedlist
					if self.whichlist[x][y] <> self.onclosedlist:
						# ok , it's not
						if self.cell[x][y].passable:
							corner_walkable=True
							if x == px-1:
								if y == py-1:
									if self.cell[px-1][py].passable is False or self.cell[px][py-1].passable is False:
										corner_walkable=False
								elif y == py+1:
									if self.cell[px-1][py].passable is False or self.cell[px][py+1].passable is False:
										corner_walkable=False
							elif x == px+1:
								if y == py-1:
									if self.cell[px][py-1].passable is False or self.cell[px+1][py].passable is False:
										corner_walkable=False
								elif y == py+1:
									if self.cell[px+1][py].passable is False or self.cell[px][py+1].passable is False:
										corner_walkable=False
							if corner_walkable:
								l.append ([x,y])
		return l
		
		

class slowTower:
	def __init__ (self, position):
		self.highlight = False
		self.pos = position
		self.direction = 0
		self.active = True
		self.target = None
		self.range = 24
		self.time_between_shots = 1.2
		self.time_since_last_shot = 3
		self.target_mode = 1	# 1=nearest end of path 2=nearest 3=furthest 4=weakest 5=strongest 
		
		
	def update (self,dt):
		self.time_since_last_shot+=dt
		if self.time_since_last_shot > self.time_between_shots:
			# find a new target
			nearby_enemies=[]
			for enemy in game.enemies:
				# get squared distance
				sd = (self.pos[0]-enemy.pos[0])**2 + (self.pos[1]-enemy.pos[1])**2
				if sd < self.range:
					nearby_enemies.append ((enemy, sd, len (enemy.mypath.path) ))	# create list of enemy, dist, and path length remaining
			if nearby_enemies:
				enemy_path_left=99999
				closest=99999
				for near_enemy in nearby_enemies:
					if self.target_mode == 1:	# nearest to end of path
						if near_enemy[2] < enemy_path_left:
							enemy_path_left=near_enemy[2]
							self.target = near_enemy[0]	
					elif self.target_mode == 2:	# nearest to tower
						if near_enemy[1] < closest:
							closest = near_enemy[1]
							self.target = near_enemy[0]
			else:
				self.target = None
				return 0
					
		if self.target and self.target.alive:
			# if target also still alive
			# check target is still in range
			sd = (self.pos[0]-self.target.pos[0])**2 + (self.pos[1]-self.target.pos[1])**2
			if sd < self.range:
				# have target, can we fire?
				if self.time_since_last_shot > self.time_between_shots:
					# yes we can
					#print "BANG!"
					game.projectiles.append (slowBullet (copy.copy(self.pos), self.target, 22))
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
		
	def draw_highlight (self):
		glColor4f (1,0.2,0.2,1)
		glPushMatrix()
		glTranslatef (self.pos[0], self.pos[1], 0.01)
		scale = (math.sqrt (self.range))
		draw_filled_circle ( scale, 0.3)
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
		self.speed = 8
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
		glColor4f (1.0, 0.8, 0.2, 0.2)
		glPushMatrix()
		glTranslatef (self.reallyoldpos[0], self.reallyoldpos[1], 0)
		glCallList (PROJ_BULLET_DL)
		glPopMatrix()
		glColor4f (1.0, 0.8, 0.2, 0.4)
		glPushMatrix()
		glTranslatef (self.oldpos[0], self.oldpos[1], 0)
		glCallList (PROJ_BULLET_DL)
		glPopMatrix()
		glColor4f (1.0, 0.8, 0.2, 1)
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
				# Spawn hit particle
				game.particles.append (particle_small_hit (self.pos))
				game.particles.append (particle_small_hit (self.pos))
				game.particles.append (particle_small_hit (self.pos))
				game.particles.append (particle_small_hit (self.pos))
				game.particles.append (particle_small_hit (self.pos))
				game.particles.append (particle_small_hit (self.pos))
				game.projectiles.remove (self)
				self.target.health -= self.damage
			else:
				speed = copy.copy (self.speed) * tick
				self.reallyoldpos=copy.copy(self.oldpos)
				self.oldpos=copy.copy(self.pos)
				if dx==0:
					self.direction=[0,speed*dy]
				elif dy==0:
					self.direction=[speed*dx,0]
				else:
					length = math.sqrt (dx**2 + dy**2)
					self.direction = [ speed*(dx/length), speed*(dy/length) ]
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
					

class particle_small_hit:
	def __init__ (self, pos):
		self.duration = random.random()*0.5
		self.time_alive = 0
		self.xdir = 0.1-(random.random()*0.2)
		self.ydir = 0.1-(random.random()*0.2)
		self.pos=copy.copy(pos)
		self.p1=copy.copy(pos)
		self.p2=[self.p1[0]+self.xdir,self.p1[1]+self.ydir]
		
	def draw (self):
		#glPushMatrix()
		#glTranslatef (self.pos[0], self.pos[1], 0.1)
		#glColor4f (1,0.7,0.1, 1-(self.time_alive/self.duration) )	# fading particles
		glColor4f (1,0.7,0.1, 1 )	# non fading particles
		glBegin (GL_LINES)
		glVertex2f (self.p1[0], self.p1[1])
		glVertex2f (self.p2[0], self.p2[1])
		glEnd ()
		#glPopMatrix()
	
	def update (self, tick):
		self.time_alive += tick
		if self.time_alive < self.duration:
			self.p2=copy.copy(self.p1)
			self.p1[0]+=self.xdir
			self.p1[1]+=self.ydir
		else:
			game.particles.remove (self)
				
				

class particle_explosion:
	def __init__ (self, pos):
		print "Explosion created..."
		self.duration = 1
		self.time_alive = 0
		self.particle_count = 12
		self.dir=[]
		self.curpos=[]
		self.oldpos=[]
		for i in range (0,self.particle_count):
			self.dir.append ([0.5-(random.random()*1.0), 0.5-(random.random()*1.0)])
			a=copy.copy(pos)
			b=copy.copy(pos)
			self.oldpos.append (a)
			self.curpos.append (b)
		
	def draw (self):
		#glColor4f (1,0.7,0.1, 1-(self.time_alive/self.duration) )	# fading particles
		#glColor4f (1,0.7,0.1, 1 )	# non fading particles
		alpha = 1-(self.time_alive/self.duration)
		glLineWidth(2)
		for i in range (0,self.particle_count):
			glBegin (GL_LINES)
			glColor4f (1,0.7,0.1, alpha )
			glVertex2f (self.curpos[i][0], self.curpos[i][1])
			glColor4f (1,0.7,0.1, 0 )
			glVertex2f (self.oldpos[i][0], self.oldpos[i][1])
			glEnd ()
		glLineWidth(1)
		
	
	def update (self, tick):
		self.time_alive += tick
		if self.time_alive < self.duration:
			for i in range (0,self.particle_count):
				if self.time_alive > 0.2:
					self.oldpos[i][0]+=self.dir[i][0]
					self.oldpos[i][1]+=self.dir[i][1]
				#self.oldpos[i] = copy.copy(self.curpos[i])
				self.curpos[i][0]+=self.dir[i][0]
				self.curpos[i][1]+=self.dir[i][1]
				self.dir[i][0]*=0.96	# slows particles due to air density
				self.dir[i][1]*=0.96	# slows particles due to air density
		else:
			game.particles.remove (self)
				
				
				
class normalEnemy:
	""" pass start point and goal point optionally """
	def __init__ (self, start=[0,8], goal=[30,8]):
		self.pos = [0,0]
		self.pos[0]=start[0]+0.5
		self.pos[1]=start[1]+0.5
		self.path_position=0
		self.diag = False
		self.health = 100
		self.alive = True
		self.dir = RIGHT
		self.speed = 1.7
		self.mypath = aPath(start,goal)
		self.mypath.calc(game.map)
		#print self.mypath.path
		self.next_position = [0.5+x for x in self.mypath.path[0]]
		if abs(self.pos[0]-self.next_position[0]) > 0.6 and abs(self.pos[1]-self.next_position[1]) > 0.6:
			self.diag = True
		else:
			self.diag = False
		
	def draw (self):
		#self.mypath.draw()
		glPushMatrix()
		glTranslatef (self.pos[0], self.pos[1], 0.1)
		glCallList (ENEMY_NORMAL_DL)
		glPopMatrix()

	def update (self, tick):
		if self.health<0:
			# I`m dead
			game.particles.append (particle_explosion(self.pos))
			self.alive = False
			game.score += 200
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
				if abs(self.pos[0]-self.next_position[0]) > 0.6 and abs(self.pos[1]-self.next_position[1]) > 0.6:
					self.diag = True
				else:
					self.diag = False
			else:
				# job done - update all
				for path_entry in self.mypath.path:
					game.map.paths[path_entry[0]][path_entry[1]]-=1	# remove path from global path counter
				self.alive = False
				game.enemies.remove (self)
			
			
		if self.diag:
			speed = self.speed * 0.7
			if self.pos[0] > self.next_position[0]+0.1:
				self.pos[0] -= tick * speed
			elif self.pos[0] < self.next_position[0]-0.1:
				self.pos[0] += tick * speed
			if self.pos[1] > self.next_position[1]+0.1:
				self.pos[1] -= tick *speed
			elif self.pos[1] < self.next_position[1]-0.1:
				self.pos[1] += tick *speed
		else:
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
		#return cmp(other.f, self.f)
		
	def __lt__ (self, other):
		return (self.f < other.f)
		
	def __le__ (self, other):
		return (self.f <= other.f)
		
	def __gt__ (self, other):
		return (self.f > other.f)
		
	def __ge__ (self, other):
		return (self.f >= other.f)
		
	def __eq__ (self, other):
		return (self.f == other.f)

		
def manhattan (a, b):
	return abs(a[0]-b[0]) + abs(a[1]-b[1])
		
		
class aPath:
	def __init__ (self, start=[0,0], end=[0,0]):
		self.path=[] # list of coordinate tuples
		self.start = start
		self.end = end
		
	def draw (self):
		glColor4f (0.5,0.5,0.8,0.3)
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
		closedset=map.closedset
		openset=[]	# nb.  maintained as binary heap, using heappush and heappop 
		start=aNode(self.start)
		start.h = manhattan (self.start, self.end)
		start.f = start.g + start.h
		#openset=[start]
		heappush (openset,start)
		map.whichlist[self.start[0]][self.start[1]] = onopenlist
		while openset:
			# get lowest score node from openset
			x = heappop (openset)
			if x.pos == self.end:
				#print "PATH COMPLETE!!!"
				# reconstruct path - and update maps 'paths' array
				self.path = []
				while x.parent is not None:
					map.paths[x.pos[0]][y.pos[1]]+=1
					self.path.append (x.pos)
					x = x.parent
				self.path.reverse()
				# add each item of the path to the global path counter array
				for item in self.path:
					game.map.paths[item[0]][item[1]]+=1
				del (openset)
				return 1
			# path not completed yet....
			closedset.append (x)
			map.whichlist[x.pos[0]][x.pos[1]] = onclosedlist
			# get neighbour list
			for y_pos in map.get_neighbours (x.pos):
				if map.whichlist[y_pos[0]][y_pos[1]] <> onclosedlist :
					tentative_g_score = x.g + 1
					if map.whichlist[y_pos[0]][y_pos[1]] <> onopenlist :
						y = aNode (y_pos)
						y.h = manhattan (y.pos, self.end)
						y.parent = x
						y.g = tentative_g_score
						y.f = y.g + y.h
						heappush (openset, y)
						map.whichlist[y_pos[0]][y_pos[1]] = onopenlist
					else:
						# get g score already in openset
						for i in openset:
							if i.pos == y_pos:
								if tentative_g_score < i.g:
									i.parent = x
									i.g = tentative_g_score
									i.f = i.g + i.h
									break
						
			# debug - show openlist and wait for keypress
			#openset.sort()
			#print "Openset after checking neighbours:"
			#for i in openset:
			#	print i, " : ", i.f
			#blah = raw_input ()
		print "NO PATH FOUND between ", self.start," and ",self.end
		del (openset)
		return 0
						
			
	
		
			
		
class aGame:
	def __init__ (self):
		self.map = None
		self.create_tower_display_lists()
		self.towers=[]
		self.enemies=[]
		self.projectiles=[]
		self.particles=[]
		self.camera_x = 0
		self.camera_y = 0
		self.camera_height = 0
		self.gui = None
		self.score = 0
		self.bonus = 0
		self.credits = 75
		
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
		self.camera_height = -(max(x, y)) * 0.99
		self.camera_x = -(x/2.0)-4
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
	glMatrixMode (GL_MODELVIEW)
	glLoadIdentity()
	window.clear()
	do_selection()
	
	# DRAW MAP PLUS ENTITIES
	
	# move camera
	glTranslatef ( game.camera_x, game.camera_y, game.camera_height )
	
	amouse.draw()
	
	game.gui.draw()
	
	game.map.draw()
	
	glTranslatef (0,0,0.03)
	for enemy in game.enemies:
		enemy.draw()
	
	for tower in game.towers:
		tower.draw()
		
	if amouse.over < 999:
		game.towers[amouse.over].draw_highlight()
		
	for proj in game.projectiles:
		proj.draw()
		
	for part in game.particles:
		part.draw()
		
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
	glReadPixels (amouse.x, amouse.y, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT, depth) #get depth buffer for mouse pixel
	gluUnProject(amouse.x, amouse.y, depth[0], model_view, projection, viewport, x, y, z)
	# convert gl floats to standard python floats
	amouse.map_x = x.value 
	amouse.map_y = y.value 
	amouse.map_z = z.value
	
	# do 2d text
	draw_text()
	
		
	
	
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
		
		# check if paths need recalculated
		if game.map.paths[x][y]>0 or game.map.paths[x-1][y]>0 or game.map.paths[x-1][y-1]>0 or game.map.paths[x][y-1]>0:
			# yes, recalc paths for critters
			print "Recalculating paths..."
			for enemy in game.enemies:
				enemy.mypath.start[0] = int(enemy.pos[0])
				enemy.mypath.start[1] = int(enemy.pos[1])
				enemy.mypath.calc(game.map)
				enemy.next_position = [0.5+x for x in enemy.mypath.path[0]]
				enemy.path_position=0
		else:
			print "No need to recalculate!"
	if keybstate.s: 
		print "S pressed"
		keybstate.s=False
		yadda = normalEnemy([0,int(random.random()*11)],[game.map.width-1,11])
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
	global amouse
	amouse.x = x
	amouse.y = y
	
@window.event
def on_mouse_release (x,y,buttons,modifiers):
	if buttons & mouse.LEFT:
		# left clicked on something - see what mouse is over
		if amouse.over > 999 and amouse.over<9999:
			# clicked on gui element
			if amouse.over==1000:
				#clicked on slowtower icon
				print "Ready to deploy tower..."
				deploying=slowTower([0,0])

		if amouse.over < 999:
			# clicked on tower
			global selected
			selected = game.towers[amouse.over]
			global deploying
			deploying=None
			print "Selected a tower."
			
		if amouse.over == 999:
			# clicked on map
			if deploying and amouse.deployable:
				# have something to deploy and am able to deploy
				x=int(amouse.map_x+0.5)
				y=int(amouse.map_y+0.5)
				game.map.cell[x][y].passable=False
				game.map.cell[x-1][y].passable=False
				game.map.cell[x-1][y-1].passable=False
				game.map.cell[x][y-1].passable=False
				
				if deploying==1:
					#deploy slow tower
					blah = slowTower([x,y])
					game.towers.append ( blah )
					
				# check if paths need recalculated
				if game.map.paths[x][y]>0 or game.map.paths[x-1][y]>0 or game.map.paths[x-1][y-1]>0 or game.map.paths[x][y-1]>0:
					# yes, recalc paths for critters
					print "Recalculating paths..."
					for enemy in game.enemies:
						enemy.mypath.start[0] = int(enemy.pos[0])
						enemy.mypath.start[1] = int(enemy.pos[1])
						enemy.mypath.calc(game.map)
						enemy.next_position = [0.5+x for x in enemy.mypath.path[0]]
						enemy.path_position=0
				else:
					print "No need to recalculate!"
					
				# tidy up
					
			
	if buttons & mouse.RIGHT:
		# right clicked
		print "Cancelling all orders..."
		global selected
		global deploying
		selected = None
		deploying = None
		
			
		

		
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
	global WIDTH, HEIGHT
	WIDTH=width
	HEIGHT=height
	
	return pyglet.event.EVENT_HANDLED

	
def draw_circle (r,i):
	angle=0
	glBegin (GL_LINE_STRIP)
	while angle<=i+(math.pi*2):
		glVertex2f (math.cos(angle)*r, math.sin(angle)*r)
		angle+=i
	glEnd()
	
def draw_filled_circle (r,i, outline=True):
	angle=0
	glColor4f (1,0.2,0.2,0.1)
	glBegin (GL_TRIANGLE_FAN)
	glVertex2f (0,0)	# first vert in centre
	while angle<=i+(math.pi*2):
		glVertex2f (math.cos(angle)*r, math.sin(angle)*r)
		angle+=i
	glEnd()
	
	if outline:
		glColor4f (1,0.2,0.2,1)
		angle=0
		glBegin (GL_LINE_STRIP)
		while angle<=i+(math.pi*2):
			glVertex3f (math.cos(angle)*r, math.sin(angle)*r, 0.01)
			angle+=i
		glEnd()

	
	

	
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
	gluPickMatrix (amouse.x, amouse.y, 1, 1, viewport)
	gluPerspective(60., WIDTH / float(HEIGHT), .1, 1000.)
	
	# go back to model view and render selectable objects / things
	glMatrixMode (GL_MODELVIEW)
	# DRAW STUFF TO BE HIT BY MOUSE
	glPushMatrix()
	glTranslatef ( game.camera_x, game.camera_y, game.camera_height )
	glPushName (999)
	game.map.draw_selection()
	glPopName()
	game.gui.draw_selection()
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
		amouse.over = 99999	# mouse is over empty space
		

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
		amouse.over = 999	# mouse is over map
		#print "Mouse on map at: ", mouse.map_x, ",", mouse.map_y, ",", mouse.map_z #DEBUG
	else:
		for name in names:
			if name < 999:
				# mouse is over a tower - mouse.over = index in towers list
				amouse.over = name
				#game.towers[name].draw_highlight()
			if name > 999 and name < 99999:
				# mouse is over a gui element - mouse.over = index in gui list
				amouse.over = name
			

def update(dt):
	amouse.update (dt)
	game.map.swarm_update (dt)
	for particle in game.particles:
		particle.update (dt)
	for tower in game.towers:
		tower.update (dt)
	for enemy in game.enemies:
		enemy.update(dt)
	for proj in game.projectiles:
		proj.update(dt)
	key_handler()
	#print mouse.over #debug
	

	
# MAIN CODE

import psyco
psyco.full()
#psyco.bind(aPath)

game = aGame()
amouse = aMouse()

game.create_level (30,26,game)
game.gui = aGUI()
	
score_label = pyglet.text.Label("Score: " + str(game.score)  , 
                          font_name='Saved By Zero', 
                          font_size=16,
                          x=30, y=window.height-30)
	
	
pyglet.clock.schedule_interval(update,1/60.)	
pyglet.app.run()