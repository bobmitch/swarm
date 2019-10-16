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

ZOOMED=False

SELL_TIME=1
SELL_TIME_INCREASE=1

selected=None	# currently selected unit
deploying=None	# unit type selected for deploying
buttons={}		# dictionary of all gui and menu buttons
ai={1:"Nearest exit",2:"Nearest tower",3:"Strongest",4:"Weakest",5:"Fastest",6:"Slowest"}

# game modes
MAIN_MENU = 0
PRE_GAME = True
IN_GAME = 1
PAUSED = 2
GAME_STATE = IN_GAME


WIDTH = 800
HEIGHT = 600

LEFT = 1
RIGHT = 2
UP = 3
DOWN = 4

# TOWER TYPES
SLOW_TOWER = 1
FAST_TOWER = 2

# TOWER STATS
SLOW_TOWER_COST = 5
SLOW_TOWER_RANGE = 9
SLOW_TOWER_RANGE_SQ = int(math.sqrt (SLOW_TOWER_RANGE))
SLOW_TOWER_DAMAGE = 5
SLOW_TOWER_UPGRADE_COST = 20
SLOW_TOWER_SELL_PRICE = 3
SLOW_TOWER_UPGRADE_TIME = 2

SLOW_TOWER2_COST = 20
SLOW_TOWER2_RANGE = 16
SLOW_TOWER2_RANGE_SQ = int(math.sqrt (SLOW_TOWER2_RANGE))
SLOW_TOWER2_DAMAGE = 25
SLOW_TOWER2_UPGRADE_COST = 50
SLOW_TOWER2_SELL_PRICE = 10
SLOW_TOWER2_UPGRADE_TIME = 4

SLOW_TOWER3_COST = 150
SLOW_TOWER3_RANGE = 25
SLOW_TOWER3_RANGE_SQ = int(math.sqrt (SLOW_TOWER2_RANGE))
SLOW_TOWER3_DAMAGE = 75
SLOW_TOWER3_UPGRADE_COST = 240
SLOW_TOWER3_SELL_PRICE = 70
SLOW_TOWER3_UPGRADE_TIME = 8

# DISPLAY LISTS
GRID_DL = 1
TOWER_BASE_DL = 5
TOWER_SLOW_DL = 10
TOWER_SLOW2_DL = 11
TOWER_SLOW3_DL = 12
TOWER_FAST_DL = 20

ENEMY_NORMAL_DL = 200

PROJ_BULLET_DL = 300



# OBJECT ID
ID_NOTHING = 99999
ID_MAP = 1
ID_TOWER = 2

# GUI OBEJCT ID
ID_SLOWTOWER = 1000
ID_UPGRADE = 1100
ID_UPGRADE_NOT_OK = 1101
ID_PAUSE = 1102
ID_START = 1103
ID_SELL = 1104
ID_AI_STRONG_OFF = 1105
ID_AI_WEAK_OFF = 1106
ID_AI_FAST_OFF = 1107
ID_AI_SLOW_OFF = 1108
ID_AI_NEAR_OFF = 1109
ID_AI_FAR_OFF = 1110
ID_AI_STRONG_ON = 1111
ID_AI_WEAK_ON = 1112
ID_AI_FAST_ON = 1113
ID_AI_SLOW_ON = 1114
ID_AI_NEAR_ON = 1115
ID_AI_FAR_ON = 1116

# WINDOW SETUP
window = pyglet.window.Window(WIDTH,HEIGHT,"sc",True)
window.set_vsync (False)
#window.set_fullscreen(True)
#window.set_exclusive_mouse()
#window.set_mouse_visible (False)

class button:
	def __init__ (self, x, y, w, h, id, texid):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.id = id
		self.texid = texid
	
	def draw (self):
		glPushMatrix()
		glTranslatef (self.x, self.y, 0)
		glBindTexture (GL_TEXTURE_2D, self.texid)
		glEnable (GL_TEXTURE_2D)
		glBegin(GL_QUADS)
		glTexCoord2f (0,0)
		glVertex2f (0,0)
		glTexCoord2f (0,1)
		glVertex2f (0,self.h)
		glTexCoord2f (1,1)
		glVertex2f (self.w, self.h)
		glTexCoord2f (1,0)
		glVertex2f (self.w, 0)
		glEnd()
		glPopMatrix()
		glDisable (GL_TEXTURE_2D)
		
	def draw_selection (self):
		glPushName (self.id)
		glPushMatrix()
		glTranslatef (self.x, self.y, 0)
		glBegin (GL_QUADS)
		glVertex2f (0,0)
		glVertex2f (0,self.h)
		glVertex2f (self.w, self.h)
		glVertex2f (self.w, 0)
		glEnd()
		glPopMatrix()
		glPopName ()
	

class bitmap_font:
	def __init__ (self, name, texture_id=4):
		self.glyphs={}
		self.texid = texture_id
		# load font file and textures
		f = open(name+'.fnt', 'r')
		fc = f.readlines()	# read all lines in fnt file into list
		# read texture filename - page id=0 file="test_00.png"
		tf = fc[2].split('"')[1]
		# load texture and create mipmap
		tex_image = pyglet.image.load (tf)
		self.texture = tex_image.get_mipmapped_texture()
		x_scale = 1.0 / tex_image.width
		y_scale = 1.0 / tex_image.height
		# get number of chars n from chars count=10
		n = int(fc[3].split('=')[1])
		# loop through each character and put glyph info into glyphs dictionary 
		# example line: char id=48   x=42    y=0     width=39    height=62    xoffset=4     yoffset=16    xadvance=47    page=0  chnl=15
		for m in range(4,n+4):
			print "Char "+str(m-3)+",",
			charid = int(fc[m].split('=')[1].split()[0])
			x = int(fc[m].split('=')[2].split()[0])
			y = int(fc[m].split('=')[3].split()[0])
			w = int(fc[m].split('=')[4].split()[0])
			h = int(fc[m].split('=')[5].split()[0])
			xo = int(fc[m].split('=')[6].split()[0])
			yo = int(fc[m].split('=')[7].split()[0])
			xa = int(fc[m].split('=')[8].split()[0])
			char = chr(charid)
			# generate glyph entry in dictionary
			# nple: x tex coord, y tex coord, x tex width, x tex height, xo, yo, xa
			# always drawn clockwise from tl
			self.glyphs[char] = (x*x_scale, 1-(y*y_scale), w*x_scale, h*y_scale, xo*x_scale, yo*y_scale, xa*x_scale)
		self.fixed_width=self.glyphs['w'][6]
			
	def draw (self, ox, oy, text, scale=10, fixed=False):
		x=copy.copy(ox)
		y=copy.copy(oy)
		glEnable (GL_TEXTURE_2D)
		glBindTexture (GL_TEXTURE_2D, self.texid)
		glBegin (GL_QUADS)
		for c in text:
			if ord(c)==10:
				# newline
				y-=(scale*(self.glyphs['w'][3]+self.glyphs['a'][5]))
				x=copy.copy(ox)
			else:
				# get glyph from dictionary
				g = self.glyphs[c]
				x += scale*g[4]
				y -= scale*g[5]
				# tl
				glTexCoord2f (g[0], g[1])
				glVertex2f (x,y)
				# tr
				glTexCoord2f (g[0]+g[2], g[1])
				glVertex2f (x+scale*g[2], y)
				# br
				glTexCoord2f (g[0]+g[2], g[1]-g[3])
				glVertex2f (x+scale*g[2], y-scale*g[3])
				# bl
				glTexCoord2f (g[0], g[1]-g[3])
				glVertex2f (x, y-scale*g[3])
				# advance to next char and restore any offsets
				if fixed:
					y += scale*g[5]
					x += scale * self.fixed_width
				else:
					y += scale*g[5]
					x += scale*g[6] - scale*g[4]
		glEnd ()
		glDisable (GL_TEXTURE_2D)
			
		



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
	
	glTranslatef (0,0,0.2)
	
	glColor4f (1,1,1,1)
	if PRE_GAME and GAME_STATE<>PAUSED:
		glColor4f (0.4, 0.4, 0.7, 0.1)
		big_font.draw (1,14,"     Build your towers!\nClick START when ready!",12)
		glColor4f (1,1,1,1)
	if GAME_STATE==PAUSED:
		big_font.draw (5, 15, "PAUSED",26)
	if (amouse.over == ID_SLOWTOWER and selected is None) or (deploying and amouse.over>998):	# mouse over slow tower icon
		font.draw (game.map.width + 1, 14, "SLOW TOWER\nCost: "+str(SLOW_TOWER_COST),12)
		font.draw (game.map.width + 1, 11, "Slow firing tower with\nmedium damage to\nboth ground and air\nunits.\n(Hey, it's cheap!)\n\nUpgrades:\nDamage, Range and\neventually firing speed.",12)
	if selected:
		font.draw (game.map.width + 1, 14, selected.label,12)
		font.draw (game.map.width + 1, 12, selected.info_headings,12)
		font.draw (game.map.width + 9, 12, selected.info,12)
		if selected.target_mode:
			glColor4f (1.0, 0.4, 0.4, 1)
			font.draw (game.map.width + 1, 3, "Target: " + ai[selected.target_mode],12)
			glColor4f (1,1,1,1)
	if amouse.over<999 and selected is None:
		font.draw (game.map.width + 1, 14, game.towers[amouse.over].label,12)
		font.draw (game.map.width + 1, 12, game.towers[amouse.over].info_headings,12)
		font.draw (game.map.width + 9, 12, game.towers[amouse.over].info,12)
		if game.towers[amouse.over].target_mode:
			glColor4f (1.0, 0.4, 0.4, 1)
			font.draw (game.map.width + 1, 3, "Target: " + ai[game.towers[amouse.over].target_mode],12)
			glColor4f (1,1,1,1)
	if GAME_STATE<>MAIN_MENU:
		font.draw (0, game.map.height+3, "Score: " + str(game.score),16)
		font.draw (10, game.map.height+3, "Lives: " + str(game.lives),16)
		font.draw (19, game.map.height+3, "Credits: " + str(game.credits),16)
		
	glTranslatef (0,0,-0.2)

		

class aGUI:
	def __init__ (self):
		self.mode = 0	# 0=normal, 1=unit selected, 2=deploying
		self.x=game.map.width + 3
		self.y=game.map.height - 3
		
	def draw (self):
		if PRE_GAME:
			# draw start button
			buttons[ID_START].draw()
		if GAME_STATE==IN_GAME or GAME_STATE==PAUSED:
			# draw pause button
			buttons[ID_PAUSE].draw()
		if selected:
			# if a tower is selected
			# draw sell button
			buttons[ID_SELL].draw()
			if game.credits>=selected.upgrade_cost:
				# draw upgrade button if we have the funds
				buttons[ID_UPGRADE].draw()
			else:
				# draw greyed out upgrade button
				buttons[ID_UPGRADE_NOT_OK].draw()
			# draw ai buttons
			if selected.target_mode:	# > 0 (0 means no AI - for bash towers or rotating beams)
				t = selected.target_mode
				if t==1:
					buttons[ID_AI_FAR_ON].draw()
					buttons[ID_AI_STRONG_OFF].draw()
					buttons[ID_AI_WEAK_OFF].draw()
					buttons[ID_AI_FAST_OFF].draw()
					buttons[ID_AI_SLOW_OFF].draw()
					buttons[ID_AI_NEAR_OFF].draw()
				elif t==2:
					buttons[ID_AI_NEAR_ON].draw()
					buttons[ID_AI_STRONG_OFF].draw()
					buttons[ID_AI_WEAK_OFF].draw()
					buttons[ID_AI_FAST_OFF].draw()
					buttons[ID_AI_SLOW_OFF].draw()
					buttons[ID_AI_FAR_OFF].draw()
				elif t==3:
					buttons[ID_AI_NEAR_OFF].draw()
					buttons[ID_AI_STRONG_ON].draw()
					buttons[ID_AI_WEAK_OFF].draw()
					buttons[ID_AI_FAST_OFF].draw()
					buttons[ID_AI_SLOW_OFF].draw()
					buttons[ID_AI_FAR_OFF].draw()
				elif t==4:
					buttons[ID_AI_NEAR_OFF].draw()
					buttons[ID_AI_STRONG_OFF].draw()
					buttons[ID_AI_WEAK_ON].draw()
					buttons[ID_AI_FAST_OFF].draw()
					buttons[ID_AI_SLOW_OFF].draw()
					buttons[ID_AI_FAR_OFF].draw()
				elif t==5:
					buttons[ID_AI_NEAR_OFF].draw()
					buttons[ID_AI_STRONG_OFF].draw()
					buttons[ID_AI_WEAK_OFF].draw()
					buttons[ID_AI_FAST_ON].draw()
					buttons[ID_AI_SLOW_OFF].draw()
					buttons[ID_AI_FAR_OFF].draw()
				elif t==6:
					buttons[ID_AI_NEAR_OFF].draw()
					buttons[ID_AI_STRONG_OFF].draw()
					buttons[ID_AI_WEAK_OFF].draw()
					buttons[ID_AI_FAST_OFF].draw()
					buttons[ID_AI_SLOW_ON].draw()
					buttons[ID_AI_FAR_OFF].draw()
	
		
		# draw slow tower icon
		glColor4f (0.2,1,0.2,1)
		glPushMatrix()
		glTranslatef (self.x, self.y, 0)
		glCallList (TOWER_BASE_DL)
		glCallList (TOWER_SLOW_DL)
		if game.credits < SLOW_TOWER_COST:
			glColor4f (1,0.2,0.2,0.5)
		else:
			glColor4f (0.2,1,0.2,0.2)
		glBegin (GL_QUADS)
		glVertex3f (-1,-1, 0.01)
		glVertex3f (-1,1, 0.01)
		glVertex3f (1,1, 0.01)
		glVertex3f (1,-1, 0.01)
		glEnd()
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
		
		if PRE_GAME:
			# draw start button
			buttons[ID_START].draw_selection()
		if GAME_STATE==IN_GAME or GAME_STATE==PAUSED:
			# draw pause button
			buttons[ID_PAUSE].draw_selection()
		if selected:
			# if a tower is selected
			# draw sell button
			buttons[ID_SELL].draw_selection()
			if game.credits>=selected.upgrade_cost:
				# draw upgrade button if we have the funds
				buttons[ID_UPGRADE].draw_selection()
			if selected.target_mode:	# > 0 (0 means no AI - for bash towers or rotating beams)
				buttons[ID_AI_STRONG_OFF].draw_selection()
				buttons[ID_AI_WEAK_OFF].draw_selection()
				buttons[ID_AI_FAST_OFF].draw_selection()
				buttons[ID_AI_SLOW_OFF].draw_selection()
				buttons[ID_AI_NEAR_OFF].draw_selection()
				buttons[ID_AI_FAR_OFF].draw_selection()
		
	

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
		self.alpha_sin+=tick*12
		if self.alpha_sin>4.1416:
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
					# OK, draw appropraite tower ready for deploying and have enough to cover cost
					deploying.pos = [x,y]
					if nothing_underneath and game.credits >= deploying.cost:
						deploying.draw(self.alpha)
						glPushMatrix()
						glTranslatef (x, y, 0.1)
						draw_filled_circle (math.sqrt(deploying.range), 0.3, False, self.alpha)
						#glColor4f (1,0.2,0.2,self.alpha)
						draw_circle (math.sqrt(deploying.range), 0.3)
						glPopMatrix()
					else:
						# slowtower - cant build here
						deploying.draw(self.alpha * 0.5)
						glPushMatrix()
						glTranslatef (x, y, 0)
						glLineWidth(4)
						glColor4f (1,0.2,0.2,1)
						glBegin (GL_LINES)
						glVertex3f (-0.6, -0.6, 0.01)
						glVertex3f (0.6, 0.6, 0.01)
						glVertex3f (-0.6, 0.6, 0.01)
						glVertex3f (0.6, -0.6, 0.01)
						glEnd()
						glLineWidth(1)
						glPopMatrix()
		if selected:
			# if a tower is selected, draw it's range
			glPushMatrix()
			glTranslatef (selected.pos[0], selected.pos[1], 0.1)
			draw_filled_circle (math.sqrt(selected.range), 0.3, True)
			glPopMatrix()
				

class aCell:
	def __init__ (self):
		self.entities = []
		self.passable=True
		
		# debug - random maze
		#if random.random() > 0.899:
			#self.passable=False

class aSwarm:
	def __init__(self, type=0, no=10, health=100, time=60, credits=10):
		
		self.type=type
		self.no=no
		self.count=0
		self.health=health
		self.credits=credits
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
					yadda = normalEnemy(route, self.health, self.credits )
					yadda.health=self.health
					game.enemies.append ( yadda )
					self.count+=1
					self.time_since_last_spawn=0
		if self.time < 0:
			# do next wave
			print "Next wave..."
			if game.map.swarms and len(game.map.active_swarms)==1:
				# if this is only current swarm, and still have swarms left, pop next from list onto actives
				game.map.active_swarms.append ( game.map.swarms.pop(0) )
			# remove self from active swarm list
			game.map.active_swarms.remove (self)
			
			
		# else do nothing

class aNode:
	def __init__ (self,pos):
		self.pos=pos
		self.next=None
		self.distance=99999
	
	#for heapq
	def __cmp__(self, other): return cmp(self.distance, other.distance)
			
class aRoute:
	def __init__ (self, start, end, width, height):
		self.start=start
		self.end=end
		self.route={}
		for a in xrange(0,width):
			for b in xrange(0,height):
				self.route[(a,b)]=aNode([a,b])
				
	
	def reset (self):
		for a in xrange(0,game.map.width):
			for b in xrange(0,game.map.height):
				self.route[(a,b)].next=None
				self.route[(a,b)].distance=99999
				
	def recalc (self):
		"""	dijkstra algorithm - works from exit to start fills all reachable nodes in map """
		path_found = False
		self.reset()
		Q = []
		visited = {}
		self.route[(self.end[0],self.end[1])].next=None
		self.route[(self.end[0],self.end[1])].distance=0	# dist to exit (end) node is going to be zero
		# create starting set Q, (binary heap) containing all nodes with exit node set to 0
		heappush (Q, self.route[(self.end[0],self.end[1])] )
		map = game.map
		nb = game.map.get_neighbours
		while Q:
			curnode = heappop (Q)	# pop next nearest node off top of binary heap
			if curnode not in visited:
				visited[curnode]=True
				neighbours = nb (curnode.pos)
				for pos in neighbours:
					if pos == self.start:
						path_found = True
					neighbour_node = self.route[(pos[0],pos[1])]
					if neighbour_node.distance > curnode.distance+1:
						neighbour_node.next = curnode
						neighbour_node.distance = curnode.distance+1
					if neighbour_node not in visited:
						# if neighbour node not already fully processed, stick on priority queue for consideration
						heappush (Q, neighbour_node)
		return path_found
		
	
	
	
	
	def recalc_no_priority (self):
		"""	dijkstra algorithm - works from exit to start fills all reachable nodes in map """
		path_found = False
		self.reset()
		Q = []
		visited = {}
		self.route[(self.end[0],self.end[1])].next=None
		self.route[(self.end[0],self.end[1])].distance=0	# dist to exit (end) node is going to be zero
		# create starting set Q, (binary heap) containing all nodes with exit node set to 0
		Q.append (self.route[(self.end[0],self.end[1])] )
		map = game.map
		nb = game.map.get_neighbours
		distance = 1	# default distance - changed to 1.4 for diagonals
		while Q:
			curnode = Q.pop()	# pop next nearest node off top of binary heap
			if curnode not in visited:
				visited[curnode]=True
				neighbours = nb (curnode.pos)
				for pos in neighbours:
					if pos == self.start:
						path_found = True
					neighbour_node = self.route[(pos[0],pos[1])]
					if pos[0]<>curnode.pos[0] and pos[1]<>curnode.pos[1]:
						distance = 1.4
					else:
						distance = 1
					if neighbour_node.distance > curnode.distance+distance:
						neighbour_node.next = curnode
						neighbour_node.distance = curnode.distance+distance
					if neighbour_node not in visited:
						# if neighbour node not already fully processed, stick on priority queue for consideration
						Q.append (neighbour_node)
		return path_found
		
	def draw (self):
		glBegin (GL_LINES)
		# TODO: change to iterate through dictionary DONE
		for k,r in self.route.items():
			if r.next:
				x = r.pos[0]
				y= r.pos[1]
				xd = (r.next.pos[0]-r.pos[0])/2.2
				yd = (r.next.pos[1]-r.pos[1])/2.2
				glColor4f (0.2, 0.2, 1, 0.5)
				glVertex2f (x+0.5, y+0.5)
				glColor4f (0.8, 0.8, 1, 1)
				glVertex2f (x+0.5+xd, y+0.5+yd)
		glEnd()
		
		
class aSell:
	def __init__ (self, x, y, time):
		self.x = copy.copy(x)
		self.y = copy.copy(y)
		self.time=time
		self.time_alive=0
		self.scale = 1.6 / time
		
	def update(self,dt):
		self.time_alive+=dt
		if self.time_alive>self.time:
			# sale complete - update map and recalc routes
			game.towers.remove (self)
			game.map.cell[self.x][self.y].passable=True
			game.map.cell[self.x-1][self.y].passable=True
			game.map.cell[self.x-1][self.y-1].passable=True
			game.map.cell[self.x][self.y-1].passable=True
			for route in game.map.routes:
				route.recalc_no_priority()
			
	def draw_selection (self):
		# no need for mouse detection
		pass
			
	def draw(self):
		glColor4f (0.2,1,0.2,1)
		glPushMatrix()
		glTranslatef (self.x, self.y, 0)
		glColor4f (1,1,1,1)
		glBegin(GL_LINES)
		glVertex3f (-0.8,0,0.1)
		glVertex3f (0.8 - (self.time_alive * self.scale),0,0.1)
		glEnd()
		glCallList (TOWER_BASE_DL)
		glPopMatrix()
			


			
class anUpgrade:
	def __init__ (self, x, y, time, next_tower):
		self.pos = [x,y]
		self.time=time
		self.time_alive=0
		self.scale = 1.6 / time
		self.next_tower = next_tower
		
	def update(self,dt):
		self.time_alive+=dt
		if self.time_alive>self.time:
			# upgrade complete
			game.towers.append (self.next_tower)
			game.towers.remove (self)
			
	def draw_selection (self):
		# no need for mouse detection
		pass
			
	def draw(self):
		glColor4f (0.2,1,0.2,1)
		glPushMatrix()
		glTranslatef (self.pos[0], self.pos[1], 0)
		glColor4f (1,1,1,1)
		glBegin(GL_LINES)
		glVertex3f (-0.8,0,0.1)
		glVertex3f (-0.8 + (self.time_alive * self.scale),0,0.1)
		glEnd()
		glCallList (TOWER_BASE_DL)
		glPopMatrix()
			
class aMap:
	def __init__ (self, x, y, game):
		# create 2d array of Cells
		self.cell = []
		self.width = x
		self.height = y
		self.current_swarm=0
		
		self.swarms = []	# type, number of critters, health of each critter, time till next swarm, credits per kill
		self.swarms.append ( aSwarm (0, 5, 10, 10, 1) )
		self.swarms.append ( aSwarm (0, 10, 15, 10, 1) )
		self.swarms.append ( aSwarm (0, 15, 15, 20, 1) )
		self.swarms.append ( aSwarm (0, 20, 20, 20, 1) )
		self.swarms.append ( aSwarm (0, 20, 40, 20, 1) )
		self.swarms.append ( aSwarm (0, 20, 60, 30, 1) )
		self.swarms.append ( aSwarm (0, 20, 80, 30, 1) )
		self.swarms.append ( aSwarm (0, 30, 90, 30, 2) )
		self.swarms.append ( aSwarm (0, 30, 100, 40, 3) )
		self.swarms.append ( aSwarm (0, 30, 120, 40, 4) )
		self.swarms.append ( aSwarm (0, 40, 150, 50, 5) )
		
		
		self.routes=[]
		self.routes.append ( aRoute([0,y/2],[x-1,y/2],x,y) )
		self.routes.append ( aRoute([x/2,y-1],[x/2,0],x,y) )
		
		
		# create map
		for a in xrange(0,x):
			row=[]
			for b in xrange(0,y):
				row.append ( aCell() )
			self.cell.append ( row )
			
		
			
		# TEMPORARY WALLS - TODO: implement custom map loading
		for a in range(x):
			if a < (x/2)-4 or a > (x/2)+3:
				self.cell[a][0].passable = False
				self.cell[a][y-1].passable = False
		for a in range(y):
			if a < (y/2)-3 or a > (y/2)+2:
				self.cell[0][a].passable = False
				self.cell[x-1][a].passable = False
		
		self.create_display_list(game)
		
		
	def swarm_update (self, tick):
		if self.active_swarms:
			for swarm in self.active_swarms:
				swarm.update(tick)
			
	def create_display_list (self, game):
		glNewList(1,GL_COMPILE)
		# QUAD
		#glColor4f (0.6,0.6,1,0.1)
		glColor4f (1,1,1,0.5)
		glEnable (GL_TEXTURE_2D)
		glBindTexture (GL_TEXTURE_2D, 24)
		glBegin (GL_QUADS)
		glTexCoord2f (0,0)
		glVertex3f (0,0,-0.001)
		glTexCoord2f (1,0)
		glVertex3f (self.width,0,-0.001)
		glTexCoord2f (1,1)
		glVertex3f (self.width,self.height,-0.001)
		glTexCoord2f (0,1)
		glVertex3f (0,self.height,-0.001)
		glEnd()
		glDisable (GL_TEXTURE_2D)
		
		# GRID
		#glColor4f (1,1,1,0.01)
		#glLineWidth(1)
		#glBegin (GL_LINES)
		#for x in range (0,self.width+1):
		#	glVertex2f (x,0)
		#	glVertex2f (x,self.height)
		#for y in range (0,self.height+1):
		#	glVertex2f (0,y)
		#	glVertex2f (self.width,y)
		#glEnd()
		
		# WALLS
		glColor4f (1,1,1,0.2)
		glBegin (GL_QUADS)
		for x in range (0,self.width):
			for y in range (0,self.height):
				if self.cell[x][y].passable != True:
					glVertex3f (x,y, 0.002)
					glVertex3f (x, y+1, 0.002)
					glVertex3f (x+1, y+1, 0.002)
					glVertex3f (x+1, y, 0.002)
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
		self.label = "SLOW TOWER - LVL 1"
		self.highlight = False
		self.pos = position
		self.direction = 0
		self.active = True
		self.target = None
		self.cost = SLOW_TOWER_COST
		self.range = SLOW_TOWER_RANGE
		self.range_sq = SLOW_TOWER_RANGE_SQ
		self.upgrade_cost = SLOW_TOWER_UPGRADE_COST
		self.upgrade_time = SLOW_TOWER_UPGRADE_TIME
		self.damage_per_shot = SLOW_TOWER_DAMAGE
		self.sell_price = SLOW_TOWER_SELL_PRICE
		self.time_between_shots = 1.2
		self.time_since_last_shot = 3
		self.target_mode = 2	# 1=nearest end of path 2=nearest 3=strongest 4=strongest  5=fastest 6=slowest 0 = no AI
		self.upgradeable = True
		self.info_headings = "Range:\nDamage:\nRate:\n\nUpgrade for:\nSell for:"
		self.info = str(self.range_sq) + "\n" + str(self.damage_per_shot) + "\n" + str(self.time_between_shots) + "\n\n" + str(self.upgrade_cost) + "\n" + str(self.sell_price)
		
	def sell (self):
		global selected
		selected=None
		if PRE_GAME:
			# take no time
			game.towers.append ( aSell (self.pos[0],self.pos[1], 0.01) )
			# and free
			game.credits += self.cost
		else:
			game.towers.append ( aSell (self.pos[0],self.pos[1], SELL_TIME) )
			game.credits += self.sell_price
		game.towers.remove (self)
		
	def upgrade (self):
		# take upgrade time from selected tower
		game.credits-=self.upgrade_cost
		pos=copy.copy(self.pos)
		upgrade_to = self.get_upgrade()
		if PRE_GAME:
			self.upgrade_time = 0.01
		game.towers.append ( anUpgrade (pos[0], pos[1], self.upgrade_time, upgrade_to) )
		game.towers.remove( self )
		global selected
		selected=None
	
	def get_upgrade(self):
		return slowTower2 (copy.copy(self.pos))
		
	def update (self,dt):
		self.time_since_last_shot+=dt
		if self.time_since_last_shot > self.time_between_shots:
			# find a new target
			nearby_enemies=[]
			for enemy in game.enemies:
				# get squared distance
				sd = (self.pos[0]-enemy.pos[0])**2 + (self.pos[1]-enemy.pos[1])**2
				if sd < self.range:
					nearby_enemies.append ((enemy, sd, enemy.get_path_distance_left() ))	# create list of enemy, dist, and path length remaining
			if nearby_enemies:
				if self.target_mode == 1:	# nearest to end of path
					enemy_path_left=99999
					for near_enemy in nearby_enemies:
						if near_enemy[2] < enemy_path_left:
							enemy_path_left=near_enemy[2]
							self.target = near_enemy[0]	
				elif self.target_mode == 2:	# nearest to tower
					closest=99999
					for near_enemy in nearby_enemies:
						if near_enemy[1] < closest:
							closest = near_enemy[1]
							self.target = near_enemy[0]
				elif self.target_mode == 3:	# strongest
					strongest=-1
					for near_enemy in nearby_enemies:
						if near_enemy[0].health > strongest:
							strongest = near_enemy[0].health
							self.target = near_enemy[0]
				elif self.target_mode == 4:	# weakest
					strongest=99999
					for near_enemy in nearby_enemies:
						if near_enemy[0].health < strongest:
							strongest = near_enemy[0].health
							self.target = near_enemy[0]
				elif self.target_mode == 5:	# fastest
					fastest=0
					for near_enemy in nearby_enemies:
						if near_enemy[0].speed > fastest:
							fastest = near_enemy[0].speed
							self.target = near_enemy[0]
				elif self.target_mode == 6:	# slowest
					fastest=99999
					for near_enemy in nearby_enemies:
						if near_enemy[0].speed < fastest:
							fastest = near_enemy[0].speed
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
					game.projectiles.append (slowBullet (copy.copy(self.pos), self.target, self.damage_per_shot))
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
			
		
		
		
	def draw (self, alpha=1):
		glColor4f (0.2,1,0.2,alpha)
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
		glTranslatef (self.pos[0], self.pos[1], 0)
		scale = (math.sqrt (self.range))
		draw_filled_circle ( scale, 0.3, False)
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


		

class slowTower2:
	def __init__ (self, position):
		self.label = "SLOW TOWER - LVL 2"
		self.highlight = False
		self.pos = position
		self.direction = 0
		self.active = True
		self.target = None
		self.cost = SLOW_TOWER2_COST
		self.range = SLOW_TOWER2_RANGE
		self.range_sq = SLOW_TOWER2_RANGE_SQ
		self.upgrade_cost = SLOW_TOWER2_UPGRADE_COST
		self.upgrade_time = SLOW_TOWER2_UPGRADE_TIME
		self.damage_per_shot = SLOW_TOWER2_DAMAGE
		self.sell_price = SLOW_TOWER2_SELL_PRICE
		self.time_between_shots = 1.2
		self.time_since_last_shot = 3
		self.target_mode = 2	# 1=nearest end of path 2=nearest 3=furthest 4=weakest 5=strongest 
		self.upgradeable = True
		self.info_headings = "Range:\nDamage:\nRate:\n\nUpgrade for:\nSell for:"
		self.info = str(self.range_sq) + "\n" + str(self.damage_per_shot) + "\n" + str(self.time_between_shots) + "\n\n" + str(self.upgrade_cost) + "\n" + str(self.sell_price)
		
		
	def sell (self):
		global selected
		selected=None
		if PRE_GAME:
			# take no time
			game.towers.append ( aSell (self.pos[0],self.pos[1], 0.01) )
			# and free
			game.credits += self.cost
		else:
			game.towers.append ( aSell (self.pos[0],self.pos[1], SELL_TIME) )
			game.credits += self.sell_price
		game.towers.remove (self)
		
	def upgrade (self):
		# take upgrade time from selected tower
		game.credits-=self.upgrade_cost
		pos=copy.copy(self.pos)
		upgrade_to = self.get_upgrade()
		if PRE_GAME:
			self.upgrade_time = 0.01
		game.towers.append ( anUpgrade (pos[0], pos[1], self.upgrade_time, upgrade_to) )
		game.towers.remove( self )
		global selected
		selected=None
	
	def get_upgrade(self):
		return slowTower3 (copy.copy(self.pos))
		
	def update (self,dt):
		self.time_since_last_shot+=dt
		if self.time_since_last_shot > self.time_between_shots:
			# find a new target
			nearby_enemies=[]
			for enemy in game.enemies:
				# get squared distance
				sd = (self.pos[0]-enemy.pos[0])**2 + (self.pos[1]-enemy.pos[1])**2
				if sd < self.range:
					nearby_enemies.append ((enemy, sd, enemy.get_path_distance_left() ))	# create list of enemy, dist, and path length remaining
			if nearby_enemies:
				if self.target_mode == 1:	# nearest to end of path
					enemy_path_left=99999
					for near_enemy in nearby_enemies:
						if near_enemy[2] < enemy_path_left:
							enemy_path_left=near_enemy[2]
							self.target = near_enemy[0]	
				elif self.target_mode == 2:	# nearest to tower
					closest=99999
					for near_enemy in nearby_enemies:
						if near_enemy[1] < closest:
							closest = near_enemy[1]
							self.target = near_enemy[0]
				elif self.target_mode == 3:	# strongest
					strongest=-1
					for near_enemy in nearby_enemies:
						if near_enemy[0].health > strongest:
							strongest = near_enemy[0].health
							self.target = near_enemy[0]
				elif self.target_mode == 4:	# weakest
					strongest=99999
					for near_enemy in nearby_enemies:
						if near_enemy[0].health < strongest:
							strongest = near_enemy[0].health
							self.target = near_enemy[0]
				elif self.target_mode == 5:	# fastest
					fastest=0
					for near_enemy in nearby_enemies:
						if near_enemy[0].speed > fastest:
							fastest = near_enemy[0].speed
							self.target = near_enemy[0]
				elif self.target_mode == 6:	# slowest
					fastest=99999
					for near_enemy in nearby_enemies:
						if near_enemy[0].speed < fastest:
							fastest = near_enemy[0].speed
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
					game.projectiles.append (slowBullet (copy.copy(self.pos), self.target, self.damage_per_shot))
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
				
		
	def draw (self, alpha=1):
		glColor4f (0.7,1,0.2,alpha)
		glPushMatrix()
		glTranslatef (self.pos[0], self.pos[1], 0)
		glCallList (TOWER_BASE_DL)
		glRotatef (-self.direction, 0, 0, 1)
		glCallList (TOWER_SLOW2_DL)
		glPopMatrix()
		glPopMatrix()
		
	def draw_highlight (self):
		glColor4f (1,0.2,0.2,1)
		glPushMatrix()
		glTranslatef (self.pos[0], self.pos[1], 0)
		scale = (math.sqrt (self.range))
		draw_filled_circle ( scale, 0.3, False)
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
		
		
		
		
class slowTower3:
	def __init__ (self, position):
		self.label = "SLOW TOWER - LVL 3"
		self.highlight = False
		self.pos = position
		self.direction = 0
		self.active = True
		self.target = None
		self.cost = SLOW_TOWER3_COST
		self.range = SLOW_TOWER3_RANGE
		self.range_sq = SLOW_TOWER3_RANGE_SQ
		self.upgrade_cost = SLOW_TOWER3_UPGRADE_COST
		self.upgrade_time = SLOW_TOWER3_UPGRADE_TIME
		self.damage_per_shot = SLOW_TOWER3_DAMAGE
		self.sell_price = SLOW_TOWER3_SELL_PRICE
		self.time_between_shots = 1.2
		self.time_since_last_shot = 3
		self.target_mode = 2	# 1=nearest end of path 2=nearest 3=furthest 4=weakest 5=strongest 
		self.upgradeable = True
		self.info_headings = "Range:\nDamage:\nRate:\n\nUpgrade for:\nSell for:"
		self.info = str(self.range_sq) + "\n" + str(self.damage_per_shot) + "\n" + str(self.time_between_shots) + "\n\n" + str(self.upgrade_cost) + "\n" + str(self.sell_price)
		
		
	def sell (self):
		global selected
		selected=None
		if PRE_GAME:
			# take no time
			game.towers.append ( aSell (self.pos[0],self.pos[1], 0.01) )
			# and free
			game.credits += self.cost
		else:
			game.towers.append ( aSell (self.pos[0],self.pos[1], SELL_TIME) )
			game.credits += self.sell_price
		game.towers.remove (self)
		
	def upgrade (self):
		# take upgrade time from selected tower
		game.credits-=self.upgrade_cost
		pos=copy.copy(self.pos)
		upgrade_to = self.get_upgrade()
		if PRE_GAME:
			self.upgrade_time = 0.01
		game.towers.append ( anUpgrade (pos[0], pos[1], self.upgrade_time, upgrade_to) )
		game.towers.remove( self )
		global selected
		selected=None
	
	def get_upgrade(self):
		return slowTower3 (copy.copy(self.pos))
		
	def update (self,dt):
		self.time_since_last_shot+=dt
		if self.time_since_last_shot > self.time_between_shots:
			# find a new target
			nearby_enemies=[]
			for enemy in game.enemies:
				# get squared distance
				sd = (self.pos[0]-enemy.pos[0])**2 + (self.pos[1]-enemy.pos[1])**2
				if sd < self.range:
					nearby_enemies.append ((enemy, sd, enemy.get_path_distance_left() ))	# create list of enemy, dist, and path length remaining
			if nearby_enemies:
				if self.target_mode == 1:	# nearest to end of path
					enemy_path_left=99999
					for near_enemy in nearby_enemies:
						if near_enemy[2] < enemy_path_left:
							enemy_path_left=near_enemy[2]
							self.target = near_enemy[0]	
				elif self.target_mode == 2:	# nearest to tower
					closest=99999
					for near_enemy in nearby_enemies:
						if near_enemy[1] < closest:
							closest = near_enemy[1]
							self.target = near_enemy[0]
				elif self.target_mode == 3:	# strongest
					strongest=-1
					for near_enemy in nearby_enemies:
						if near_enemy[0].health > strongest:
							strongest = near_enemy[0].health
							self.target = near_enemy[0]
				elif self.target_mode == 4:	# weakest
					strongest=99999
					for near_enemy in nearby_enemies:
						if near_enemy[0].health < strongest:
							strongest = near_enemy[0].health
							self.target = near_enemy[0]
				elif self.target_mode == 5:	# fastest
					fastest=0
					for near_enemy in nearby_enemies:
						if near_enemy[0].speed > fastest:
							fastest = near_enemy[0].speed
							self.target = near_enemy[0]
				elif self.target_mode == 6:	# slowest
					fastest=99999
					for near_enemy in nearby_enemies:
						if near_enemy[0].speed < fastest:
							fastest = near_enemy[0].speed
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
					game.projectiles.append (slowBullet (copy.copy(self.pos), self.target, self.damage_per_shot))
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
				
		
	def draw (self, alpha=1):
		glColor4f (0.7,1,0.2,alpha)
		glPushMatrix()
		glTranslatef (self.pos[0], self.pos[1], 0)
		glCallList (TOWER_BASE_DL)
		glRotatef (-self.direction, 0, 0, 1)
		glCallList (TOWER_SLOW3_DL)
		glPopMatrix()
		glPopMatrix()
		
	def draw_highlight (self):
		glColor4f (1,0.2,0.2,1)
		glPushMatrix()
		glTranslatef (self.pos[0], self.pos[1], 0)
		scale = (math.sqrt (self.range))
		draw_filled_circle ( scale, 0.3, False)
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
	""" normal enemy class.  takes:  route, health, credits """
	def __init__ (self, route=None, health = 10, credits = 5):
		self.pos=[0,0]
		self.pos[0]=route.start[0]+0.5
		self.pos[1]=route.start[1]+0.5
		self.route = route
		self.diag = False
		self.health = health
		self.credits = credits
		self.alive = True
		self.dir = RIGHT
		self.speed = 1.7
		self.next_position = copy.copy(self.route.route[(int(self.pos[0]),int(self.pos[1]))].next.pos)
		self.next_position[0] += 0.5
		self.next_position[1] += 0.5
		if abs(self.pos[0]-self.next_position[0]) > 0.6 and abs(self.pos[1]-self.next_position[1]) > 0.6:
			self.diag = True
		else:
			self.diag = False
		
	def draw (self):
		glPushMatrix()
		glTranslatef (self.pos[0], self.pos[1], 0.1)
		glCallList (ENEMY_NORMAL_DL)
		glPopMatrix()
		
	def get_current_grid_pos (self):
		return [ int(self.pos[0]), int(self.pos[1]) ]
		
	def get_path_distance_left (self):
		gridpos = self.get_current_grid_pos ()
		return self.route.route[(gridpos[0],gridpos[1])].distance

	def update (self, tick):
		if self.health<0:
			# I`m dead
			# do other cleanup jobs and spawn whatever necessary particles
			game.particles.append (particle_explosion(self.pos))
			self.alive = False
			game.score += 200
			game.credits += self.credits
			game.enemies.remove (self)
			return 0
		if abs(self.pos[0]-self.next_position[0]) < 0.1 and abs(self.pos[1]-self.next_position[1]) < 0.1:
			# get next path position
			if self.route.route[(int(self.pos[0]),int(self.pos[1]))].next:
				self.next_position = copy.copy(self.route.route[(int(self.pos[0]),int(self.pos[1]))].next.pos)
				self.next_position[0] += 0.5
				self.next_position[1] += 0.5
				if abs(self.pos[0]-self.next_position[0]) > 0.6 and abs(self.pos[1]-self.next_position[1]) > 0.6:
					self.diag = True
				else:
					self.diag = False
			else:
				# end of path
				# job done - update all
				self.alive = False
				game.enemies.remove (self)
				game.lives-=1
		
		
			
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
		
		
		



		
def manhattan (a, b):
	return abs(a[0]-b[0]) + abs(a[1]-b[1])
		
		

			
	
		
			
		
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
		self.credits = 100
		self.lives = 20
		
	def create_tower_display_lists (self):
		# TOWER BASE 1
		glNewList(TOWER_BASE_DL, GL_COMPILE)
		glColor4f (1,1,1,1)
		glEnable (GL_TEXTURE_2D)
		glBindTexture (GL_TEXTURE_2D, 20)
		glBegin (GL_QUADS)
		glTexCoord2f (0,0)
		glVertex2f (-1,-1)
		glTexCoord2f (1,0)
		glVertex2f (1,-1)
		glTexCoord2f (1,1)
		glVertex2f (1,1)
		glTexCoord2f (0,1)
		glVertex2f (-1,1)
		glEnd ()
		glDisable (GL_TEXTURE_2D)
		glEndList()
		
		# SLOW TOWER LVL 1
		glNewList(TOWER_SLOW_DL,GL_COMPILE)
		# turret
		glColor4f (1,1,1,1)
		glEnable (GL_TEXTURE_2D)
		glBindTexture (GL_TEXTURE_2D, 21)
		glBegin (GL_QUADS)
		glTexCoord2f (0,0)
		glVertex3f (-1,-1, 0.01)
		glTexCoord2f (1,0)
		glVertex3f (1,-1, 0.01)
		glTexCoord2f (1,1)
		glVertex3f (1,1, 0.01)
		glTexCoord2f (0,1)
		glVertex3f (-1,1, 0.01)
		glEnd ()
		glDisable (GL_TEXTURE_2D)
		glEndList()
		
		# SLOW TOWER LVL 2
		glNewList(TOWER_SLOW2_DL,GL_COMPILE)
		# turret
		glColor4f (1,1,1,1)
		glEnable (GL_TEXTURE_2D)
		glBindTexture (GL_TEXTURE_2D, 22)
		glBegin (GL_QUADS)
		glTexCoord2f (0,0)
		glVertex3f (-1.3,-1.3, 0.01)
		glTexCoord2f (1,0)
		glVertex3f (1.3,-1.3, 0.01)
		glTexCoord2f (1,1)
		glVertex3f (1.3,1.3, 0.01)
		glTexCoord2f (0,1)
		glVertex3f (-1.3,1.3, 0.01)
		glEnd ()
		glDisable (GL_TEXTURE_2D)
		glEndList()
		
		# SLOW TOWER LVL 3
		glNewList(TOWER_SLOW3_DL,GL_COMPILE)
		# turret
		glColor4f (1,1,1,1)
		glEnable (GL_TEXTURE_2D)
		glBindTexture (GL_TEXTURE_2D, 23)
		glBegin (GL_QUADS)
		glTexCoord2f (0,0)
		glVertex3f (-1.5,-1.5, 0.01)
		glTexCoord2f (1,0)
		glVertex3f (1.5,-1.5, 0.01)
		glTexCoord2f (1,1)
		glVertex3f (1.5,1.5, 0.01)
		glTexCoord2f (0,1)
		glVertex3f (-1.5,1.5, 0.01)
		glEnd ()
		glDisable (GL_TEXTURE_2D)
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
		for route in self.map.routes:
			route.recalc()
		
	def recalc_camera (self,x,y):
		self.camera_height = -(max(x, y)) * 0.99
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
		self.u = False
keybstate = aKeybstate()	# GLOBAL keyboard state 





@window.event
def on_draw():

	if ZOOMED:
		if game.camera_x<-14:
			game.camera_x *= 0.98
			game.camera_height *= 0.982
	else:
		if game.camera_x>-20:
			game.camera_x *= 1.02
			game.camera_height *= 1.018
					
	glMatrixMode (GL_MODELVIEW)
	glLoadIdentity()
	window.clear()
	do_selection()
	
	# DRAW MAP PLUS ENTITIES	
	# move camera
	
	glTranslatef ( game.camera_x, game.camera_y, game.camera_height )
	
	
	
	if GAME_STATE==PAUSED:
		glColor4f (1,1,1,0.2)
		glBegin (GL_QUADS)
		glVertex3f (-50,-50,-1)
		glVertex3f (-50,50,-1)
		glVertex3f (50,50,-1)
		glVertex3f (50,-50,-1)
		glEnd()
	game.gui.draw()
	game.map.draw()
	
	if keybstate.space and GAME_STATE==IN_GAME:
		for route in game.map.routes:
			route.draw()
	glTranslatef (0,0,0.03)
	for enemy in game.enemies:
		enemy.draw()
	glDisable (GL_DEPTH_TEST)
	for tower in game.towers:
		tower.draw()
	glEnable (GL_DEPTH_TEST)
	if keybstate.tab:
		for tower in game.towers:
			tower.draw_highlight()
	if amouse.over < 999:
		game.towers[amouse.over].draw_highlight()
	glTranslatef (0,0,0.1)
	for proj in game.projectiles:
		proj.draw()
	for part in game.particles:
		part.draw()
	amouse.draw()
	draw_text()
	#print_number (0,-2,1234567890123876876435, 2)
	
	
		
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
	
	
	
	
		
	
	
def key_handler ():
	if keybstate.w: 
		keybstate.w=False
		print "Toggling paused state..."
		global GAME_STATE
		if GAME_STATE==IN_GAME:
			GAME_STATE=PAUSED
		else:
			GAME_STATE=IN_GAME
	if keybstate.s: 
		keybstate.s=False
		if selected:
			selected.sell()
	if keybstate.u:
		keybstate.u=False
		if selected and game.credits>=selected.upgrade_cost:
			selected.upgrade()
	if keybstate.up:
		game.camera_x += 0.075
		game.camera_height += 0.1
		print game.camera_x, "   ", game.camera_height
	if keybstate.down:
		game.camera_x -= 0.075
		game.camera_height -= 0.1
			
	
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
	if symbol==key.DOWN:
		keybstate.down = True
	if symbol==key.LSHIFT:
		keybstate.shift = True
	if symbol==key.TAB:
		keybstate.tab = True
	if symbol==key.T:
		keybstate.t = True
	if symbol==key.U:
		keybstate.y = True
	

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
	if symbol==key.DOWN:
		keybstate.down = False
	if symbol==key.LSHIFT:
		keybstate.shift = False
	if symbol==key.TAB:
		keybstate.tab = False
	if symbol==key.T:
		keybstate.t = False
	if symbol==key.U:
		keybstate.u = True

			
@window.event
def on_mouse_motion (x,y,dx,dy):
	global amouse
	amouse.x = x
	amouse.y = y
	
@window.event
def on_mouse_release (x,y,buttons,modifiers):
	if buttons & mouse.MIDDLE:
		global ZOOMED
		if ZOOMED:
			ZOOMED=False
		else:
			ZOOMED=True
		
	print "CLICKED ON " + str(amouse.over)
	if buttons and GAME_STATE==PAUSED:
		global GAME_STATE
		GAME_STATE=IN_GAME
		return
	if buttons & mouse.LEFT and GAME_STATE==IN_GAME:
		# left clicked on something - see what mouse is over
		if amouse.over > 999 and amouse.over<9999:
			# clicked on gui element
			if amouse.over==1000:
				#clicked on slowtower icon
				print "Ready to deploy tower..."
				deploying=slowTower([0,0])
				selected=None # unselect any selected tower
			if amouse.over==ID_SELL:
				selected.sell()
			if amouse.over==1100:
				#clicked on upgrade button (not greyed out)
				selected.upgrade()
			if amouse.over==ID_AI_FAST_OFF:
				selected.target_mode = 5
			if amouse.over==ID_AI_SLOW_OFF:
				selected.target_mode = 6
			if amouse.over==ID_AI_STRONG_OFF:
				selected.target_mode = 3
			if amouse.over==ID_AI_WEAK_OFF:
				selected.target_mode = 4
			if amouse.over==ID_AI_NEAR_OFF:
				selected.target_mode = 2
			if amouse.over==ID_AI_FAR_OFF:
				selected.target_mode = 1
					
		if amouse.over==ID_PAUSE:
			global GAME_STATE
			GAME_STATE=PAUSED
			
		if amouse.over==ID_START:
			if PRE_GAME:
				global PRE_GAME
				PRE_GAME=False
				game.map.active_swarms=[ game.map.swarms.pop(0) ]

		if amouse.over < 999:
			# clicked on tower
			global selected
			selected = game.towers[amouse.over]
			global deploying
			deploying=None
			print "Selected a tower."
			
		if amouse.over == 999:
			# clicked on map
			if not deploying:
				# just cancel stuff
				selected=None
			if deploying and amouse.deployable and game.credits >= deploying.cost:
				# have something to deploy and am able to deploy
				x=int(amouse.map_x+0.5)
				y=int(amouse.map_y+0.5)
				game.map.cell[x][y].passable=False
				game.map.cell[x-1][y].passable=False
				game.map.cell[x-1][y-1].passable=False
				game.map.cell[x][y-1].passable=False
				
				
				# recalc routes
				valid=True
				
				for route in game.map.routes:
					#if not route.recalc_no_priority():
					if not route.recalc_no_priority():
						valid=False
						break
				if not valid:
					# reverse placement and exit function, recalc routes
					print "Invalid path"
					game.map.cell[x][y].passable=True
					game.map.cell[x-1][y].passable=True
					game.map.cell[x-1][y-1].passable=True
					game.map.cell[x][y-1].passable=True
					for route in game.map.routes:
						#route.recalc_no_priority()
						route.recalc_no_priority()
					return False
						
				
				# add to game list
				game.towers.append ( deploying )
				# create new tower ready to deploy
				#deploying=slowTower([0,0])	# TODO - get this to create the appropriate type/class
				deploying= copy.copy (deploying)
				# reduce credits by cost
				game.credits -= deploying.cost
				
				# tidy up
					
			
	if buttons & mouse.RIGHT and GAME_STATE<>PAUSED:
		# right clicked while not paused
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
	glAlphaFunc ( GL_GREATER, 0.1 )
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
	
def draw_filled_circle (r,i, outline=True, alpha=1):
	angle=0
	glColor4f (1,0.2,0.2,0.1*alpha)
	glBegin (GL_TRIANGLE_FAN)
	glVertex2f (0,0)	# first vert in centre
	while angle<=i+(math.pi*2):
		glVertex2f (math.cos(angle)*r, math.sin(angle)*r)
		angle+=i
	glEnd()
	
	if outline:
		glColor4f (1,0.2,0.2,alpha)
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
	if GAME_STATE==IN_GAME or GAME_STATE==PAUSED:
		
		for particle in game.particles:
			particle.update (dt)	# done before check of game state because particles are frame rate dependant for speed purposes
		if GAME_STATE==PAUSED:
			dt = 0
		amouse.update (dt)
		if not PRE_GAME:
			game.map.swarm_update (dt)
		for tower in game.towers:
			tower.update (dt)
		for enemy in game.enemies:
			enemy.update(dt)
		for proj in game.projectiles:
			proj.update(dt)
	key_handler()
	#print mouse.over #debug
	

	
# MAIN CODE

# load textures
upgrade_button_image = pyglet.image.load ('upgrade_ok.png')
texture = upgrade_button_image.get_mipmapped_texture()
upgrade_grey_button_image = pyglet.image.load ('upgrade_not_ok.png')
texture = upgrade_grey_button_image.get_mipmapped_texture()
sell_button_image = pyglet.image.load ('sell_ok.png')
texture = sell_button_image.get_mipmapped_texture()
pause_button_image = pyglet.image.load ('pause.png')
texture = pause_button_image.get_mipmapped_texture()
start_button_image = pyglet.image.load ('start.png')
texture = start_button_image.get_mipmapped_texture()
ai1 = pyglet.image.load ('ai_strong_off.png')
texture = ai1.get_mipmapped_texture()
ai2 = pyglet.image.load ('ai_weak_off.png')
texture = ai2.get_mipmapped_texture()
ai3 = pyglet.image.load ('ai_fast_off.png')
texture = ai3.get_mipmapped_texture()
ai4 = pyglet.image.load ('ai_slow_off.png')
texture = ai4.get_mipmapped_texture()
ai5 = pyglet.image.load ('ai_near_off.png')
texture = ai5.get_mipmapped_texture()
ai6 = pyglet.image.load ('ai_far_off.png')
texture = ai6.get_mipmapped_texture()
ai7 = pyglet.image.load ('ai_strong_on.png')
texture = ai7.get_mipmapped_texture()
ai8 = pyglet.image.load ('ai_weak_on.png')
texture = ai8.get_mipmapped_texture()
ai9 = pyglet.image.load ('ai_fast_on.png')
texture = ai9.get_mipmapped_texture()
ai10 = pyglet.image.load ('ai_slow_on.png')
texture = ai10.get_mipmapped_texture()
ai11 = pyglet.image.load ('ai_near_on.png')
texture = ai11.get_mipmapped_texture()
ai12 = pyglet.image.load ('ai_far_on.png')
texture = ai12.get_mipmapped_texture()

buttons[ID_UPGRADE]=button(29, 0, 5, 1.2, ID_UPGRADE, 1)
buttons[ID_UPGRADE_NOT_OK]=button(29, 0, 5, 1.2, ID_UPGRADE, 2)
buttons[ID_SELL]=button(35, 0, 5, 1.2, ID_SELL, 3)
buttons[ID_PAUSE]=button(35, 25, 3.5, 1.5, ID_PAUSE, 4)
buttons[ID_START]=button(30, 25, 3.5, 1.5, ID_START, 5)
buttons[ID_AI_STRONG_OFF]=	button(29, 3, 1.6, 1.6, ID_AI_STRONG_OFF, 6)
buttons[ID_AI_WEAK_OFF]=	button(31, 3, 1.6, 1.6, ID_AI_WEAK_OFF, 7)
buttons[ID_AI_FAST_OFF]=	button(33, 3, 1.6, 1.6, ID_AI_FAST_OFF, 8)
buttons[ID_AI_SLOW_OFF]=	button(35, 3, 1.6, 1.6, ID_AI_SLOW_OFF, 9)
buttons[ID_AI_NEAR_OFF]=	button(37, 3, 1.6, 1.6, ID_AI_NEAR_OFF, 10)
buttons[ID_AI_FAR_OFF]=		button(39, 3, 1.6, 1.6, ID_AI_FAR_OFF, 11)
buttons[ID_AI_STRONG_ON]=	button(29, 3, 1.6, 1.6, ID_AI_STRONG_ON, 12)
buttons[ID_AI_WEAK_ON]=		button(31, 3, 1.6, 1.6, ID_AI_WEAK_ON, 13)
buttons[ID_AI_FAST_ON]=		button(33, 3, 1.6, 1.6, ID_AI_FAST_ON, 14)
buttons[ID_AI_SLOW_ON]=		button(35, 3, 1.6, 1.6, ID_AI_SLOW_ON, 15)
buttons[ID_AI_NEAR_ON]=		button(37, 3, 1.6, 1.6, ID_AI_NEAR_ON, 16)
buttons[ID_AI_FAR_ON]=		button(39, 3, 1.6, 1.6, ID_AI_FAR_ON, 17)

font=bitmap_font('test',18)
big_font=bitmap_font('test2',19)

tower_base_texture = pyglet.image.load ('base.png')
texture = tower_base_texture.get_texture()
slow_tower_turret = pyglet.image.load ('slow_tower_turret.png')
texture = slow_tower_turret.get_texture()
slow_tower_turret2 = pyglet.image.load ('slow_tower_turret2.png')
texture = slow_tower_turret2.get_texture()
slow_tower_turret3 = pyglet.image.load ('slow_tower_turret4.png')
texture = slow_tower_turret3.get_texture()
bg = pyglet.image.load ('hubble.jpg')
texture = bg.get_texture()

import psyco
psyco.full()
#psyco.bind(aPath)

game = aGame()
amouse = aMouse()

game.create_level (28,24,game)
game.gui = aGUI()



	
	
pyglet.clock.schedule_interval(update,1/60.)	
pyglet.app.run()