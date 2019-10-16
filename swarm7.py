# TODO: wrap all sprite blits (especially enemy and particles) into display list calls + gltranslates for speed - about 60% faster then plain blit(x,y)


try:
	pass
	#import psyco
	#from psyco.classes import *
except:
	# no psyco - hope you have a nice cpu ;)
	print "No psyco..."


#psyco.full()

from heapq import heappush, heappop
import math
import operator
import pyglet
import sys
pyglet.options['debug_gl'] = False	# TURN ON FOR DEBUGGIN GL!!!
import random
from pyglet.window import key
from pyglet.window import mouse
from pyglet import resource
from pyglet.gl import *
from pyglet import clock
import copy



#FONT_NAME = 'Saved By Zero'
FONT_NAME = 'Arial'
audio = None


#window.set_minimum_size (width=1024, height=768)

#
#	LOAD TEXTURES AND TEXTURE FUNCTIONS
#

sprite_atlas = pyglet.image.atlas.TextureAtlas (width=2048, height=2048)
batch = pyglet.graphics.Batch()	# not used
resource.path.append('res')
resource.reindex()

def tex_border (tex):
	""" takes a pyglet texture/region and insets the texture coordinates by half a texel
		allowing for sub-pixel blitting without interpolation with nearby regions within 
		same texture atlas """
	coord_width = tex.tex_coords[3] - tex.tex_coords[0]
	coord_height = tex.tex_coords[4] - tex.tex_coords[1]
	x_adjust = (coord_width / tex.width) / 2.0	# get tex coord half texel width
	y_adjust = (coord_height / tex.height) / 2.0	# get tex coord half texel width
	# create new 12-tuple texture coordinate
	tex.tex_coords = ( 	tex.tex_coords[0]+x_adjust, tex.tex_coords[1]+y_adjust, 0,
						tex.tex_coords[3]-x_adjust, tex.tex_coords[4]+y_adjust, 0,
						tex.tex_coords[6]-x_adjust, tex.tex_coords[7]-y_adjust, 0,
						tex.tex_coords[9]+x_adjust, tex.tex_coords[10]-y_adjust, 0)
						


def sprite_load (filename, trim=False):
	""" takes a filename, loads it as a pyglet image, adds it to the atlas
	optionally trims the atlas image for clean sub-pixel rendering.  also sets anchor
	to centre of image """
	pic = pyglet.image.load (filename)
	tex = sprite_atlas.add (pic)
	tex.anchor_x = pic.width / 2
	tex.anchor_y = pic.height / 2
	if trim:
		tex_border (tex)
	return tex

pointer_image = resource.image('pointer.png')
pointer_image.anchor_x = pointer_image.width // 2
pointer_image.anchor_y = pointer_image.height // 2
pointer_image_flip = resource.image('pointer.png', flip_x=True)

small_red_bug_tex = sprite_load ('roomba_medium.png', True)
roomba_boss_tex = sprite_load ('roomba_boss.png', True)
fast_tex = sprite_load ('fast.png', True)
jet_sprite = sprite_load ('jet.png',True)
jet_shadow_sprite = sprite_load ('jet_shadow.png', True)
valid_placement_pic = pyglet.image.load('valid_placement.png')
valid_placement_tex = sprite_atlas.add (valid_placement_pic)
selected_pic = pyglet.image.load('selected.png')
selected_tex = sprite_atlas.add (selected_pic)
money_tex = sprite_load ('money.png')
invalid_placement_tex = sprite_load ('invalid_placement.png')
cannon_1_base_pic = pyglet.image.load('cannon_1_base.png')
cannon_1_base_sprite = sprite_atlas.add (cannon_1_base_pic)
cannon_2_base_pic = pyglet.image.load('cannon_2_base.png')
cannon_2_base_sprite = sprite_atlas.add (cannon_2_base_pic)
cannon_3_base_pic = pyglet.image.load('cannon_3_base.png')
cannon_3_base_sprite = sprite_atlas.add (cannon_3_base_pic)
cannon_1_turret_sprite = sprite_load ('cannon_1_turret.png',True)
cannon_2_turret_sprite = sprite_load ('cannon_2_turret.png',True)
cannon_3_turret_sprite = sprite_load ('cannon_3_turret.png',True)
berserker_1_turret_sprite = sprite_load ('berserker_1_turret.png',True)
icbm_1_turret_sprite = sprite_load ('icbm_1_turret.png')
temporal_1_turret_sprite = sprite_load ('temporal_1_turret.png')
tesla_1_turret_sprite = sprite_load ('tesla_1_turret.png')
tesla_2_turret_sprite = sprite_load ('tesla_2_turret.png')
aa_1_turret_sprite = sprite_load ('aa_1_turret.png',True)
sell_outline_pic = pyglet.image.load ('sell_outline.png')
sell_outline_sprite = sprite_atlas.add (sell_outline_pic)
bullet_1_sprite = sprite_load ('bullet_1.png')
bullet_2_sprite = sprite_load ('bullet_2.png')
bullet_3_sprite = sprite_load ('bullet_3.png')
rail_1_sprite = sprite_load ('rail_1.png')
rail_2_sprite = sprite_load ('rail_2.png')
rail_3_sprite = sprite_load ('rail_3.png')
missile_1_sprite = sprite_load ('missile_1.png',True)
missile_2_sprite = sprite_load ('missile_2.png',True)
missile_3_sprite = sprite_load ('missile_3.png',True)
aa_bullet_1_sprite = sprite_load ('aa_bullet_1.png',True)

purple_laser_pic = pyglet.image.load('purple_laser.png')
purple_laser_sprite = sprite_atlas.add (purple_laser_pic)
purple_laser_sprite.anchor_x = purple_laser_pic.width / 2
#purple_laser_sprite.anchor_y = purple_laser_pic.height  # only anchor in x mid, so rotation point is at tail - so laser looks right
#tex_border (purple_laser_sprite)

lightning_1_pic = pyglet.image.load('lightning_1.png')
lightning_1_sprite = sprite_atlas.add (lightning_1_pic)
lightning_1_sprite.anchor_x = lightning_1_pic.width / 2
#lightning_1_sprite.anchor_y = lightning_1_pic.height  # only anchor in x mid, so rotation point is at tail - so laser looks right
tex_border (lightning_1_sprite)

lightning_2_pic = pyglet.image.load('lightning_2.png')
lightning_2_sprite = sprite_atlas.add (lightning_2_pic)
lightning_2_sprite.anchor_x = lightning_2_pic.width / 2
#lightning_1_sprite.anchor_y = lightning_1_pic.height  # only anchor in x mid, so rotation point is at tail - so laser looks right
tex_border (lightning_2_sprite)

purple_laser_source_sprite = sprite_load ('purple_laser_source.png')
purple_laser_source2_sprite = sprite_load ('purple_laser_source2.png')
lightning_source_sprite = sprite_load ('lightning_source.png')
tesla_damage_sprite = sprite_load ('tesla_damage.png')
spark_sprite = sprite_load ('spark.png')
blue_particle_sprite = sprite_load ('blue_particle.png')
white_particle_sprite = sprite_load ('white_particle.png')
spark_big_sprite = sprite_load ('spark_big.png')
mote_sprite = sprite_load ('mote.png')

smoke_pic = pyglet.image.load('smoke.png')
smoke_sprite = sprite_atlas.add (smoke_pic)

white_pic = pyglet.image.load('white.png')
health_sprite = sprite_atlas.add (white_pic)
tex_border (health_sprite)

red_shockwave_pic = pyglet.image.load('red_shockwave.png')
red_shockwave_sprite = sprite_atlas.add (red_shockwave_pic)

purple_shockwave_pic = pyglet.image.load('purple_shockwave.png')
purple_shockwave_sprite = sprite_atlas.add (purple_shockwave_pic)

swarm_normal_pic = pyglet.image.load('swarm_normal.png')
swarm_normal_tex = sprite_atlas.add (swarm_normal_pic)

swarm_fast_pic = pyglet.image.load('swarm_fast.png')
swarm_fast_tex = sprite_atlas.add (swarm_fast_pic)

swarm_group_pic = pyglet.image.load('swarm_group.png')
swarm_group_tex = sprite_atlas.add (swarm_group_pic)

swarm_normal_boss_pic = pyglet.image.load('swarm_normal_boss.png')
swarm_normal_boss_tex = sprite_atlas.add (swarm_normal_boss_pic)

swarm_jet_pic = pyglet.image.load('swarm_jet.png')
swarm_jet_tex = sprite_atlas.add (swarm_jet_pic)

# LOOKUP FOR TEXTURES
swarm_lookup = {	0:swarm_normal_tex,
					1:swarm_fast_tex,
					2:swarm_group_tex,
					3:swarm_normal_boss_tex,	
					4:swarm_jet_tex}


range_pic = pyglet.image.load('range.png')
range_sprite = sprite_atlas.add (range_pic)


frame_test_pic = pyglet.image.load ('frame_test.png')

button_ai_weak_off_pic = pyglet.image.load ('ai_weak_off.png')
button_ai_weak_on_pic = pyglet.image.load ('ai_weak_on.png')
button_ai_strong_off_pic = pyglet.image.load ('ai_strong_off.png')
button_ai_strong_on_pic = pyglet.image.load ('ai_strong_on.png')
button_ai_slow_off_pic = pyglet.image.load ('ai_slow_off.png')
button_ai_slow_on_pic = pyglet.image.load ('ai_slow_on.png')
button_ai_fast_off_pic = pyglet.image.load ('ai_fast_off.png')
button_ai_fast_on_pic = pyglet.image.load ('ai_fast_on.png')
button_ai_near_off_pic = pyglet.image.load ('ai_near_off.png')
button_ai_near_on_pic = pyglet.image.load ('ai_near_on.png')
button_ai_far_off_pic = pyglet.image.load ('ai_far_off.png')
button_ai_far_on_pic = pyglet.image.load ('ai_far_on.png')

button_cannon_tower_pic = pyglet.image.load ('cannon.png')
button_cannon_tower_mouseover_pic = pyglet.image.load ('cannon_mouseover.png')
button_cannon_tower_selected_pic = pyglet.image.load ('cannon_selected.png')

button_berserker_tower_pic = pyglet.image.load ('berserker_1_turret.png')
button_berserker_tower_mouseover_pic = pyglet.image.load ('berserker_mouseover.png')
button_berserker_tower_selected_pic = pyglet.image.load ('berserker_selected.png')

button_icbm_tower_pic = pyglet.image.load ('icbm_1_turret.png')
button_icbm_tower_mouseover_pic = pyglet.image.load ('icbm_mouseover.png')
button_icbm_tower_selected_pic = pyglet.image.load ('icbm_selected.png')

button_temporal_tower_pic = pyglet.image.load ('temporal_1_turret.png')
button_temporal_tower_mouseover_pic = pyglet.image.load ('temporal_mouseover.png')
button_temporal_tower_selected_pic = pyglet.image.load ('temporal_selected.png')

button_tesla_tower_pic = pyglet.image.load ('tesla_1_turret.png')
button_tesla_tower_mouseover_pic = pyglet.image.load ('tesla_mouseover.png')
button_tesla_tower_selected_pic = pyglet.image.load ('tesla_selected.png')

button_aa_tower_pic = pyglet.image.load ('aa_1_turret.png')
button_aa_tower_mouseover_pic = pyglet.image.load ('aa_mouseover.png')
button_aa_tower_selected_pic = pyglet.image.load ('aa_selected.png')

button_start_pic = pyglet.image.load ('start.png')
button_pause_pic = pyglet.image.load ('pause.png')

upgrade_pic = pyglet.image.load('upgrade.png')
sell_pic = pyglet.image.load('sell_ok.png')

map_bg = resource.image ('wp2.jpg')

title_background = resource.image('SWARM.jpg')
pause_background = resource.image('SWARM.png')




#
#	END OF LOAD TEXTURES
#	



#
#	LOAD AUDIO
#

if audio:

#title_music =  resource.media('yarp.mp3')
#title_music.play()

	audio_menu_over =  pyglet.media.StaticSource (resource.media('audio_menu_over.wav'))
	audio_menu_ok =  pyglet.media.StaticSource (resource.media('audio_menu_ok.wav'))
	audio_menu_escape =  pyglet.media.StaticSource (resource.media('audio_menu_escape.wav'))
	audio_menu_click =  pyglet.media.StaticSource (resource.media('audio_menu_click.wav'))

	audio_cannon_1_fire = pyglet.media.StaticSource (resource.media('audio_cannon_1_fire.wav'))
	audio_cannon_2_fire = pyglet.media.StaticSource (resource.media('audio_cannon_2_fire.wav'))

	audio_rail_1_fire = pyglet.media.StaticSource (resource.media('audio_rail_1_fire.wav'))

	audio_hit =  pyglet.media.StaticSource (resource.media('hit3.wav'))
	audio_explode = pyglet.media.StaticSource (resource.media('explode.mp3'))

	audio_upgrade = pyglet.media.StaticSource (resource.media('upgrade.wav'))
	


#
#	END OF LOAD AUDIO - SET UP WINDOW
#


window = pyglet.window.Window(1024, 768,"SWARM",True)
window.set_vsync (False)
window.set_fullscreen (False)
window.clear()

# over ride default escape key behaviour
def on_key_press(symbol, modifiers):
	if symbol == key.ESCAPE:
		if game.state & game.states['ingame']:
			game.state = game.state ^ game.states['paused']
			set_overlay ( PauseMenu() )
		return True
window.push_handlers(on_key_press)

glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
glEnable (GL_TEXTURE_2D)	


# SETUP DISPLAY LISTS

glNewList (4, GL_COMPILE)
spark_big_sprite.blit(0,0)
glEndList()
glNewList (2, GL_COMPILE)
spark_sprite.blit(0,0)
glEndList()
glNewList (3, GL_COMPILE)
mote_sprite.blit(0,0)
glEndList()
glNewList (5, GL_COMPILE)
white_particle_sprite.blit(0,0)
glEndList()
glNewList (6, GL_COMPILE)
small_red_bug_tex.blit(0,0)
glEndList()
glNewList (7, GL_COMPILE)
cannon_1_base_sprite.blit(0,0)
glEndList()
glNewList (8, GL_COMPILE)
cannon_1_turret_sprite.blit(0,0)
glEndList()
glNewList (9, GL_COMPILE)
fast_tex.blit(0,0)
glEndList()
glNewList (10, GL_COMPILE)
roomba_boss_tex.blit(0,0)
glEndList()
glNewList (11, GL_COMPILE)
cannon_2_turret_sprite.blit(0,0)
glEndList()
glNewList (12, GL_COMPILE)
cannon_3_turret_sprite.blit(0,0)
glEndList()
glNewList (13, GL_COMPILE)
cannon_2_base_sprite.blit(0,0)
glEndList()
glNewList (14, GL_COMPILE)
cannon_3_base_sprite.blit(0,0)
glEndList()
glNewList (15, GL_COMPILE)
jet_sprite.blit(0,0)
glEndList()
glNewList (16, GL_COMPILE)
jet_shadow_sprite.blit(0,0)
glEndList()
glNewList (17, GL_COMPILE)
aa_1_turret_sprite.blit (0,0)
glEndList()

#
#	MENU CLASSES
#

class Overlay(object):
    def update(self, dt):
        pass

    def draw(self):
        pass

class Menu(Overlay):
	def __init__ (self, title, background=None):
		self.title_text = pyglet.text.Label(title, 
                                            font_name=FONT_NAME,
                                            font_size=36,
                                            x=window.width // 2, 
                                            y=340,
                                            anchor_x='center',
                                            anchor_y='center')
		self.items = []
		self.background=background
		
	def reset(self):
		# assumes items have been added - to be called usually after menu has been setup with items.  if no items - use a banner instead :)
		self.selected_index = 0
		self.items[self.selected_index].selected = True
	
	def on_mouse_motion(self, x, y, dx, dy):
		for item in self.items:
			item.on_mouse_motion(x,y,dx,dy)
			
	def on_mouse_release(self, x, y, buttons, modifiers):
		for item in self.items:
			item.on_mouse_release(x,y,buttons,modifiers)
		
	def on_key_press(self, symbol, modifiers):
		if symbol == key.DOWN:
			self.selected_index += 1
			if audio: audio_menu_over.play()
		elif symbol == key.UP:
			self.selected_index -= 1
			if audio: audio_menu_over.play()
		else:
			self.items[self.selected_index].on_key_press(symbol, modifiers)
		self.selected_index = min(max(self.selected_index, 0), len(self.items) - 1)

		if symbol in (key.DOWN, key.UP) and game.sound_enabled:
			if audio: bullet_sound.play()
			
		if symbol == key.ESCAPE:
		# esc pressed while in a menu
			if audio: audio_menu_escape.play()
			if self.title_text.text=='Main Menu':
				# main menu esc pressed
				quit_option()
			elif self.title_text.text=='Pause':
				# in game pause menu esc pressed
				unpause()
				return pyglet.event.EVENT_HANDLED
			elif self.title_text.text=='Options':
				# options menu esc pressed, go back to main
				goto_main_menu()
			else:
				pass	# do nothing
				

	def draw(self):
		if self.background:
			self.background.blit (0,0,width=window.width, height=window.height)
		self.title_text.draw()
		
		# now check if mouse is over any of the items, if it is make sure this is the selected item
		for i, item in enumerate(self.items):
			if item.mouseover:
				if self.selected_index <> i:
					# new item, play over sound
					if audio: audio_menu_over.play()
				self.selected_index = i
				
		
		# now draw item, sending flag of true as parameter if this is selected - this will trigger the pointer drawing routine on this item
		for i, item in enumerate(self.items):
			item.draw(i == self.selected_index)
	

class MenuItem(object):
	pointer_color = (.46, 0, 1.)
	inverted_pointers = False
	
	def __init__(self, label, y, activate_func):
		self.y = y
		self.text = pyglet.text.Label(label,
                                      font_name=FONT_NAME,
                                      font_size=24,
                                      x=window.width // 2, 
                                      y=y,
                                      anchor_x='center',
                                      anchor_y='center')
		self.activate_func = activate_func
		self.mouseover=False

	def draw_pointer(self, x, y, color, flip=False):
		# Tint the pointer image to a color
		glPushAttrib(GL_CURRENT_BIT)
		glColor3f(*color)
		if flip:
			pointer_image_flip.blit(x, y)
		else:
			pointer_image.blit(x, y)
		glPopAttrib()

	def draw(self, selected):
		self.text.draw()

		if selected:
			self.draw_pointer(
                self.text.x - self.text.content_width / 2 - 
                    pointer_image.width / 2,
                self.y, 
                self.pointer_color,
                self.inverted_pointers)
			self.draw_pointer(
                self.text.x + self.text.content_width / 2 + 
                    pointer_image.width / 2,
                self.y,
                self.pointer_color,
                not self.inverted_pointers)

	def on_key_press(self, symbol, modifiers):
		if symbol == key.ENTER and self.activate_func:
			if audio: audio_menu_click.play()
			self.activate_func()
			
	def on_mouse_motion(self, x, y, dx, dy):
		if (y>self.text.y-(self.text.font_size//2) and y<self.text.y+(self.text.font_size//2)):
			self.mouseover=True
		else:
			self.mouseover=False
			
	def on_mouse_release(self, x, y, buttons, modifiers):
		if self.mouseover and buttons & mouse.LEFT:
			if audio: audio_menu_click.play()
			self.activate_func()


class ToggleMenuItem(MenuItem):
	pointer_color = (.27, .82, .25)
	inverted_pointers = True

	def __init__(self, label, value, y, toggle_func):
		self.value = value
		self.label = label
		self.toggle_func = toggle_func
		super(ToggleMenuItem, self).__init__(self.get_label(), y, None)

	def get_label(self):
		return self.label + (self.value and ': ON' or ': OFF')

	def on_key_press(self, symbol, modifiers):
		if symbol == key.LEFT or symbol == key.RIGHT:
			self.value = not self.value
			self.text.text = self.get_label()
			self.toggle_func(self.value)
			if audio: audio_menu_ok.play()	

	def on_mouse_release(self, x, y, buttons, modifiers):
	# overrides menuitem mouse release funtion
		if self.mouseover and buttons & mouse.LEFT:
			self.value = not self.value
			self.text.text = self.get_label()
			self.toggle_func(self.value)
			if audio: audio_menu_ok.play()	
			
			
	
class MainMenu(Menu):
	def __init__(self):
		super(MainMenu, self).__init__('Main Menu',background=title_background)
		self.items.append(MenuItem('Start', 280, begin_option))
		self.items.append(MenuItem('Options',250, options_option))
		self.items.append(MenuItem('Quit', 100, quit_option))
		self.reset()
		
class PauseMenu(Menu):
	def __init__(self):
		super(PauseMenu, self).__init__('Pause',background=pause_background)
		self.items.append(MenuItem('Continue',280,unpause))
		self.items.append(MenuItem('Main Menu',250,end_game))
		self.items.append(MenuItem('Game Options',220,ingame_options_option))
		self.items.append(MenuItem('Restart',160,begin_option))
		self.items.append(MenuItem('Quit',100,quit_option))
		self.reset()
		
	

class OptionsMenu(Menu):
	def __init__(self):
		super(OptionsMenu, self).__init__('Options',background=title_background)
		self.items.append(ToggleMenuItem('Fullscreen', window.fullscreen, 280, toggle_fullscreen_options_menu))
		self.items.append(ToggleMenuItem('Vsync', window.vsync, 250, window.set_vsync))
		self.items.append(MenuItem('Done', 190, end_game))
		self.reset()
		
class IngameOptionsMenu(Menu):
	def __init__(self):
		super(IngameOptionsMenu, self).__init__('Options',background=pause_background)
		self.items.append(ToggleMenuItem('Fullscreen', window.fullscreen, 280, toggle_fullscreen_ingameoptions_menu))
		self.items.append(ToggleMenuItem('Vsync', window.vsync, 250, window.set_vsync))
		self.items.append(MenuItem('Done', 190, pause))
		self.reset()
		
class GameOver (Menu):
	def __init__(self):
		super(GameOver, self).__init__('Game Over!',background=pause_background)
		self.items.append(MenuItem('Retry',280, begin_option))
		self.items.append(MenuItem('Main Menu',250,goto_main_menu))
		self.items.append(MenuItem('Quit',100,quit_option))
		self.reset()
		
# menu option functions

def toggle_fullscreen_options_menu(value):
	window.set_fullscreen(value)
	set_overlay (None)
	set_overlay (OptionsMenu())

def toggle_fullscreen_ingameoptions_menu(value):
	window.set_fullscreen(value)
	set_overlay (None)
	set_overlay (IngameOptionsMenu())
	
def pause():
	set_overlay ( PauseMenu() )

def unpause():
	game.state = game.state ^ game.states['paused']
	set_overlay ( None )

def ingame_options_option():
	set_overlay ( IngameOptionsMenu() )
	
def options_option():
	set_overlay ( OptionsMenu() )
	
def end_game ():
	# remove handlers of all objects
	for tower in game.towers:
		window.remove_handlers(tower)
	# reset game state and overlay
	game.state = game.states['menu']
	set_overlay ( MainMenu() )
	
def goto_main_menu():
	game.state = game.states['menu']
	set_overlay ( MainMenu() )

def begin_option ():
	# remove handlers of any towers left over from previous game (this could be from 'retry' option at gameover...
	for tower in game.towers:
		window.remove_handlers(tower)
	set_overlay(None)
	game.reset()
	if start_button not in gui.widgets:
		gui.widgets.append (start_button)
	game.state =  game.states['pregame'] | game.states['ingame']
	
def quit_option ():
	sys.exit()
	
def set_overlay(new_overlay):
	if game.overlay:
		window.remove_handlers(game.overlay)
	game.overlay = new_overlay
	if game.overlay:
		window.push_handlers(game.overlay)
		
		
		
		
		
#
#	END OF MENU CLASSES / FUNCTIONS
#	
	
	
	
	
def draw_circle (x, y, r,i):
	""" r = radius, i = steps"""
	angle=0
	r*=game.map.cellsize
	glLineWidth (2)
	glColor4f (1,0.5,0.5,0.5)
	glDisable (GL_TEXTURE_2D)
	glPushMatrix()
	glTranslatef (x,y,0)
	glBegin (GL_LINE_STRIP)
	while angle<=i+(math.pi*2):
		glVertex2f (math.cos(angle)*r, math.sin(angle)*r)
		angle+=i
	glEnd()
	glPopMatrix()
	glEnable (GL_TEXTURE_2D)
	glColor4f(1,1,1,1)
	

class amouse(object):
	def __init__ (self):
		self.x = 0
		self.y = 0
		self.mapx = 0
		self.mapy = 0
		self.dx = 0	# deploy x and y - used rather than mapx and mapy to give more natural feel to deploying towers
		self.dy = 0
		self.overmap = False
		self.lmb_clicked=False
		self.rmb_clicked=False
		self.tex = None
		
	def update_pos (self,x,y):
		self.x = x
		self.y = y
		
	def draw (self):
		if game.state & game.states['ingame'] and not game.state & game.states['paused'] and self.tex:
			if self.tex is valid_placement_tex:
				glColor4f (1,1,1,0.3)
				self.tex.blit (self.x-game.map.cellsize, self.y-game.map.cellsize)
				glColor4f (1,1,1,1)
				self.tex.blit (game.map.llx + (self.dx*game.map.cellsize), game.map.lly + (self.dy*game.map.cellsize) )
				draw_circle (self.x, self.y, game.deploying.range_sq, 0.15)
				if hasattr (game.deploying, "min_range_sq"):
					draw_circle (self.x, self.y, game.deploying.min_range_sq, 0.15)
			else:
				self.tex.blit (self.x, self.y)
		
		
	def update (self):
		# get map coords and display appropraite mouse icons
		if game.state & game.states['ingame']:
			if self.x > game.map.llx and self.x < game.map.llx + game.map.width_pixels and self.y > game.map.lly and self.y < game.map.lly + game.map.height_pixels:
				self.overmap = True
				self.mapx = (self.x - game.map.llx ) / game.map.cellsize
				self.mapy = (self.y - game.map.lly ) / game.map.cellsize
				#if game.deploying and game.map.placement_valid (self.mapx, self.mapy):
				if game.deploying:
					self.dx = int( ((self.x - game.map.llx )-(game.map.cellsize*0.5)) / game.map.cellsize)
					self.dy = int( ((self.y - game.map.lly )-(game.map.cellsize*0.5)) / game.map.cellsize)
					if game.credits >= game.deploying.cost:
						if game.map.placement_valid (self.dx, self.dy):
							self.tex = valid_placement_tex
						else:
							self.tex = invalid_placement_tex
					else:
						self.tex = money_tex
				
			else:
				self.overmap = False
				self.tex = None
				self.mapx = -1
				self.mapy = -1
		# reset mouse clicks from last frame and handle mouse clicks made 
		if self.lmb_clicked:
			self.lmb_clicked=False
			if game.state & game.states['ingame']:
				if self.tex is valid_placement_tex and game.deploying:
					if game.deploying.deploy():
						if audio: audio_menu_ok.play()
						game.credits-=game.deploying.cost
						credits_label.text = 'Credits: '+str(game.credits)
						game.deploying=copy.copy(game.deploying)	# ready to deploy next tower of same type
					else:
						pass # could not deploy for whatever reason
					
					
				if (self.tex is invalid_placement_tex or self.tex is money_tex) and game.deploying:
					# handle playing of error noise or something
					if audio: audio_menu_escape.play()
					pass
		if self.rmb_clicked:
			game.deploying=None
			self.tex = None
			game.selected=None
			if audio: audio_menu_escape.play()
			self.rmb_clicked=False
			
		
			

			
		
	def over (self, ll, tr):
		if self.x >= ll[0] and self.x <= tr[0] and self.y >= ll[1] and self.y <=tr[1]:
			return True
		else:
			return False

class GUI(object):
	""" gui contains widgets or frames, which contain all widgets """
	def __init__ (self):
		# get coords of corners
		self.ll = (0,0)
		self.lr = (window.width,0)
		self.tr = (window.width,window.height)
		self.tl = (0,window.height)
		self.widgets=[]
		self.enabled = True # always true
		
	def update (self,dt):
		for frame in self.widgets:
			frame.update(dt)
			
	def draw (self):
		for frame in self.widgets:
			frame.draw()
		
class Frame(object):
	""" a widget container """
	def __init__ (self, pos=(250,250), width=100, height=100, scale=False, border=None, background=None, background_colour=None):
		self.pos=pos
		self.scale=scale
		self.enabled = True
		self.visible = True
		
		# if background texture supplied, use that to determine area of frame, unless scale is True
		if background and not scale:
			self.width = background.width
			self.height = background.height
		else:
			self.width=width
			self.height=height
		
		# get coords of corners
		self.ll = (pos[0],pos[1]-self.height)
		self.lr = (pos[0]+self.width,pos[1]-self.height)
		self.tr = (pos[0]+self.width,pos[1])
		self.tl = (pos[0], pos[1])
			
		self.widgets=[]
		self.background = background
		
		# if no background colour given, then make it opaqe if texture given, otherwise make it almost black
		if background_colour is None:
			if background:
				self.background_colour = (1,1,1,1)
			else:
				self.background_colour = (1,1,1,0.1)
		else:
			self.background_colour = background_colour
		self.border = border
		
		# logic
		self.mouseover = False
		
		# callbacks
		self.on_mouseover = None
		
		# add self to gui
		gui.widgets.append (self)
		
	def update(self,dt):
		if self.visible:
			if mymouse.over ( self.ll , self.tr ):
				self.mouseover = True
			else:
				self.mouseover = False
				
			# update widgets in frame
			for widget in self.widgets:
				widget.update(dt)
		
			
	def draw (self):
		if self.enabled:
			if self.background:
				if self.scale:
					glColor4f (*self.background_colour)
					self.background.blit (self.ll[0], self.ll[1], width=self.width, height=self.height)
					glColor4f (1,1,1,1)
				else:
					glColor4f (*self.background_colour)
					self.background.blit (self.ll[0], self.ll[1])
					glColor4f (1,1,1,1)
			else:
				glColor4f (*self.background_colour)
				glDisable (GL_TEXTURE_2D)
				pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', (	self.ll[0], self.ll[1],
																		self.lr[0], self.lr[1],
																		self.tr[0], self.tr[1],
																		self.tl[0], self.tl[1])))
				glEnable (GL_TEXTURE_2D)
				glColor4f (1,1,1,1)
			for widget in self.widgets:
				widget.draw()

class Button(object):
	""" a button widget """
	def __init__ (self, parent, pos=(10, 10), width=10, height=10, scale=False, rmb_clears=True, background=None, background_colour=None, background_selected=None, background_mouseover=None):
		self.parent=parent # pointer to parent frame
	
		self.pos=(parent.tl[0]+pos[0], parent.tl[1]-pos[1])	# relative to parent top left
		self.scale=scale
		self.enabled=True
		self.visible=True
		self.rmb_clears=rmb_clears
		
		
		# if background texture supplied, use that to determine area of frame
		if background and not scale:
			self.width = background.width
			self.height = background.height
		else:
			self.width=width
			self.height=height
		
		# get coords of corners
		self.ll = (self.pos[0],				self.pos[1]-self.height)
		self.lr = (self.pos[0]+self.width,	self.pos[1]-self.height)
		self.tr = (self.pos[0]+self.width,	self.pos[1])
		self.tl = (self.pos[0], 			self.pos[1])
			
		self.background = background
		self.background_mouseover = background_mouseover
		
		self.background_selected = background_selected
		
		# if no background colour given, then make it opaqe if texture given, otherwise make it almost black
		if background_colour is None:
			if background:
				self.background_colour = (1,1,1,1)
			else:
				self.background_colour = (1,1,1,0.1)
		else:
			self.background_colour = background_colour
		
		# logic
		self.mouseover = False
		self.click = False
		self.selected = False
		
		# callbacks
		self.on_mouseover = None
		self.on_click = None
		self.on_right_click = None
		
		# add self to parent frame
		parent.widgets.append (self)
		
		# push handlers
		window.push_handlers(self)
		
	def update(self,dt):
		if self.enabled:
			pass
			
	def draw (self):
		if self.visible:
			if not self.enabled:
				glColor4f (1,1,1,0.6)
				self.background.blit (self.ll[0], self.ll[1])
				glColor4f (1,1,1,1)
				return
			if self.selected:
				glColor4f (*self.background_colour)
				self.background_selected.blit (self.ll[0], self.ll[1])
				glColor4f (1,1,1,1)
			else:
				if self.mouseover and self.background_mouseover:
					glColor4f (*self.background_colour)
					self.background_mouseover.blit (self.ll[0], self.ll[1])
					glColor4f (1,1,1,1)
				elif self.mouseover:
					self.background.blit (self.ll[0], self.ll[1])
				else:
					glColor4f (1,1,1,0.75)
					self.background.blit (self.ll[0], self.ll[1])
					glColor4f (1,1,1,1)
					
		
	def on_mouse_motion(self, x, y, dx, dy):
		if (x>self.ll[0] and x<self.tr[0] and y>self.ll[1] and y<self.tl[1]):
			if not self.mouseover:
				#audio_menu_over.play()
				self.mouseover=True
		else:
			self.mouseover=False
			
	def on_mouse_release(self, x, y, buttons, modifiers):
		if self.mouseover and buttons & mouse.LEFT  and self.visible and self.parent.enabled:
			if self.on_click:
				#audio_menu_click.play()
				self.on_click(self)
		if buttons & mouse.RIGHT and self.rmb_clears:
			self.selected = False
		

		
class anUpgrade(object):
	def __init__ (self, x, y, time, next_tower, oldai=0):
		self.x = copy.copy(x)
		self.y = copy.copy(y)
		self.screenx = game.map.llx + x*game.map.cellsize
		self.screeny = game.map.lly + y*game.map.cellsize
		self.time=time
		self.time_alive=0
		self.scale = 1.0 / time
		self.next_tower = next_tower
		self.oldai=oldai
		
	def update(self,dt):
		self.time_alive+=dt
		if self.time_alive>self.time:
			# upgrade complete
			print "Updgrade complete, putting tower at ", self.next_tower.pos
			self.next_tower.deploy_fast ()	# tells itself to deploy quickly with no map recalcs, and push its handlers itself
			# give upgraded tower same ai as old one - if applicable
			if self.oldai:
				self.next_tower.target_mode = self.oldai
			game.towers.remove (self)	# remove upgrade tower no longer needed
			
	def draw_selection (self):
		# no need for mouse detection - but function required
		pass
			
	def draw(self):
		glColor4f (1,1,0.5, (self.time_alive * self.scale))
		glDisable (GL_TEXTURE_2D)
		pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', (	self.screenx, self.screeny,
																self.screenx+game.cw*2, self.screeny,
																self.screenx+game.cw*2, self.screeny+game.cw*2,
																self.screenx, self.screeny+game.cw*2)))
		glEnable (GL_TEXTURE_2D)
		glColor4f (1,1,1,1)
		sell_outline_sprite.blit (self.screenx, self.screeny)
		
		
		

class aSell(object):
	def __init__ (self, x, y, time):
		self.x = copy.copy(x)
		self.y = copy.copy(y)
		self.screenx = game.map.llx + x*game.map.cellsize
		self.screeny = game.map.lly + y*game.map.cellsize
		self.time=time
		self.time_alive=0
		self.scale = 1.0 / time
		
	def update(self,dt):
		self.time_alive+=dt
		if self.time_alive>self.time:
			# sale complete - update map and recalc routes
			game.towers.remove (self)
			game.map.cell[self.x][self.y].passable=True
			game.map.cell[self.x+1][self.y].passable=True
			game.map.cell[self.x+1][self.y+1].passable=True
			game.map.cell[self.x][self.y+1].passable=True
			game.map.recalc_routes()
			
	def draw_selection (self):
		# no need 
		pass
			
	def draw(self):
		glColor4f (1,1,0.5, 1-(self.time_alive * self.scale))
		glDisable (GL_TEXTURE_2D)
		pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', (	self.screenx, self.screeny,
																self.screenx+game.cw*2, self.screeny,
																self.screenx+game.cw*2, self.screeny+game.cw*2,
																self.screenx, self.screeny+game.cw*2)))
		glEnable (GL_TEXTURE_2D)
		glColor4f (1,1,1,1)
		sell_outline_sprite.blit (self.screenx, self.screeny)
		
		
		
class aCell(object):
	def __init__ (self):
		self.passable=True
		self.tower = None
		

class aSwarm(object):
	def __init__(self, type=0, no=10, health=100, time=60, credits=10):
		""" create a swarm 
			0 = normal
			1 = fast
			2 = group
			3 = normal boss 
			4 = jet
		"""
		
		self.type=type
		self.no=no
		self.count=0
		self.health=health
		self.credits=credits
		self.time=time
		self.time_till_next_swarm = time
		if type==0:
			self.time_between_spawns = 0.8
		elif type==1:
			self.time_between_spawns = 1.0
		elif type==2:
			self.time_between_spawns = 0.05
		else:
			self.time_between_spawns = 0.8
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
			if self.type == 1:
				# create critter type 1 at start of routes
				for route in game.map.routes:
					yadda = fastEnemy(route, self.health, self.credits )
					yadda.health=self.health
					game.enemies.append ( yadda )
					self.count+=1
					self.time_since_last_spawn=0
			if self.type == 2:
				# create critter type 2 at start of routes
				for route in game.map.routes:
					yadda = normalEnemy(route, self.health, self.credits )
					yadda.health=self.health
					game.enemies.append ( yadda )
					self.count+=1
					self.time_since_last_spawn=0
			if self.type == 3:
				# create critter type 3 at start of routes
				for route in game.map.routes:
					yadda = normalEnemyBoss(route, self.health, self.credits )
					yadda.health=self.health
					game.enemies.append ( yadda )
					self.count+=1
					self.time_since_last_spawn=0
			if self.type == 4:
				# create critter type 4 at start of routes
				for route in game.map.routes:
					yadda = jetEnemy (route, self.health, self.credits )
					yadda.health=self.health
					game.flying_enemies.append ( yadda )
					self.count+=1
					self.time_since_last_spawn=0
		if self.time < 0:
			# do next wave
			if game.map.swarms and len(game.map.active_swarms)==1:
				# if this is only current swarm, and still have swarms left, pop next from list onto actives
				game.map.active_swarms.append ( game.map.swarms.pop(0) )
			# remove self from active swarm list
			game.map.active_swarms.remove (self)
			# ... and add time spent to total
			game.map.time_passed-=self.time_till_next_swarm
			
			
		# else do nothing

class aNode(object):
	def __init__ (self,pos):
		self.pos=pos
		self.next=None
		self.distance=99999
	
	#for heapq
	#def __cmp__(self, other): return cmp(self.distance, other.distance)
	
	#def __eq__ (self, other): return self is other
	def __eq__ (self, other): return self.distance == other.distance
	def __ne__ (self, other): return self.distance <> other.distance
	def __lt__ (self, other): return self.distance < other.distance
	def __gt__ (self, other): return self.distance > other.distance
	def __le__ (self, other): return self.distance <= other.distance
	def __ge__ (self, other): return self.distance >= other.distance
	
	#def __hash__ (self): return (100*self.pos[0] + self.pos[0])
	#def __hash__ (self): return id(self)
			
class aRoute(object):
	def __init__ (self, start, end, map):
		""" route class - takes start, end tuples of (x,y), and the map it belongs to """
		self.map = map
		self.start=start
		self.end=end
		self.route={}
		for a in xrange(0,self.map.width):
			for b in xrange(0,self.map.height):
				self.route[(a,b)]=aNode((a,b))
				
	
	def reset (self):
		for a in xrange(0,self.map.width):
			for b in xrange(0,self.map.height):
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
		map = self.map
		nb = self.map.get_neighbours
		distance = 1	# default distance - changed to 1.4 for diagonals
		start=self.start		# set up local for speed
		self_route=self.route	# set up local for speed
		hpop = heappop			# set up local for speed
		hpush = heappush		# set up local for speed
		while Q:
			curnode = hpop (Q)	# pop next nearest node off top of binary heap
			if curnode.pos not in visited:
				curnode_pos = curnode.pos	# remove dot for speed
				visited[curnode_pos]=True
				neighbours = nb (curnode_pos)
				for pos in neighbours:
					if pos == start:
						path_found = True
					neighbour_node = self_route [(pos[0],pos[1])]
					if pos[0]<>curnode_pos[0] and pos[1]<>curnode_pos[1]:
						distance = 1.4
					else:
						distance = 1
					newdist = curnode.distance+distance
					if neighbour_node.distance > newdist:
						neighbour_node.next = curnode
						neighbour_node.distance = newdist
					if neighbour_node.pos not in visited:
						# if neighbour node not already fully processed, stick on priority queue for consideration
						hpush (Q, neighbour_node)
		return path_found
		
	
	
	
	
	def recalc_no_priority (self):
		"""	dijkstra algorithm - works from exit to start fills all reachable nodes in map 
			no priority queue - so produces not so great paths - but very fast """
		path_found = False
		self.reset()
		Q = []
		visited = {}
		self.route[(self.end[0],self.end[1])].next=None
		self.route[(self.end[0],self.end[1])].distance=0	# dist to exit (end) node is going to be zero
		# create starting set Q, (binary heap) containing all nodes with exit node set to 0
		Q.append (self.route[(self.end[0],self.end[1])] )
		map = self.map
		nb = self.map.get_neighbours
		distance = 1	# default distance - changed to 1.4 for diagonals
		start=self.start	# set up local for speed
		while Q:
			curnode = Q.pop()	# pop next nearest node off top of binary heap
			if curnode.pos not in visited:
				visited[curnode.pos]=True
				neighbours = nb (curnode.pos)
				for pos in neighbours:
					if pos == start:
						path_found = True
					neighbour_node = self.route[(pos[0],pos[1])]
					if pos[0]<>curnode.pos[0] and pos[1]<>curnode.pos[1]:
						distance = 1.4
					else:
						distance = 1
					if neighbour_node.distance > curnode.distance+distance:
						neighbour_node.next = curnode
						neighbour_node.distance = curnode.distance+distance
					if neighbour_node.pos not in visited:
						# if neighbour node not already fully processed, stick on priority queue for consideration
						Q.append (neighbour_node)
		return path_found
		

		
		
		
class aMap(object):
	def __init__ (self, width=28, height=24, cellsize=24, llx=148, lly=148):
		""" aMap - takes width, height, cellsize and llx and lly for offset of lower left hand corner from screen edges """
		# create 2d array of Cells
		self.cell = []
		self.width = width
		self.height = height
		self.width_pixels = width * cellsize
		self.height_pixels = height * cellsize
		self.current_swarm=0
		self.llx = llx
		self.lly = lly
		self.cellsize=cellsize
		self.sell_time = 2
		self.sell_time_multiplier = 1.05
		self.time_passed = 0
		
		
		self.active_swarms = []
		self.swarms = []	# type, number of critters, health of each critter, time till next swarm, credits per kill
		self.swarms.append ( aSwarm (0, 30, 15, 25, 1) )
		self.swarms.append ( aSwarm (1, 15, 15, 25, 2) )
		self.swarms.append ( aSwarm (2, 20, 20, 25, 2) )
		self.swarms.append ( aSwarm (1, 25, 30, 25, 2) )
		self.swarms.append ( aSwarm (0, 20, 50, 25, 2) )
		self.swarms.append ( aSwarm (4, 20, 10, 25, 3) )
		self.swarms.append ( aSwarm (2, 30, 70, 30, 3) )
		self.swarms.append ( aSwarm (1, 30, 100, 30, 3) )
		self.swarms.append ( aSwarm (2, 30, 150, 30, 3) )
		self.swarms.append ( aSwarm (1, 35, 150, 30, 3) )	
		self.swarms.append ( aSwarm (3, 1, 7000, 30, 100) )
		self.swarms.append ( aSwarm (1, 40, 200, 30, 4) )
		self.swarms.append ( aSwarm (4, 20, 180, 30, 5) )
		self.swarms.append ( aSwarm (0, 20, 300, 30, 5) )
		
		
		self.routes=[]
		self.routes.append ( aRoute( (0,height/2), (width-1,height/2), self) )
		self.routes.append ( aRoute( (width/2,height-1), (width/2,0), self) )
		
		
		# create map
		for a in xrange(0,width):
			row=[]
			for b in xrange(0,height):
				row.append ( aCell() )
			self.cell.append ( row )
			
		
			
		# TEMPORARY WALLS - TODO: implement custom map loading
		for a in range(width):
			if a < (width/2)-4 or a > (width/2)+3:
				self.cell[a][0].passable = False
				self.cell[a][height-1].passable = False
		for a in range(height):
			if a < (height/2)-3 or a > (height/2)+2:
				self.cell[0][a].passable = False
				self.cell[width-1][a].passable = False
		
		self.create_display_list()
		
	def swarm_update (self, tick):
		if self.active_swarms:
			for swarm in self.active_swarms:
				swarm.update(tick)
			
	def create_display_list (self):
		glNewList(1,GL_COMPILE)
		
		# draw map background here if needed
		map_bg.blit (self.llx, self.lly, width=(self.width*self.cellsize), height=(self.height*self.cellsize))
		
		glDisable (GL_TEXTURE_2D)
		
		# GRID
		glColor4f (0.7,0.7,1,0.05)
		glLineWidth(1)
		glBegin (GL_LINES)
		for x in range (0,self.width+1):
			glVertex2f (self.llx + (x*self.cellsize), self.lly)
			glVertex2f (self.llx + (x*self.cellsize), self.lly + (self.height * self.cellsize))
		for y in range (0,self.height+1):
			glVertex2f (self.llx, self.lly + (y*self.cellsize))
			glVertex2f (self.llx + (self.width * self.cellsize), self.lly + (y*self.cellsize))
		glEnd()
		
		# WALLS
		glColor4f (1,1,1,0.2)
		glBegin (GL_QUADS)
		for x in range (0,self.width):
			for y in range (0,self.height):
				if self.cell[x][y].passable != True:
					glVertex2f ( (x*self.cellsize)+self.llx, (y*self.cellsize)+self.lly)
					glVertex2f ((x*self.cellsize)+self.llx, (y*self.cellsize)+self.lly+self.cellsize)
					glVertex2f ((x*self.cellsize)+self.llx+self.cellsize, (y*self.cellsize)+self.lly+self.cellsize)
					glVertex2f ((x*self.cellsize)+self.llx+self.cellsize, (y*self.cellsize)+self.lly)
		glEnd()
		glColor4f (1,1,1,1)
		
		glEnable (GL_TEXTURE_2D)
		
		glEndList()
		
	def draw (self):
		pass
		glCallList(1)
		
	def draw_selection (self):
		pass
		
	def debug_check_cells (self):
		for x in range(self.width):
			for y in range(self.height):
				print "Cell ",x,",",y," is passable? ", self.cell[x][y].passable
				
	def recalc_routes (self):
		valid = True
		for route in self.routes:
			#if not route.recalc_no_priority():
			if not route.recalc():
				valid = False
		return valid
		

		
	def get_neighbours (self, pos):
		""" for pos (tuple of x,y) returns passable neightbours in map as a list of coordinate tuples - empty list if none """
		l=[]
		px=pos[0]
		py=pos[1]
		# create local for speed
		c = self.cell
		for x in xrange (pos[0]-1, pos[0]+2):
			for y in xrange (pos[1]-1,pos[1]+2):
				if x is not -1 and y is not -1 and x is not self.width and y is not self.height:
					# in bounds
					#print "debug: getting neighbours for cell at ",x,",",y
					if c[x][y].passable:
						corner_walkable=True
						if x == px-1:
							if y == py-1:
								if c[px-1][py].passable is False or c[px][py-1].passable is False:
									corner_walkable=False
							elif y == py+1:
								if c[px-1][py].passable is False or c[px][py+1].passable is False:
									corner_walkable=False
						elif x == px+1:
							if y == py-1:
								if c[px][py-1].passable is False or c[px+1][py].passable is False:
									corner_walkable=False
							elif y == py+1:
								if c[px+1][py].passable is False or c[px][py+1].passable is False:
									corner_walkable=False
						if corner_walkable:
							l.append ( (x,y) )
		return l
		
	def placement_valid (self, x, y):
		""" takes map x and y and determines if 2x2 placement is valid """
		# check against map itself
		if x<0 or y<0 or x>self.width-2 or y>self.height-2:
			return False
		if not self.cell[x][y].passable or not self.cell[x+1][y].passable or not self.cell[x+1][y+1].passable or not self.cell[x][y+1].passable:
			return False
		# map is ok, check against all beasties
		for enemy in game.enemies:
			if int(enemy.pos[0]) == x or int(enemy.pos[0]) == x+1:
				if int(enemy.pos[1]) == y or int(enemy.pos[1]) == y+1:
					return False
		return True
	


	
	
	
	
	
#
#	Entities
#






class Enemy(object):
	""" normal enemy BASE class.  takes:  route, health, credits """
	def __init__ (self, route=None, health = 10, credits = 5):
		self.map = game.map
		self.pos=[0,0]
		self.pos[0]=route.start[0]+0.5
		self.pos[1]=route.start[1]+0.5
		
		self.route = route
		self.diag = False
		self.health = health
		self.health_scale = 1.0/health
		self.credits = credits
		self.alive = True
		self.dir = None
		self.target_dir = None
		self.speed = 1.8
		self.speed_multiplier = 1
		self.speed_reduction_time_left = 0
		self.damage_per_second=0
		self.damage_time=0
		
		self.next_position = copy.copy(self.route.route[(int(self.pos[0]),int(self.pos[1]))].next.pos)
		self.next_position = (self.next_position[0]+0.5,self.next_position[1]+0.5)
		#self.previous_position = self.next_position
		self.previous_position = self.pos
		
		self.time_since_hit = 0
		
		self.tex = None
		
		# offset start and randomize a bit
		if route.start[0]==0:
			self.pos[0]-=4
			yrand=-2+(int(random.random()*4))
			self.pos[1]+=yrand
			self.next_position = (self.next_position[0]-1, self.pos[1])
		if route.start[1]==game.map.height-1:
			self.pos[1]+=5
			xrand=-2+(int(random.random()*4))
			self.pos[0]+=xrand
			self.next_position = (self.pos[0], self.next_position[1])
		
		if abs(self.pos[0]-self.next_position[0]) > 0.6 and abs(self.pos[1]-self.next_position[1]) > 0.6:
			self.diag = True
		else:
			self.diag = False
		# make sure initial direction is facing intital target path
		self.set_target_dir()
		self.dir = copy.copy (self.target_dir)
		

	def draw (self):
		x = self.map.llx + (self.pos[0]*self.map.cellsize)
		y = self.map.lly + (self.pos[1]*self.map.cellsize)
		h = self.health * self.health_scale
	
		glPushMatrix()
		glTranslatef (x, y, 0)
		glRotatef (self.dir, 0, 0, 1)
		glCallList (self.tex)
		if self.speed_multiplier<1:
			purple_laser_source_sprite.blit(0,0)
		if self.damage_per_second:
			tesla_damage_sprite.blit(0,0)
		glPopMatrix()
		
		#health bar
		if h>0:
			glColor4f (1-h,h,0,1)
			health_sprite.blit (x-12,y+18, width=h*24)
			glColor4f (1,1,1,1)
			
	def reduce_speed (self, multiplier, effect_time):
		self.speed_multiplier = multiplier
		self.speed_reduction_time_left += effect_time
		
	def damage_over_time (self, damage_per_second, time):
		self.damage_per_second+=damage_per_second
		self.damage_time+=time
	
	def set_target_dir (self):
		if int(self.next_position[0]) > int(self.pos[0]):
			# right
			if int(self.next_position[1]) > int(self.pos[1]):
				# up right
				self.target_dir = 315
			elif int(self.next_position[1]) == int(self.pos[1]):
				# right
				self.target_dir = 270
			else:
				#down right
				self.target_dir = 225
		elif int(self.next_position[0]) < int(self.pos[0]):
			# left
			if int(self.next_position[1]) > int(self.pos[1]):
				# up left
				self.target_dir = 45
			elif int(self.next_position[1]) == int(self.pos[1]):
				# left
				self.target_dir = 90
			else:
				#down left
				self.target_dir = 135
		else:
			# straight up or down
			if int(self.next_position[1]) > int(self.pos[1]):
				# up
				self.target_dir = 0
			else:
				#down
				self.target_dir = 180
			
	def get_current_grid_pos (self):
		return [ int(self.pos[0]), int(self.pos[1]) ]
		
	def get_path_distance_left (self):
		if self.pos[0]<0 or self.pos[1]>game.map.height-2:	# maybe should be just -1?
			return 99
		#gridpos = self.get_current_grid_pos ()
		return self.route.route[ (int(self.pos[0]), int(self.pos[1]) ) ].distance

	def update (self, tick):
	
		# do attrition damage (from tesla or similar)
		if self.damage_per_second:
			self.damage_time-=tick
			if self.damage_time<0:
				self.damage_per_second=0
			else:
				self.health-=self.damage_per_second*tick
				
		if self.health<0:
			# I`m dead
			if audio: audio_explode.play()
			# do other cleanup jobs and spawn whatever necessary particles
			game.particles.append (particle_explosion(copy.copy(self.pos)))
			self.alive = False
			game.score += self.credits*3
			game.credits += self.credits
			credits_label.text = "Credits: " + str(game.credits)
			score_label.text = "Score: " +str(game.score)
			game.enemies.remove (self)
			return 0
		
		if self.speed_multiplier<1:
			self.speed_reduction_time_left -= tick
			if self.speed_reduction_time_left < 0:
				self.speed_multiplier = 1
				self.speed = copy.copy(self.original_speed)
			else:
				self.speed = self.original_speed * self.speed_multiplier
		
		self.time_since_hit+=tick
		
		# check still on path
		# make locals for speed
		sp0 = self.pos[0]
		sp1 = self.pos[1]
		if abs(sp0-self.next_position[0]) < 0.1 and abs(sp1-self.next_position[1]) < 0.1:
			# get next path position
			if self.route.route[(int(sp0),int(sp1))].next:
				self.previous_position = copy.copy(self.next_position)
				self.next_position = copy.copy(self.route.route[(int(sp0),int(sp1))].next.pos)
				self.next_position = (self.next_position[0]+0.5, self.next_position[1]+0.5)
				
				if abs(sp0-self.next_position[0]) > 0.6 and abs(sp1-self.next_position[1]) > 0.6:
					self.diag = True
				else:
					self.diag = False
				self.set_target_dir()	# set new target direction according to new next position
				
			else:
				# might be end of path - check
				if self.route.route[(int(sp0),int(sp1))].pos == self.route.end:
					# end of path!
					# job done - update all
					self.alive = False
					game.enemies.remove (self)
					game.lives -= 1
					lives_label.text = "Lives: " +str(game.lives)
					# check if game over now...
					if game.lives<1:
						set_overlay (GameOver())
						game.state=game.states['menu']
				else:
					#else not end of path, go back to where we were :)
					self.next_position = self.previous_position
		
		# rotate if necessary to face direction of travel
		if self.dir <> self.target_dir:
			if self.dir < self.target_dir:
				self.dir += 9	# must be a divisor of 45 for rotations to work properly ie. 3, 5, 9, 15, 45
			else:
				self.dir -= 9	# must be a divisor of 45 for rotations to work properly
		
		# reaffirm local next position for speed (it may have changed above)
		if self.diag:
			speed = self.speed * 0.7 
			if sp0 > self.next_position[0] +0.1:
				self.pos[0] -= tick * speed
			elif sp0 < self.next_position[0]-0.1:
				self.pos[0] += tick * speed
			if sp1 > self.next_position[1] + 0.1:
				self.pos[1] -= tick *speed
			elif sp1 <self.next_position[1] -0.1:
				self.pos[1] += tick *speed
		else:
			if sp0 > self.next_position[0]+0.1:
				self.pos[0] -= tick * self.speed 
			elif sp0 < self.next_position[0]-0.1:
				self.pos[0] += tick * self.speed
			if sp1 > self.next_position[1]+0.1:
				self.pos[1] -= tick * self.speed
			elif sp1 < self.next_position[1]-0.1:
				self.pos[1] += tick * self.speed	

				
				
class FlyingEnemy(object):
	""" normal FLYING enemy base class.  takes:  route, health, credits """
	def __init__ (self, route=None, health = 10, credits = 5):
		self.map = game.map
		self.pos=[0,0]
		self.pos[0]=route.start[0]
		self.pos[1]=route.start[1]
		
		self.route = route
		self.diag = False
		self.health = health
		self.health_scale = 1.0/health
		self.credits = credits
		self.alive = True

		self.speed_multiplier=1
		self.speed_reduction_time_left = 0
		self.damage_per_second=0
		self.damage_time=0

		self.time_since_hit = 0
		
		self.tex = None
		self.shadow_tex = None
		local_route_end=[self.route.end[0],self.route.end[1]]
		# offset start and randomize a bit
		if route.start[0]==0:
			self.pos[0]-=4
			yrand=-2+(int(random.random()*4))
			local_route_end[1] += -2+(int(random.random()*4))
			self.pos[1]+=yrand
		if route.start[1]==game.map.height-1:
			self.pos[1]+=5
			xrand=-2+(int(random.random()*4))
			local_route_end[0] += -2+(int(random.random()*4))
			self.pos[0]+=xrand
			
		dx = local_route_end[0] - self.pos[0]
		dy = local_route_end[1] - self.pos[1]
		self.dir = math.atan2 (dy, dx) * 57.2957795 + 90	# rotation angle
		length = math.sqrt (dx**2 + dy**2)
		if dx==0:
			self.direction=[0,-1]
		elif dy==0:
			self.direction=[1,0]
		else:
			self.direction = [ (dx/length), (dy/length) ]

		

		

	def draw (self):
		x = self.map.llx + (self.pos[0]*self.map.cellsize)
		y = self.map.lly + (self.pos[1]*self.map.cellsize)
		h = self.health * self.health_scale
	
		# shadow
		glPushMatrix()
		glTranslatef (x-20, y-20, 0)
		glCallList (self.shadow_tex)
		glPopMatrix ()
		
		glPushMatrix()
		glTranslatef (x, y, 0)
		glRotatef (self.dir, 0, 0, 1)
		glCallList (self.tex)
		if self.speed_multiplier<1:
			purple_laser_source_sprite.blit(0,0)
		if self.damage_per_second:
			tesla_damage_sprite.blit(0,0)
		glPopMatrix()
		
		
		#health bar
		if h>0:
			glColor4f (1-h,h,0,1)
			health_sprite.blit (x-12,y+18, width=h*24)
			glColor4f (1,1,1,1)
			
	def reduce_speed (self, multiplier, effect_time):
		self.speed_multiplier = multiplier
		self.speed_reduction_time_left += effect_time
		
	def damage_over_time (self, damage_per_second, time):
		self.damage_per_second+=damage_per_second
		self.damage_time+=time
	
	def get_current_grid_pos (self):
		return [ int(self.pos[0]), int(self.pos[1]) ]
		
	def get_path_distance_left (self):
		if self.pos[0]<0 or self.pos[1]>game.map.height-2:	# maybe should be just -1?
			return 99
		#gridpos = self.get_current_grid_pos ()
		return self.route.route[ (int(self.pos[0]), int(self.pos[1]) ) ].distance

	def update (self, tick):
	
		# do attrition damage (from tesla or similar)
		if self.damage_per_second:
			self.damage_time-=tick
			if self.damage_time<0:
				self.damage_per_second=0
			else:
				self.health-=self.damage_per_second*tick
				
		if self.health<0:
			# I`m dead
			if audio: audio_explode.play()
			# do other cleanup jobs and spawn whatever necessary particles
			game.particles.append (particle_explosion(copy.copy(self.pos), ))
			self.alive = False
			game.score += self.credits*3
			game.credits += self.credits
			credits_label.text = "Credits: " + str(game.credits)
			score_label.text = "Score: " +str(game.score)
			game.flying_enemies.remove (self)
			return 0
		
		if self.speed_multiplier<1:
			self.speed_reduction_time_left -= tick
			if self.speed_reduction_time_left < 0:
				self.speed_multiplier = 1
				self.speed = copy.copy(self.original_speed)
			else:
				self.speed = self.original_speed * self.speed_multiplier
		
		self.time_since_hit+=tick
		
		# check still on path
		# make locals for speed
		sp0 = self.pos[0]
		sp1 = self.pos[1]
		
		# end of path? - check
		if ( self.route.end[1]==0 and self.pos[1]<0) or (self.route.end[1]>0 and self.pos[0]>=game.map.width):
			# end of path!
			# job done - update all
			self.alive = False
			game.flying_enemies.remove (self)
			game.lives -= 1
			lives_label.text = "Lives: " +str(game.lives)
			# check if game over now...
			if game.lives<1:
				set_overlay (GameOver())
				game.state=game.states['menu']
		else:
			self.pos[0] += self.direction[0] * tick * self.speed
			self.pos[1] += self.direction[1] * tick * self.speed
				
				

class normalEnemy(Enemy):
	""" normal enemy class.  takes:  route, health, credits """
	def __init__ (self, route=None, health = 10, credits = 5):
		super (normalEnemy, self).__init__(route, health, credits)	# run init of parent class
		self.speed = 1.8
		self.original_speed = copy.copy(self.speed)
		self.tex = 6

		
class normalEnemyBoss(Enemy):
	""" normal enemy class.  takes:  route, health, credits """
	def __init__ (self, route=None, health = 10, credits = 5):
		super (normalEnemyBoss, self).__init__(route, health, credits)	# run init of parent class
		self.speed = 1.6
		self.original_speed = copy.copy(self.speed)
		self.tex = 10

class fastEnemy(Enemy):
	""" normal enemy class.  takes:  route, health, credits """
	def __init__ (self, route=None, health = 10, credits = 5):
		super (fastEnemy, self).__init__(route, health, credits)	# run init of parent class
		self.speed = 3.0
		self.original_speed = copy.copy(self.speed)
		self.tex = 9		
		
class jetEnemy(FlyingEnemy):
	def __init__ (self, route=None, health = 10, credits = 5):
		super (jetEnemy, self).__init__(route, health, credits)	# run init of parent class
		self.speed = 2.8
		self.original_speed = copy.copy(self.speed)
		self.tex = 15
		self.shadow_tex = 16
				
				


				
				
				
				
#
#	PROJECTILES
#
				
				
				
				
				
				
class DummyTarget(object):	# used for projectiles to aim for once target is dead
	def __init__(self,pos):
		self.pos = pos
		self.health=0
		self.alive=True
				

class AA_Bullet_1(object):
	def __init__ (self, pos, target, damage):
		# dir set at init phase - determined by angle to target, then scheduled task pushed onto stack to recheck every 0.2 seconds
		self.pos=pos
		self.target=target
		self.damage=damage
		self.damage_range_sq = 5
		self.speed = 14
		self.dir=0
		dx = target.pos[0]-pos[0]
		dy = target.pos[1]-pos[1]
		self.dir = math.atan2 (dy, dx) * 57.2957795 + 90
		length = math.sqrt (dx**2 + dy**2)
		if dx==0:
			self.direction=[0,self.speed*dy]
		elif dy==0:
			self.direction=[self.speed*dx,0]
		else:
			self.direction = [ self.speed*(dx/length), self.speed*(dy/length) ]
		clock.schedule_interval(self.check_dir, .2)   # check direction to target once every 0.2 seconds
		
	def draw (self):
		glPushMatrix()
		glTranslatef (game.map.llx + (game.map.cellsize * self.pos[0]),  game.map.lly + (game.map.cellsize * self.pos[1]), 0)
		glRotatef (self.dir, 0, 0, 1)
		aa_bullet_1_sprite.blit (0,0)
		glPopMatrix()
		
	def check_dir (self, dt):
		dx = self.target.pos[0]-self.pos[0]
		dy = self.target.pos[1]-self.pos[1]
		self.dir = math.atan2 (dy, dx) * 57.2957795 + 90
		
	def update (self, tick):
		
		# add particle fx here
		#game.particles.append (particle_small_hit( [ game.map.llx + (game.map.cellsize * self.pos[0]), game.map.lly + (game.map.cellsize * self.pos[1])]     ))
		
		if self.target.alive:
			dx = self.target.pos[0]-self.pos[0]
			dy = self.target.pos[1]-self.pos[1]
			if abs(dx) < 0.5 and abs(dy) < 0.5:
				# HIT TARGET
				if audio: audio_hit.play()
			
				self.target.health-=self.damage
				game.projectiles.remove (self)
				clock.unschedule (self.check_dir)	# remove direction check from scheduler
			else:
				speed = self.speed * tick
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
			# target dead - set up dummy target to aim for
			game.projectiles.remove (self)
			#self.target = DummyTarget (self.target.pos)

				
				
class Missile_1(object):
	def __init__ (self, pos, target, damage):
		# dir set at init phase - determined by angle to target, then scheduled task pushed onto stack to recheck every 0.2 seconds
		self.pos=pos
		self.target=target
		self.damage=damage
		self.damage_range_sq = 5
		self.speed = 0.1
		self.accel = 7
		self.dir=0
		dx = target.pos[0]-pos[0]
		dy = target.pos[1]-pos[1]
		self.dir = math.atan2 (dy, dx) * 57.2957795 + 90
		length = math.sqrt (dx**2 + dy**2)
		if dx==0:
			self.direction=[0,self.speed*dy]
		elif dy==0:
			self.direction=[self.speed*dx,0]
		else:
			self.direction = [ self.speed*(dx/length), self.speed*(dy/length) ]
		clock.schedule_interval(self.check_dir, .2)   # check direction to target once every 0.2 seconds
		
	def draw (self):
		glPushMatrix()
		glTranslatef (game.map.llx + (game.map.cellsize * self.pos[0]),  game.map.lly + (game.map.cellsize * self.pos[1]), 0)
		glRotatef (self.dir, 0, 0, 1)
		missile_1_sprite.blit (0,0)
		glPopMatrix()
		
	def check_dir (self, dt):
		dx = self.target.pos[0]-self.pos[0]
		dy = self.target.pos[1]-self.pos[1]
		self.dir = math.atan2 (dy, dx) * 57.2957795 + 90
		
	def update (self, tick):
		
		# add particle fx here
		game.particles.append (particle_small_hit( [ game.map.llx + (game.map.cellsize * self.pos[0]), game.map.lly + (game.map.cellsize * self.pos[1])]     ))
		#if random.random()>0.4: game.particles.append (particle_smoke( self.pos))
		
		self.speed += self.accel * tick
			
		if self.target.alive:
			dx = self.target.pos[0]-self.pos[0]
			dy = self.target.pos[1]-self.pos[1]
			if abs(dx) < 0.5 and abs(dy) < 0.5:
				# HIT TARGET
				if audio: audio_hit.play()
				
				# do shockwave
				game.particles.append ( particle_shockwave (self.pos))
				
				# damage all within damage radius
				for enemy in game.enemies:
					# get squared distance
					sd = (self.pos[0]-enemy.pos[0])**2 + (self.pos[1]-enemy.pos[1])**2
					if sd < self.damage_range_sq:
						enemy.health-=self.damage
						
				game.projectiles.remove (self)
				clock.unschedule (self.check_dir)	# remove direction check from scheduler
			else:
				speed = self.speed * tick
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
			# target dead - set up dummy target to aim for
			self.target = DummyTarget (self.target.pos)
			
			# commented out code below - used only if dummy target idea not used
			#game.particles.append ( particle_shockwave (self.pos))
			#game.projectiles.remove (self)
		


class Missile_2(object):
	def __init__ (self, pos, target, damage):
		# dir set at init phase - determined by angle to target, then scheduled task pushed onto stack to recheck every 0.1 seconds
		self.pos=pos
		self.target=target
		self.damage=damage
		self.damage_range_sq = 8
		self.speed = 0.1
		self.accel = 17
		self.dir=0
		dx = target.pos[0]-pos[0]
		dy = target.pos[1]-pos[1]
		self.dir = math.atan2 (dy, dx) * 57.2957795 + 90
		length = math.sqrt (dx**2 + dy**2)
		if dx==0:
			self.direction=[0,self.speed*dy]
		elif dy==0:
			self.direction=[self.speed*dx,0]
		else:
			self.direction = [ self.speed*(dx/length), self.speed*(dy/length) ]
		clock.schedule_interval(self.check_dir, .1)   # check direction to target once every 0.1 seconds
		
	def draw (self):
		glPushMatrix()
		glTranslatef (game.map.llx + (game.map.cellsize * self.pos[0]),  game.map.lly + (game.map.cellsize * self.pos[1]), 0)
		glRotatef (self.dir, 0, 0, 1)
		missile_2_sprite.blit (0,0)
		glPopMatrix()
		
	def check_dir (self, dt):
		dx = self.target.pos[0]-self.pos[0]
		dy = self.target.pos[1]-self.pos[1]
		self.dir = math.atan2 (dy, dx) * 57.2957795 + 90
		
	def update (self, tick):
		
		# add particle fx here
		game.particles.append (particle_white_trail(self.pos))
		
		
		#if random.random()>0.4: game.particles.append (particle_smoke( self.pos))
		
		self.speed += self.accel * tick
			
		if self.target.alive:
			dx = self.target.pos[0]-self.pos[0]
			dy = self.target.pos[1]-self.pos[1]
			if abs(dx) < 0.5 and abs(dy) < 0.5:
				# HIT TARGET
				if audio: audio_hit.play()
				
				# do shockwave
				game.particles.append ( particle_shockwave (self.pos, 0.7, 900))
				
				# damage all within damage radius
				for enemy in game.enemies:
					# get squared distance
					sd = (self.pos[0]-enemy.pos[0])**2 + (self.pos[1]-enemy.pos[1])**2
					if sd < self.damage_range_sq:
						enemy.health-=self.damage
						
				game.projectiles.remove (self)
				clock.unschedule (self.check_dir)	# remove direction check from scheduler
			else:
				speed = self.speed * tick
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
			# target dead - set up dummy target to aim for
			self.target = DummyTarget (self.target.pos)
			
			# commented out code below - used only if dummy target idea not used
			#game.particles.append ( particle_shockwave (self.pos))
			#game.projectiles.remove (self)

class Missile_3(object):
	def __init__ (self, pos, target, damage):
		# dir set at init phase - determined by angle to target, then scheduled task pushed onto stack to recheck every 0.1 seconds
		self.pos=pos
		self.target=target
		self.damage=damage
		self.damage_range_sq = 12
		self.speed = 0.1
		self.accel = 24
		self.dir=0
		dx = target.pos[0]-pos[0]
		dy = target.pos[1]-pos[1]
		self.dir = math.atan2 (dy, dx) * 57.2957795 + 90
		length = math.sqrt (dx**2 + dy**2)
		if dx==0:
			self.direction=[0,self.speed*dy]
		elif dy==0:
			self.direction=[self.speed*dx,0]
		else:
			self.direction = [ self.speed*(dx/length), self.speed*(dy/length) ]
		clock.schedule_interval(self.check_dir, .1)   # check direction to target once every 0.1 seconds
		
	def draw (self):
		glPushMatrix()
		glTranslatef (game.map.llx + (game.map.cellsize * self.pos[0]),  game.map.lly + (game.map.cellsize * self.pos[1]), 0)
		glRotatef (self.dir, 0, 0, 1)
		missile_3_sprite.blit (0,0)
		glPopMatrix()
		
	def check_dir (self, dt):
		dx = self.target.pos[0]-self.pos[0]
		dy = self.target.pos[1]-self.pos[1]
		self.dir = math.atan2 (dy, dx) * 57.2957795 + 90
		
	def update (self, tick):
		
		# add particle fx here
		game.particles.append (particle_blue_trail(self.pos))
		#if random.random()>0.4: game.particles.append (particle_smoke( self.pos))
		
		self.speed += self.accel * tick
			
		if self.target.alive:
			dx = self.target.pos[0]-self.pos[0]
			dy = self.target.pos[1]-self.pos[1]
			if abs(dx) < 0.5 and abs(dy) < 0.5:
				# HIT TARGET
				if audio: audio_hit.play()
				
				# do shockwave
				game.particles.append ( particle_shockwave (self.pos, 0.5, 1300))
				
				# damage all within damage radius
				for enemy in game.enemies:
					# get squared distance
					sd = (self.pos[0]-enemy.pos[0])**2 + (self.pos[1]-enemy.pos[1])**2
					if sd < self.damage_range_sq:
						enemy.health-=self.damage
						
				game.projectiles.remove (self)
				clock.unschedule (self.check_dir)	# remove direction check from scheduler
			else:
				speed = self.speed * tick
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
			# target dead - set up dummy target to aim for
			self.target = DummyTarget (self.target.pos)
			
			# commented out code below - used only if dummy target idea not used
			#game.particles.append ( particle_shockwave (self.pos))
			#game.projectiles.remove (self)
				
class Purple_laser (object):
	def __init__(self, pos, target, duration):
		self.pos = pos
		self.time_alive = 0			
		self.duration = duration
		self.target = target
		self.cx = (pos[0]*game.map.cellsize)+game.map.llx
		self.cy = (pos[1]*game.map.cellsize)+game.map.lly
		dx = target.pos[0]-pos[0]
		dy = target.pos[1]-pos[1]
		self.dir = math.atan2 (-dy, -dx) * 57.2957795 + 90
		self.length = (math.sqrt (dx**2 + dy**2) * game.map.cellsize)
		
			
	def draw(self):
		glPushMatrix()
		glTranslatef (self.cx,  self.cy, 0)
		
		glRotatef (self.dir, 0, 0, 1)
		purple_laser_sprite.blit (0,0,height=self.length)
		purple_laser_source2_sprite.blit (0,0)
		glPopMatrix()
		
	def update(self,dt):
		self.time_alive += dt
		if self.time_alive>self.duration or not self.target.alive:
			game.projectiles.remove (self)
		else:
			dx = self.target.pos[0]-self.pos[0]
			dy = self.target.pos[1]-self.pos[1]
			self.dir = math.atan2 (-dy, -dx) * 57.2957795 + 90
			self.length = (math.sqrt (dx**2 + dy**2) * game.map.cellsize)
			
			
			
class Lightning_1 (object):
	def __init__(self, pos, target_pos):
		self.pos = pos
		self.time_alive = 0			
		self.duration = 0.1
		self.cx = (pos[0]*game.map.cellsize)+game.map.llx
		self.cy = (pos[1]*game.map.cellsize)+game.map.lly
		dx = target_pos[0]-pos[0]
		dy = target_pos[1]-pos[1]
		self.dir = math.atan2 (-dy, -dx) * 57.2957795 + 90
		self.length = (math.sqrt (dx**2 + dy**2) * game.map.cellsize)
		
			
	def draw(self):
		glPushMatrix()
		glTranslatef (self.cx,  self.cy, 0)
		glRotatef (self.dir, 0, 0, 1)
		lightning_1_sprite.blit (0,0, height=self.length)
		purple_laser_source2_sprite.blit (0,0)
		glPopMatrix()
		
	def update(self,dt):
		self.time_alive += dt
		if self.time_alive>self.duration:
			game.projectiles.remove (self)
			
			
class Lightning_2 (object):
	def __init__(self, pos, target_pos):
		self.pos = pos
		self.time_alive = 0			
		self.duration = 0.1
		self.cx = (pos[0]*game.map.cellsize)+game.map.llx
		self.cy = (pos[1]*game.map.cellsize)+game.map.lly
		dx = target_pos[0]-pos[0]
		dy = target_pos[1]-pos[1]
		self.dir = math.atan2 (-dy, -dx) * 57.2957795 + 90
		self.length = (math.sqrt (dx**2 + dy**2) * game.map.cellsize)
		
			
	def draw(self):
		glPushMatrix()
		glTranslatef (self.cx,  self.cy, 0)
		glRotatef (self.dir, 0, 0, 1)
		lightning_2_sprite.blit (0,0, height=self.length)
		lightning_source_sprite.blit (0,0)
		glPopMatrix()
		
	def update(self,dt):
		self.time_alive += dt
		if self.time_alive>self.duration:
			game.projectiles.remove (self)
		
			
			
			
		
class Bullet_1(object):
	def __init__ (self, pos, target, damage):
		self.pos=pos
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
		bullet_1_sprite.blit (game.map.llx + (game.map.cellsize * self.pos[0]) , game.map.lly + (game.map.cellsize * self.pos[1]) )
		
	def update (self, tick):
		if self.target.alive:
			dx = self.target.pos[0]-self.pos[0]
			dy = self.target.pos[1]-self.pos[1]
			if abs(dx) < 0.5 and abs(dy) < 0.5:
				# HIT TARGET
				if audio: audio_hit.play()
				# Spawn hit particles
				# get screen coords
				sx = game.map.llx + (game.map.cellsize * self.pos[0])
				sy = game.map.lly + (game.map.cellsize * self.pos[1])
				
				# create some particles - TODO: check fps is high enough
				g = game.particles.append
				for x in xrange(8):
					g (particle_small_hit ([sx,sy]))
				
				self.target.health -= self.damage
				self.target.time_since_hit = 0
				
				game.projectiles.remove (self)
			else:
				speed = self.speed * tick
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
			self.pos[0] += self.direction[0] 
			self.pos[1] += self.direction[1]
			

class Bullet_2(object):
	def __init__ (self, pos, target, damage):
		self.pos=pos
		self.target=target
		self.damage=damage
		self.speed = 10
		self.dir=0
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
		glTranslatef (game.map.llx + (game.map.cellsize * self.pos[0]),  game.map.lly + (game.map.cellsize * self.pos[1]), 0)
		glRotatef (self.dir, 0, 0, 1)
		#bullet_2_sprite.blit (game.map.llx + (game.map.cellsize * self.pos[0]) , game.map.lly + (game.map.cellsize * self.pos[1]) )
		bullet_2_sprite.blit (0,0)
		glPopMatrix()
		
		
	def update (self, tick):
		self.dir+=700*tick

		if self.target.alive:
			dx = self.target.pos[0]-self.pos[0]
			dy = self.target.pos[1]-self.pos[1]
			if abs(dx) < 0.5 and abs(dy) < 0.5:
				# HIT TARGET
				self.target.health -= self.damage
				if audio: audio_hit.play()
				
				if self.target.health>0:
					# Spawn hit particles
					# set up locals
					g=game.particles.append
					# get screen coords
					sx = game.map.llx + (game.map.cellsize * self.pos[0])
					sy = game.map.lly + (game.map.cellsize * self.pos[1])
					g (particle_small_hit ([sx,sy]))
					g (particle_small_hit ([sx,sy]))
					g (particle_small_hit ([sx,sy]))
					g (particle_small_hit ([sx,sy]))
					g (particle_small_hit ([sx,sy]))
					g (particle_small_hit ([sx,sy]))

				game.projectiles.remove (self)
			else:
				speed = self.speed * tick
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
			self.pos[0] += self.direction[0]
			self.pos[1] += self.direction[1]
			
			
			
class Bullet_3(object):
	def __init__ (self, pos, target, damage):
		self.pos=pos
		self.target=target
		self.damage=damage
		self.speed = 8
		self.dir=0
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
		glTranslatef (game.map.llx + (game.map.cellsize * self.pos[0]),  game.map.lly + (game.map.cellsize * self.pos[1]), 0)
		glRotatef (self.dir, 0, 0, 1)
		#bullet_2_sprite.blit (game.map.llx + (game.map.cellsize * self.pos[0]) , game.map.lly + (game.map.cellsize * self.pos[1]) )
		bullet_3_sprite.blit (0,0)
		glPopMatrix()
		
		
	def update (self, tick):
		self.dir+=1200*tick
		
		# do glowing blue trail
		game.particles.append (particle_blue_trail (self.pos))
			
		if self.target.alive:
			dx = self.target.pos[0]-self.pos[0]
			dy = self.target.pos[1]-self.pos[1]
			if abs(dx) < 0.5 and abs(dy) < 0.5:
				# HIT TARGET
				if audio: audio_hit.play()
				
				self.target.health -= self.damage
				game.projectiles.remove (self)
			else:
				speed = self.speed * tick
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
			self.pos[0] += self.direction[0]
			self.pos[1] += self.direction[1]
			
			

class Rail_1(object):
	def __init__ (self, pos, target, damage):
		# dir set at init phase - determined by angle to target
		self.pos=pos
		self.target=target
		self.damage=damage
		self.speed = 24
		self.dir=0
		dx = target.pos[0]-pos[0]
		dy = target.pos[1]-pos[1]
		self.dir = math.atan2 (dy, dx) * 57.2957795 + 90
		length = math.sqrt (dx**2 + dy**2)
		if dx==0:
			self.direction=[0,self.speed*dy]
		elif dy==0:
			self.direction=[self.speed*dx,0]
		else:
			self.direction = [ self.speed*(dx/length), self.speed*(dy/length) ]
		
	def draw (self):
		glPushMatrix()
		glTranslatef (game.map.llx + (game.map.cellsize * self.pos[0]),  game.map.lly + (game.map.cellsize * self.pos[1]), 0)
		glRotatef (self.dir, 0, 0, 1)
		rail_1_sprite.blit (0,0)
		glPopMatrix()
		
		
	def update (self, tick):
		
		# add particle fx here
		#game.particles.append (particle_small_hit( [ game.map.llx + (game.map.cellsize * self.pos[0]), game.map.lly + (game.map.cellsize * self.pos[1])]     ))
			
		if self.target.alive:
			dx = self.target.pos[0]-self.pos[0]
			dy = self.target.pos[1]-self.pos[1]
			if abs(dx) < 0.5 and abs(dy) < 0.5:
				# HIT TARGET
				if audio: audio_hit.play()
				# Spawn hit particles - removed for now - the rail hits a lot of times per sec, so leave them out
				# get screen coords
				#sx = game.map.llx + (game.map.cellsize * self.pos[0])
				#sy = game.map.lly + (game.map.cellsize * self.pos[1])
				#for x in xrange(6):
				#	game.particles.append (particle_small_hit ([sx,sy]))
				self.target.health -= self.damage
				game.projectiles.remove (self)
			else:
				speed = self.speed * tick
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
			self.pos[0] += self.direction[0]
			self.pos[1] += self.direction[1]
			
			
			
class Rail_2(object):
	def __init__ (self, pos, target, damage):
		# dir set at init phase - determined by angle to target
		self.pos=pos
		self.target=target
		self.damage=damage
		self.speed = 24
		self.dir=0
		dx = target.pos[0]-pos[0]
		dy = target.pos[1]-pos[1]
		self.dir = math.atan2 (dy, dx) * 57.2957795 + 90
		length = math.sqrt (dx**2 + dy**2)
		if dx==0:
			self.direction=[0,self.speed*dy]
		elif dy==0:
			self.direction=[self.speed*dx,0]
		else:
			self.direction = [ self.speed*(dx/length), self.speed*(dy/length) ]
		
	def draw (self):
		glPushMatrix()
		glTranslatef (game.map.llx + (game.map.cellsize * self.pos[0]),  game.map.lly + (game.map.cellsize * self.pos[1]), 0)
		glRotatef (self.dir, 0, 0, 1)
		rail_2_sprite.blit (0,0)
		glPopMatrix()
		
		
	def update (self, tick):
		
		# add particle fx here
		#game.particles.append (particle_small_hit( [ game.map.llx + (game.map.cellsize * self.pos[0]), game.map.lly + (game.map.cellsize * self.pos[1])]     ))
			
		if self.target.alive:
			dx = self.target.pos[0]-self.pos[0]
			dy = self.target.pos[1]-self.pos[1]
			if abs(dx) < 0.5 and abs(dy) < 0.5:
				# HIT TARGET
				if audio: audio_hit.play()
				# Spawn hit particles - removed for now - the rail hits a lot of times per sec, so leave them out
				# get screen coords
				#sx = game.map.llx + (game.map.cellsize * self.pos[0])
				#sy = game.map.lly + (game.map.cellsize * self.pos[1])
				#for x in xrange(6):
				#	game.particles.append (particle_small_hit ([sx,sy]))
				self.target.health -= self.damage
				game.projectiles.remove (self)
			else:
				speed = self.speed * tick
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
			self.pos[0] += self.direction[0]
			self.pos[1] += self.direction[1]
			



class Rail_3(object):
	def __init__ (self, pos, target, damage):
		# dir set at init phase - determined by angle to target
		self.pos=pos
		self.target=target
		self.damage=damage
		self.speed = 24
		self.dir=0
		dx = target.pos[0]-pos[0]
		dy = target.pos[1]-pos[1]
		self.dir = math.atan2 (dy, dx) * 57.2957795 + 90
		length = math.sqrt (dx**2 + dy**2)
		if dx==0:
			self.direction=[0,self.speed*dy]
		elif dy==0:
			self.direction=[self.speed*dx,0]
		else:
			self.direction = [ self.speed*(dx/length), self.speed*(dy/length) ]
		
	def draw (self):
		glPushMatrix()
		glTranslatef (game.map.llx + (game.map.cellsize * self.pos[0]),  game.map.lly + (game.map.cellsize * self.pos[1]), 0)
		glRotatef (self.dir, 0, 0, 1)
		rail_3_sprite.blit (0,0)
		glPopMatrix()
		
		
		
		
	def update (self, tick):
		
		# add particle fx here
		# do white trail
		game.particles.append (particle_white_trail (self.pos))
		
		if self.target.alive:
			dx = self.target.pos[0]-self.pos[0]
			dy = self.target.pos[1]-self.pos[1]
			if abs(dx) < 0.5 and abs(dy) < 0.5:
				# HIT TARGET
				if audio: audio_hit.play()
				# Spawn hit particles - removed for now - the rail hits a lot of times per sec, so leave them out
				# get screen coords
				#sx = game.map.llx + (game.map.cellsize * self.pos[0])
				#sy = game.map.lly + (game.map.cellsize * self.pos[1])
				#for x in xrange(6):
				#	game.particles.append (particle_small_hit ([sx,sy]))
				self.target.health -= self.damage
				game.projectiles.remove (self)
			else:
				speed = self.speed * tick
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
			self.pos[0] += self.direction[0]
			self.pos[1] += self.direction[1]


			
			

			
			
			
#
#	TOWER CLASSES
#
		
	









	

class Tower (object):
	""" Tower Base Class """
	def __init__ (self, position=(0,0)):
		print "Creating base tower class at: ", position
		self.highlight=False
		self.pos = position
		self.center = (position[0]+1, position[1]+1)
		# screen coords
		self.llx = 0
		self.lly = 0
		self.urx = 0
		self.ury = 0
		self.cx = 0
		self.cy = 0
		
		self.direction = 0
		self.active = False
		self.target = None
		self.cost = 5
		self.range_sq = 4
		self.range = self.range_sq * self.range_sq
		
		self.upgrade_cost = 40
		self.upgrade_time = 2
		self.damage_per_shot = 3
		self.sell_price = 3
		self.time_between_shots = 1.2
		self.time_since_last_shot = 3
		self.target_mode = 0	# 0 - none, 1 strong 2 weak 3 fast 4 slow 5 near 6 end of path
		self.upgradeable = True

		self.mouse_over = False
		
		self.base_tex = None
		self.tower_tex = None
	
	def on_mouse_motion(self, x, y, dx, dy):
		if (x>self.llx and x<self.urx and y>self.lly and y<self.ury) and not game.state & game.states['paused']:
			self.mouse_over=True
			game.highlighted=self
		else:
			self.mouse_over=False
			
	def on_mouse_release(self, x, y, buttons, modifiers):
		if self.mouse_over and buttons & mouse.LEFT and not game.state & game.states['paused'] and not game.deploying:
			game.selected=self
	
	def deploy (self):
		# make map squares impassable
		game.map.cell[mymouse.dx][mymouse.dy].passable=False
		game.map.cell[mymouse.dx+1][mymouse.dy].passable=False
		game.map.cell[mymouse.dx+1][mymouse.dy+1].passable=False
		game.map.cell[mymouse.dx][mymouse.dy+1].passable=False
		# put pointer to tower in map cells
		game.map.cell[mymouse.dx][mymouse.dy].tower=self
		game.map.cell[mymouse.dx+1][mymouse.dy].tower=self
		game.map.cell[mymouse.dx+1][mymouse.dy+1].tower=self
		game.map.cell[mymouse.dx][mymouse.dy+1].tower=self
		self.pos = (mymouse.dx, mymouse.dy)
		
		# DEBUG
		print "Deploying to: ",self.pos
		
		self.center = (self.pos[0]+1, self.pos[1]+1)
		# get screen coord area
		self.llx = game.map.llx + self.pos[0] * game.map.cellsize
		self.lly = game.map.lly + self.pos[1] * game.map.cellsize
		self.urx = game.map.llx + (self.pos[0]+2) * game.map.cellsize
		self.ury = game.map.lly + (self.pos[1]+2) * game.map.cellsize
		self.cx = game.map.llx + self.center[0] * game.map.cellsize
		self.cy = game.map.lly + self.center[1] * game.map.cellsize
		
		if game.map.recalc_routes():	# recalc routes
			#game.particles.append (particle_smoke ( [self.pos[0]+1, self.pos[1]+1] ))
			game.towers.append ( self )
			window.push_handlers(self)
			return True
		else:
			# make routes passable again - no path for 1 or more routes found
			game.map.cell[mymouse.dx][mymouse.dy].passable=True
			game.map.cell[mymouse.dx+1][mymouse.dy].passable=True
			game.map.cell[mymouse.dx+1][mymouse.dy+1].passable=True
			game.map.cell[mymouse.dx][mymouse.dy+1].passable=True
			# remove pointers to tower in cells
			game.map.cell[mymouse.dx][mymouse.dy].tower=None
			game.map.cell[mymouse.dx+1][mymouse.dy].tower=None
			game.map.cell[mymouse.dx+1][mymouse.dy+1].tower=None
			game.map.cell[mymouse.dx][mymouse.dy+1].tower=None
			game.map.recalc_routes()	# recalc original routes
			return False	# tell calling function that deploy failed
		
	def deploy_fast (self):	# used when re-checking of paths is not needed - ie. for an upgrade
		# get screen coord area
		self.llx = game.map.llx + self.pos[0] * game.map.cellsize
		self.lly = game.map.lly + self.pos[1] * game.map.cellsize
		self.urx = game.map.llx + (self.pos[0]+2) * game.map.cellsize
		self.ury = game.map.lly + (self.pos[1]+2) * game.map.cellsize
		self.cx = game.map.llx + self.center[0] * game.map.cellsize
		self.cy = game.map.lly + self.center[1] * game.map.cellsize
		game.towers.append ( self )
		window.push_handlers(self)	
			
	def sell (self):
		window.remove_handlers(self)
		self.mouse_over = False # BUGFIX: range still drawn when S key used to sell and mouse over spot where tower was
		game.towers.remove(self)
		game.selected = None
		if game.state & game.states['pregame']:
			# take no time
			game.towers.append ( aSell (self.pos[0],self.pos[1], 0.01) )
			# and free
			game.credits += self.cost
		else:
			game.towers.append ( aSell (self.pos[0],self.pos[1], game.map.sell_time) )
			game.credits += self.sell_price
			game.map.sell_time *= game.map.sell_time_multiplier

	def upgrade (self):
		self.mouse_over = False
		pos=copy.copy(self.pos)
		upgrade_to = self.get_upgrade()
		if game.state & game.states['pregame']:
			self.upgrade_time = 0.01
		game.towers.append ( anUpgrade (pos[0], pos[1], self.upgrade_time, upgrade_to , copy.copy(self.target_mode) ))
		window.remove_handlers(self)
		game.towers.remove( self )
		game.selected=None

	def get_upgrade(self):
		pass	

	def update (self, dt):
		pass
		
	def draw (self):
		pass
	
	def draw_selection (self):
		selected_tex.blit (self.llx, self.lly)
		
	def draw_highlight (self):
		pass		
		
			



class Berserker (Tower):
	""" Berserker Tower base class """
	def __init__ (self, position=(0,0)):
		super (Berserker, self).__init__(position) # call parent init
		
		
	def draw (self, alpha=1):
		# base
		self.base_tex.blit (self.llx, self.lly)
		# turret
		glPushMatrix()
		glTranslatef (self.cx, self.cy, 0)
		glRotatef (-self.dir, 0, 0, 1)
		self.tower_tex.blit (0,0)
		glPopMatrix()
		
	def fire_projectile(self):
		pass
		
	def draw_highlight (self):
		width = self.range_sq * game.map.cellsize * 2
		offset = width * 0.5
		range_sprite.blit ( -offset + self.cx, -offset + self.cy, width=width, height=width)
	
	def update (self,dt):
		self.dir += self.spin_speed * dt
	
		if self.spin_speed > 0 and self.target is None:
				self.spin_speed-=self.spin_accel
				if self.spin_speed < 0:
					self.spin_speed = 0
			
		self.time_since_last_shot+=dt
		if self.time_since_last_shot > self.time_between_shots:
			# find a new target
			nearby_enemies=[]
			# create locals for speed
			cx=self.center[0]
			cy=self.center[1]
			for enemy in game.enemies:
				# get squared distance
				sd = (cx-enemy.pos[0])**2 + (cy-enemy.pos[1])**2
				if sd < self.range:
					nearby_enemies.append (enemy)	
			if nearby_enemies:
				# this is berserker, so just pick random targets
				n = len(nearby_enemies)
				self.target = nearby_enemies[ int(random.random()* n) ]
				self.fire_projectile()
			else:
				# no ground units near, check for flying
				self.target=None	# set to none before checking for airborne
				if game.flying_enemies:
					for enemy in game.flying_enemies:
						sd = (cx-enemy.pos[0])**2 + (cy-enemy.pos[1])**2
						if sd < self.range:
							# got a flying beastie :)
							self.target = enemy
							self.fire_projectile()
							break
					
		if self.target and self.target.alive:
			# if target also still alive
			# spin up in anticipation
			self.spin_speed+=self.spin_accel
			if self.spin_speed>self.max_spin_speed:
				self.spin_speed=self.max_spin_speed


				
class Berserker_1 (Berserker):
	def __init__ (self, position=(0,0)):
		super (Berserker_1,self).__init__(position)

		self.spin_accel = 1
		self.max_spin_speed = 199
		self.spin_speed = 0
		self.dir = 0
		
		self.cost = 15
		self.range_sq = 5
		self.range = self.range_sq * self.range_sq
		self.upgrade_cost = 65
		self.upgrade_time = 3
		self.damage_per_shot = 3
		self.sell_price = 10
		self.time_between_shots = 0.45
		self.time_since_last_shot = 3
		self.target_mode = 0	# 0 - none, 1 strong 2 weak 3 fast 4 slow 5 near 6 end of path
		self.upgradeable = True
		
		self.base_tex = cannon_1_base_sprite
		self.tower_tex = berserker_1_turret_sprite
	
	def get_upgrade(self):
		return Berserker_2 (copy.copy(self.pos))
		
	def fire_projectile(self):
		if audio: audio_rail_1_fire.play()
		game.projectiles.append (Rail_1 ( [self.pos[0]+1, self.pos[1]+1], self.target, self.damage_per_shot))
		self.time_since_last_shot=0


class Berserker_2 (Berserker):
	def __init__ (self, position=(0,0)):
		super (Berserker_2,self).__init__(position)

		self.spin_accel = 4
		self.max_spin_speed = 800
		self.spin_speed = 0
		self.dir = 0
		
		self.cost = 75
		self.range_sq = 5
		self.range = self.range_sq * self.range_sq
		self.upgrade_cost = 150
		self.upgrade_time = 4
		self.damage_per_shot = 20
		self.sell_price = 60
		self.time_between_shots = 0.32
		self.time_since_last_shot = 3
		self.target_mode = 0	# 0 - none, 1 strong 2 weak 3 fast 4 slow 5 near 6 end of path
		self.upgradeable = True
		
		self.base_tex = cannon_2_base_sprite
		self.tower_tex = berserker_1_turret_sprite
	
	def get_upgrade(self):
		return Berserker_3 (copy.copy(self.pos))
		
	def fire_projectile(self):
		if audio: audio_rail_1_fire.play()
		game.projectiles.append (Rail_2 ( [self.pos[0]+1, self.pos[1]+1], self.target, self.damage_per_shot))
		self.time_since_last_shot=0
		self.time_between_shots = random.random() + 0.1

class Berserker_3 (Berserker):
	def __init__ (self, position=(0,0)):
		super (Berserker_3,self).__init__(position)

		self.spin_accel = 6
		self.max_spin_speed = 1400
		self.spin_speed = 0
		self.dir = 0
		
		self.cost = 150
		self.range_sq = 5.5
		self.range = self.range_sq * self.range_sq
		self.upgrade_cost = 255
		self.upgrade_time = 5
		self.damage_per_shot = 40
		self.sell_price = 125
		self.time_between_shots = 0.22
		self.time_since_last_shot = 3
		self.target_mode = 0	# 0 - none, 1 strong 2 weak 3 fast 4 slow 5 near 6 end of path
		self.upgradeable = False
		
		self.base_tex = cannon_3_base_sprite
		self.tower_tex = berserker_1_turret_sprite
	
	def get_upgrade(self):
		return Berserker_3 (copy.copy(self.pos))		

	def fire_projectile(self):
		if audio: audio_rail_1_fire.play()
		game.projectiles.append (Rail_3 ( [self.pos[0]+1, self.pos[1]+1], self.target, self.damage_per_shot))
		self.time_since_last_shot=0


		

class ICBM (Tower):
	""" Missile Launcher Tower base class """
	def __init__ (self, position=(0,0)):
		super (ICBM, self).__init__(position) # call parent init
		
	def draw (self, alpha=1):
		self.base_tex.blit (self.llx, self.lly)
		self.tower_tex.blit (self.llx+24, self.lly+26)

	def fire_projectile(self):
		pass
	
	def draw_highlight (self):
		width = self.range_sq * game.map.cellsize * 2
		offset = width * 0.5
		range_sprite.blit ( -offset + self.cx, -offset + self.cy, width=width, height=width)
		draw_circle (self.cx, self.cy, self.min_range_sq, 0.15)
	
	def update (self,dt):
		self.time_since_last_shot+=dt
		if self.time_since_last_shot > self.time_between_shots:
			# find a new target
			nearby_enemies=[]
			# create locals for speed
			cx=self.center[0]
			cy=self.center[1]
			for enemy in game.enemies:
				# get squared distance
				sd = (cx-enemy.pos[0])**2 + (cy-enemy.pos[1])**2
				if sd < self.range and sd > self.min_range:
					nearby_enemies.append (enemy)
			if nearby_enemies:
				self.target = nearby_enemies[0]
			else:
				self.target = None
				return 0
					
		if self.target and self.target.alive:
			# if target also still alive
			# check target is still in range
			sd = (self.center[0]-self.target.pos[0])**2 + (self.center[1]-self.target.pos[1])**2
			if sd < self.range and sd > self.min_range:
				# have target, can we fire?
				if self.time_since_last_shot > self.time_between_shots:
					# yes we can
					self.fire_projectile()
			else:
				# old target left range
				self.target = None
		else:
			self.target = None


class ICBM_1 (ICBM):
	def __init__ (self, position=(0,0)):
		super (ICBM_1,self).__init__(position)	# call init of parent
		self.cost = 50
		self.range_sq = 8
		self.min_range_sq = 4
		self.range = self.range_sq * self.range_sq
		self.min_range = self.min_range_sq * self.min_range_sq
		self.upgrade_cost = 150
		self.upgrade_time = 4
		self.damage_per_shot = 30
		self.sell_price = 35
		self.time_between_shots = 4
		self.time_since_last_shot = 3
		self.base_tex = cannon_1_base_sprite
		self.tower_tex = icbm_1_turret_sprite 
	
	def get_upgrade(self):
		return ICBM_2 (copy.copy(self.pos))
		
	def fire_projectile(self):
		if audio: audio_cannon_1_fire.play()
		game.projectiles.append (Missile_1 ( [self.pos[0]+1, self.pos[1]+1], self.target, self.damage_per_shot))
		game.particles.append (particle_smoke ( [self.pos[0]+1, self.pos[1]+1] ))
		self.time_since_last_shot=0		

class ICBM_2 (ICBM):
	def __init__ (self, position=(0,0)):
		super (ICBM_2,self).__init__(position)	# call init of parent
		self.cost = 150
		self.range_sq = 9
		self.min_range_sq = 5
		self.range = self.range_sq * self.range_sq
		self.min_range = self.min_range_sq * self.min_range_sq
		self.upgrade_cost = 250
		self.upgrade_time = 7
		self.damage_per_shot = 80
		self.sell_price = 35
		self.time_between_shots = 5
		self.time_since_last_shot = 6
		self.base_tex = cannon_2_base_sprite
		self.tower_tex = icbm_1_turret_sprite 
	
	def get_upgrade(self):
		return ICBM_3 (copy.copy(self.pos))
		
	def fire_projectile(self):
		if audio: audio_cannon_1_fire.play()
		game.projectiles.append (Missile_2 ( [self.pos[0]+1, self.pos[1]+1], self.target, self.damage_per_shot))
		game.particles.append (particle_smoke ( [self.pos[0]+1, self.pos[1]+1] ))
		self.time_since_last_shot=0		

class ICBM_3 (ICBM):
	def __init__ (self, position=(0,0)):
		super (ICBM_3,self).__init__(position)	# call init of parent
		self.cost = 250
		self.range_sq = 10
		self.min_range_sq = 4
		self.range = self.range_sq * self.range_sq
		self.min_range = self.min_range_sq * self.min_range_sq
		self.upgrade_cost = 450
		self.upgrade_time = 10
		self.damage_per_shot = 280
		self.sell_price = 215
		self.time_between_shots = 5
		self.time_since_last_shot = 6
		self.base_tex = cannon_3_base_sprite
		self.tower_tex = icbm_1_turret_sprite 
		
		self.upgradeable=False
	
	def get_upgrade(self):
		return Cannon_3 (copy.copy(self.pos))
		
	def fire_projectile(self):
		if audio: audio_cannon_1_fire.play()
		game.projectiles.append (Missile_3 ( [self.pos[0]+1, self.pos[1]+1], self.target, self.damage_per_shot))
		game.particles.append (particle_smoke ( [self.pos[0]+1, self.pos[1]+1] ))
		self.time_since_last_shot=0	
		
			

		

class Cannon (Tower):
	""" Photon Cannon Tower base class """
	def __init__ (self, position=(0,0)):
		super (Cannon, self).__init__(position) # call parent init
		
	def draw (self, alpha=1):
		# base
		glPushMatrix()
		glTranslatef (self.llx, self.lly, 0)
		glCallList(self.base_tex)
		glPopMatrix()
		# turret
		glPushMatrix()
		glTranslatef (self.cx, self.cy, 0)
		glRotatef (-self.direction, 0, 0, 1)
		#self.tower_tex.blit (0,0)
		glCallList(self.tower_tex)
		glPopMatrix()
		
	def fire_projectile(self):
		pass
	
	def draw_highlight (self):
		width = self.range_sq * game.map.cellsize * 2
		offset = width * 0.5
		range_sprite.blit ( -offset + self.cx, -offset + self.cy, width=width, height=width)
	
	def update (self,dt):
		self.time_since_last_shot+=dt
		if self.time_since_last_shot > self.time_between_shots:
			# find a new target
			nearby_enemies=[]
			# create locals for speed
			cx=self.center[0]
			cy=self.center[1]
			for enemy in game.enemies:
				# get squared distance
				sd = (cx-enemy.pos[0])**2 + (cy-enemy.pos[1])**2
				if sd < self.range:
					nearby_enemies.append ((enemy, sd, enemy.get_path_distance_left() ))	# create list of enemy, dist, and path length remaining
			if nearby_enemies:
				if self.target_mode == 6:	# nearest to end of path
					enemy_path_left=99999
					for near_enemy in nearby_enemies:
						if near_enemy[2] < enemy_path_left:
							enemy_path_left=near_enemy[2]
							self.target = near_enemy[0]	
				elif self.target_mode == 5:	# nearest to tower
					closest=99999
					for near_enemy in nearby_enemies:
						if near_enemy[1] < closest:
							closest = near_enemy[1]
							self.target = near_enemy[0]
				elif self.target_mode == 1:	# strongest
					strongest=-1
					for near_enemy in nearby_enemies:
						if near_enemy[0].health > strongest:
							strongest = near_enemy[0].health
							self.target = near_enemy[0]
				elif self.target_mode == 2:	# weakest
					strongest=99999
					for near_enemy in nearby_enemies:
						if near_enemy[0].health < strongest:
							strongest = near_enemy[0].health
							self.target = near_enemy[0]
				elif self.target_mode == 3:	# fastest
					fastest=0
					for near_enemy in nearby_enemies:
						if near_enemy[0].speed > fastest:
							fastest = near_enemy[0].speed
							self.target = near_enemy[0]
				elif self.target_mode == 4:	# slowest
					fastest=99999
					for near_enemy in nearby_enemies:
						if near_enemy[0].speed < fastest:
							fastest = near_enemy[0].speed
							self.target = near_enemy[0]
			else:
				# now check for airborne units
				if game.flying_enemies:
					for enemy in game.flying_enemies:
						sd = (cx-enemy.pos[0])**2 + (cy-enemy.pos[1])**2
						if sd < self.range:
							# got a flying beastie :)
							self.target = enemy
							break
				else:
					# speed up processing by putting in a little delay to next check for target
					self.time_since_last_shot = self.time_between_shots * 0.9
					self.target = None
					return 0
					
		if self.target and self.target.alive:
			# if target also still alive
			# check target is still in range
			sd = (self.center[0]-self.target.pos[0])**2 + (self.center[1]-self.target.pos[1])**2
			if sd < self.range:
				# have target, can we fire?
				if self.time_since_last_shot > self.time_between_shots:
					# yes we can
					self.fire_projectile()
				# turn turret to face target
				# get angle in degrees from turret to target
				dx = self.center[0] - self.target.pos[0]
				dy = self.center[1] - self.target.pos[1]
				self.direction = math.atan2 (dy, -dx) * 57.2957795 + 90
			else:
				# old target left range
				self.target = None
		else:
			self.target = None
		
		
class Cannon_1 (Cannon):
	def __init__ (self, position=(0,0)):
		super (Cannon_1,self).__init__(position)	# call init of parent
		self.cost = 5
		self.range_sq = 4
		self.range = self.range_sq * self.range_sq
		self.upgrade_cost = 25
		self.upgrade_time = 2
		self.damage_per_shot = 4
		self.sell_price = 3
		self.time_between_shots = 1.6
		self.time_since_last_shot = 3
		self.base_tex = 7
		self.tower_tex = 8 
		
	def fire_projectile(self):
		if audio: audio_cannon_1_fire.play()
		game.projectiles.append (Bullet_1 ( [self.pos[0]+1, self.pos[1]+1], self.target, self.damage_per_shot))
		self.time_since_last_shot=0
	
	def get_upgrade(self):
		return Cannon_2 (copy.copy(self.pos))
		
	def update (self,dt):
		# override Cannon class update - as this one doesnt have AI
		self.time_since_last_shot+=dt
		if self.time_since_last_shot > self.time_between_shots and self.target is None:
			# find a new target
			nearby_enemies=[]
			# create locals for speed
			cx=self.center[0]
			cy=self.center[1]
			for enemy in game.enemies:
				# get squared distance
				sd = (cx-enemy.pos[0])**2 + (cy-enemy.pos[1])**2
				if sd < self.range:
					self.target = enemy
					return 0
			else:
				# now check for airborne units
				if game.flying_enemies:
					for enemy in game.flying_enemies:
						sd = (cx-enemy.pos[0])**2 + (cy-enemy.pos[1])**2
						if sd < self.range:
							# got a flying beastie :)
							self.target = enemy
							break
				else:
					# speed up processing by putting in a little delay to next check for target
					self.time_since_last_shot = self.time_between_shots * 0.9
					self.target = None
					return 0
					
		if self.target and self.target.alive:
			# if target also still alive
			# check target is still in range
			sd = (self.center[0]-self.target.pos[0])**2 + (self.center[1]-self.target.pos[1])**2
			if sd < self.range:
				# have target, can we fire?
				if self.time_since_last_shot > self.time_between_shots:
					# yes we can
					self.fire_projectile()
				# turn turret to face target
				# get angle in degrees from turret to target
				dx = self.center[0] - self.target.pos[0]
				dy = self.center[1] - self.target.pos[1]
				self.direction = math.atan2 (dy, -dx) * 57.2957795 + 90
			else:
				# old target left range
				self.target = None
		else:
			self.target = None
			

class Cannon_2 (Cannon):
	def __init__ (self, position=(0,0)):
		super (Cannon_2,self).__init__(position)	# call init of parent
		self.cost = 40
		self.range_sq = 4
		self.range = self.range_sq * self.range_sq
		self.upgrade_cost = 50
		self.upgrade_time = 4
		self.damage_per_shot = 30
		self.sell_price = 30
		self.time_between_shots = 1.4
		self.time_since_last_shot = 3
		self.base_tex = 13
		self.tower_tex = 11 
		self.target_mode = 6	# VERY IMPORTANT - otherwise it will inherit target mode of 0 from lvl1 cannon tower. :)
	
	def get_upgrade(self):
		return Cannon_3 (copy.copy(self.pos))
		
	def fire_projectile(self):
		if audio: audio_cannon_1_fire.play()
		game.projectiles.append (Bullet_2 ( [self.pos[0]+1, self.pos[1]+1], self.target, self.damage_per_shot))
		self.time_since_last_shot=0
		
		
class Cannon_3 (Cannon):
	def __init__ (self, position=(0,0)):
		super (Cannon_3,self).__init__(position)	# call init of parent
		self.cost = 100
		self.range_sq = 4.5
		self.range = self.range_sq * self.range_sq
		self.upgrade_cost = 100
		self.upgrade_time = 4
		self.damage_per_shot = 140
		self.sell_price = 80
		self.time_between_shots = 2
		self.time_since_last_shot = 3
		self.base_tex = 14
		self.tower_tex = 12 
		self.upgradeable=False
	
	def get_upgrade(self):
		return Cannon_3 (copy.copy(self.pos))
	
	def fire_projectile(self):
		if audio: audio_cannon_1_fire.play()
		print "Trying to launch bullet 3"
		game.projectiles.append (Bullet_3 ( [self.pos[0]+1, self.pos[1]+1], self.target, self.damage_per_shot))
		self.time_since_last_shot=0

		
		
class Temporal (Tower):
	""" Temporal Tower base class """
	def __init__ (self, position=(0,0)):
		super (Temporal, self).__init__(position) # call parent init
		
	def draw (self, alpha=1):
		# base
		self.base_tex.blit (self.llx, self.lly)
		# turret
		self.tower_tex.blit (self.llx+24, self.lly+26)
		
	def fire_projectile(self):
		pass
	
	def draw_highlight (self):
		width = self.range_sq * game.map.cellsize * 2
		offset = width * 0.5
		range_sprite.blit ( -offset + self.cx, -offset + self.cy, width=width, height=width)
	
	def update (self,dt):
		self.time_since_last_shot+=dt
		if self.time_since_last_shot > self.time_between_shots:
			# find a new target
			nearby_enemies=[]
			# create locals for speed
			cx=self.center[0]
			cy=self.center[1]
			for enemy in game.enemies:
				# get squared distance
				sd = (cx-enemy.pos[0])**2 + (cy-enemy.pos[1])**2
				if sd < self.range:
					nearby_enemies.append (enemy)	
			if nearby_enemies:
				fastest=0
				for near_enemy in nearby_enemies:
					if near_enemy.speed > fastest:
						fastest = near_enemy.speed
						self.target = near_enemy
			else:
				self.target = None
				return 0
					
		if self.target and self.target.alive:
			# if target also still alive
			# check target is still in range
			sd = (self.center[0]-self.target.pos[0])**2 + (self.center[1]-self.target.pos[1])**2
			if sd < self.range:
				# have target, can we fire?
				if self.time_since_last_shot > self.time_between_shots:
					# yes we can
					self.fire_projectile()
			else:
				# old target left range
				self.target = None
		else:
			self.target = None		
			
			
			
			

			
			
			
		
class Temporal_1 (Temporal):
	def __init__ (self, position=(0,0)):
		super (Temporal_1,self).__init__(position)	# call init of parent
		self.cost = 20
		self.range_sq = 3
		self.range = self.range_sq * self.range_sq
		self.upgrade_cost = 50
		self.upgrade_time = 4
		self.duration = 1.0
		self.effect_time = 4
		self.speed_multiplier = 0.75
		self.sell_price = 15
		self.time_between_shots = 2
		self.time_since_last_shot = 3
		self.base_tex = cannon_1_base_sprite
		self.tower_tex = temporal_1_turret_sprite 
		self.upgradeable=True
	
	def get_upgrade(self):
		return Temporal_2 (copy.copy(self.pos))
		
	def fire_projectile(self):
		if audio: audio_cannon_1_fire.play()
		self.target.reduce_speed (self.speed_multiplier, self.effect_time)
		game.projectiles.append (Purple_laser ( (self.pos[0]+1, self.pos[1]+1) , self.target, self.duration))
		self.time_since_last_shot=0	
		
		
class Temporal_2 (Temporal):
	def __init__ (self, position=(0,0)):
		super (Temporal_2,self).__init__(position)	# call init of parent
		self.cost = 50
		self.range_sq = 4
		self.range = self.range_sq * self.range_sq
		self.upgrade_cost = 150
		self.upgrade_time = 8
		self.duration = 0.2
		self.effect_time = 5
		self.speed_multiplier = 0.65
		self.sell_price = 40
		self.time_between_shots = 1.4
		self.time_since_last_shot = 3
		self.base_tex = cannon_2_base_sprite
		self.tower_tex = temporal_1_turret_sprite 
		self.upgradeable=True
	
	def get_upgrade(self):
		return Temporal_3 (copy.copy(self.pos))
		
	def fire_projectile(self):
		if audio: audio_cannon_1_fire.play()
		self.target.reduce_speed (self.speed_multiplier, self.effect_time)
		game.particles.append ( particle_purple_shockwave( (self.cx,self.cy) ) )
		game.projectiles.append (Purple_laser ( (self.pos[0]+1, self.pos[1]+1) , self.target, self.duration))
		self.time_since_last_shot=0	
		
		
class Temporal_3 (Temporal):
	def __init__ (self, position=(0,0)):
		super (Temporal_3,self).__init__(position)	# call init of parent
		self.cost = 300
		self.range_sq = 5
		self.range = self.range_sq * self.range_sq
		self.upgrade_cost = 300
		self.upgrade_time = 8
		self.duration = 0.1
		self.effect_time = 5
		self.speed_multiplier = 0.45
		self.sell_price = 260
		self.time_between_shots = 1.0
		self.time_since_last_shot = 3
		self.base_tex = cannon_3_base_sprite
		self.tower_tex = temporal_1_turret_sprite 
		self.upgradeable=False
	
	def get_upgrade(self):
		return Temporal_2 (copy.copy(self.pos))
		
	def fire_projectile(self):
		if audio: audio_cannon_1_fire.play()
		self.target.reduce_speed (self.speed_multiplier, self.effect_time)
		game.particles.append ( particle_purple_shockwave( (self.cx,self.cy), 0.3, 900 ) )	# duration=0.2, accel=500
		game.projectiles.append (Purple_laser ( (self.pos[0]+1, self.pos[1]+1) , self.target, self.duration))
		self.time_since_last_shot=0	
		

		
class Tesla (Tower):
	""" Tesla Tower base class """
	def __init__ (self, position=(0,0)):
		super (Tesla, self).__init__(position) # call parent init
		
	def draw (self, alpha=1):
		# base
		self.base_tex.blit (self.llx, self.lly)
		# turret
		self.tower_tex.blit (self.llx+24, self.lly+26)
		
	def fire_projectile(self):
		pass
	
	def draw_highlight (self):
		width = self.range_sq * game.map.cellsize * 2
		offset = width * 0.5
		range_sprite.blit ( -offset + self.cx, -offset + self.cy, width=width, height=width)
	
	def update (self,dt):
		self.time_since_last_shot+=dt
		if self.time_since_last_shot > self.time_between_shots:
			# find a new target
			nearby_enemies=[]
			self.target = None
			# create locals for speed
			cx=self.center[0]
			cy=self.center[1]
			for enemy in game.enemies:
				# get squared distance
				sd = (cx-enemy.pos[0])**2 + (cy-enemy.pos[1])**2
				if sd < self.range:
					self.target=enemy
					
		if self.target and self.target.alive:
			# if target also still alive
			# check target is still in range
			sd = (self.center[0]-self.target.pos[0])**2 + (self.center[1]-self.target.pos[1])**2
			if sd < self.range:
				# have target, can we fire?
				if self.time_since_last_shot > self.time_between_shots:
					# yes we can
					self.fire_projectile()
			else:
				# old target left range
				self.target = None
		else:
			self.target = None		
			
	def get_closest_not_affected (self, pos):
		cx = pos[0]
		cy = pos[1]
		for enemy in game.enemies:
			# get squared distance
			sd = (cx-enemy.pos[0])**2 + (cy-enemy.pos[1])**2
			if sd < self.range and enemy.damage_per_second==0:
				return enemy
		return None

			
			
class Tesla_1 (Tesla):
	def __init__ (self, position=(0,0)):
		super (Tesla_1, self).__init__(position)	# call init of parent
		self.cost = 100
		self.range_sq = 3.5
		self.range = self.range_sq * self.range_sq
		self.upgrade_cost = 250
		self.upgrade_time = 4
		self.duration = 0.1
		self.effect_time = 6
		self.chain = 3
		self.damage_per_second = 75
		self.sell_price = 75
		self.time_between_shots = 3
		self.time_since_last_shot = 4
		self.base_tex = cannon_1_base_sprite
		self.tower_tex = tesla_1_turret_sprite 
		self.upgradeable=True
	
	def get_upgrade(self):
		return Tesla_2 (copy.copy(self.pos))
		
	def fire_projectile(self):
		if audio: audio_cannon_1_fire.play()
		self.target.damage_over_time ( self.damage_per_second, self.effect_time)
		#game.particles.append ( particle_purple_shockwave( (self.cx,self.cy), 0.3, 900 ) )	# duration=0.2, accel=500
		game.projectiles.append (Lightning_1 ( (self.pos[0]+1, self.pos[1]+1) , self.target.pos))

		count=1
		oldx = self.target.pos[0]
		oldy = self.target.pos[1]
		new_target=self.get_closest_not_affected(self.target.pos)
		while new_target and count<self.chain:
			new_target.damage_over_time ( self.damage_per_second, self.effect_time)
			game.projectiles.append (Lightning_1 ( (oldx, oldy) , new_target.pos))
			oldx = copy.copy(new_target.pos[0])
			oldy = copy.copy(new_target.pos[1])
			new_target=self.get_closest_not_affected(new_target.pos)
			count+=1
			
		self.time_since_last_shot=0		



class Tesla_2 (Tesla):
	def __init__ (self, position=(0,0)):
		super (Tesla_2, self).__init__(position)	# call init of parent
		self.cost = 250
		self.range_sq = 4.0
		self.range = self.range_sq * self.range_sq
		self.upgrade_cost = 450
		self.upgrade_time = 6
		self.duration = 0.1
		self.effect_time = 8
		self.chain = 4
		self.damage_per_second = 150
		self.sell_price = 225
		self.time_between_shots = 4
		self.time_since_last_shot = 5
		self.base_tex = cannon_2_base_sprite
		self.tower_tex = tesla_2_turret_sprite 
		self.upgradeable=False
	
	def get_upgrade(self):
		return Tesla_3 (copy.copy(self.pos))
		
	def fire_projectile(self):
		if audio: audio_cannon_1_fire.play()
		self.target.damage_over_time ( self.damage_per_second, self.effect_time)
		#game.particles.append ( particle_purple_shockwave( (self.cx,self.cy), 0.3, 900 ) )	# duration=0.2, accel=500
		game.projectiles.append (Lightning_2 ( (self.pos[0]+1, self.pos[1]+1) , self.target.pos))

		count=1
		oldx = self.target.pos[0]
		oldy = self.target.pos[1]
		new_target=self.get_closest_not_affected(self.target.pos)
		while new_target and count<self.chain:
			new_target.damage_over_time ( self.damage_per_second, self.effect_time)
			game.projectiles.append (Lightning_1 ( (oldx, oldy) , new_target.pos))
			oldx = copy.copy(new_target.pos[0])
			oldy = copy.copy(new_target.pos[1])
			new_target=self.get_closest_not_affected(new_target.pos)
			count+=1
			
		self.time_since_last_shot=0		
			


class AA (Tower):
	""" AA Tower base class """
	def __init__ (self, position=(0,0)):
		super (AA, self).__init__(position) # call parent init
		
	def draw (self, alpha=1):
		# base
		glPushMatrix()
		glTranslatef (self.llx, self.lly, 0)
		glCallList(self.base_tex)
		glPopMatrix()
		# turret
		glPushMatrix()
		glTranslatef (self.cx, self.cy, 0)
		glRotatef (-self.direction, 0, 0, 1)
		#self.tower_tex.blit (0,0)
		glCallList(self.tower_tex)
		glPopMatrix()
		
	def fire_projectile(self):
		pass
	
	def draw_highlight (self):
		width = self.range_sq * game.map.cellsize * 2
		offset = width * 0.5
		range_sprite.blit ( -offset + self.cx, -offset + self.cy, width=width, height=width)
	
	def update (self,dt):
		self.time_since_last_shot+=dt
		if self.time_since_last_shot > self.time_between_shots:
			# find a new target
			# now check for airborne units
			if game.flying_enemies:
				# create locals for speed
				cx=self.center[0]
				cy=self.center[1]
				for enemy in game.flying_enemies:
					sd = (cx-enemy.pos[0])**2 + (cy-enemy.pos[1])**2
					if sd < self.range:
						# got a flying beastie :)
						self.target = enemy
						break
			else:
				# speed up processing by putting in a little delay to next check for target
				self.time_since_last_shot = self.time_between_shots * 0.9
				self.target = None
				return 0
					
		if self.target and self.target.alive:
			# if target also still alive
			# check target is still in range
			sd = (self.center[0]-self.target.pos[0])**2 + (self.center[1]-self.target.pos[1])**2
			if sd < self.range:
				# have target, can we fire?
				if self.time_since_last_shot > self.time_between_shots:
					# yes we can
					self.fire_projectile()
				# turn turret to face target
				# get angle in degrees from turret to target
				dx = self.center[0] - self.target.pos[0]
				dy = self.center[1] - self.target.pos[1]
				self.direction = math.atan2 (dy, -dx) * 57.2957795 + 90
			else:
				# old target left range
				self.target = None
		else:
			self.target = None
			

class AA_1 (AA):
	def __init__ (self, position=(0,0)):
		super (AA_1,self).__init__(position)	# call init of parent
		self.cost = 50
		self.range_sq = 7
		self.range = self.range_sq * self.range_sq
		self.upgrade_cost = 125
		self.upgrade_time = 4
		self.damage_per_shot = 45
		self.sell_price = 35
		self.time_between_shots = 0.15
		self.time_since_last_shot = 3
		self.base_tex = 7
		self.tower_tex = 17 
		
	def fire_projectile(self):
		if audio: audio_cannon_1_fire.play()
		game.projectiles.append (AA_Bullet_1 ( [self.pos[0]+1, self.pos[1]+1], self.target, self.damage_per_shot))
		self.time_since_last_shot=0
	
	def get_upgrade(self):
		return Cannon_2 (copy.copy(self.pos))

			
		
#
#	END OF TOWERS
#







#
#	PARTICLES
#
	



		



	
class particle_small_hit(object):
	def __init__ (self, pos):
		self.duration = random.random()*1.2
		self.time_alive = 0
		self.xdir = 44-(random.random()*88)
		self.ydir = 44-(random.random()*88)
		#self.pos=[ game.map.llx + (game.map.cellsize * pos[0]) , game.map.lly + (game.map.cellsize * pos[1]) ]
		self.pos = pos
		self.alpha_scale = 1.0 / self.duration
		
	def draw (self):
		x = 1-self.time_alive * self.alpha_scale
		glColor4f (1,x,x,x)
		#mote_sprite.blit ( self.pos[0] , self.pos[1] )
		glPushMatrix()
		glTranslatef (self.pos[0], self.pos[1], 0)
		glCallList(3) #mote
		glPopMatrix()
		glColor4f (1,1,1,1)
	
	def update (self, tick):
		self.time_alive += tick
		if self.time_alive < self.duration:
			self.pos[0]+=self.xdir * tick
			self.pos[1]+=self.ydir * tick
		else:
			game.particles.remove (self)
			
			
class particle_medium_hit(object):
	def __init__ (self, pos):
		self.duration = random.random()*0.8
		self.time_alive = 0
		self.xdir = 33-(random.random()*66)
		self.ydir = 33-(random.random()*66)
		#self.pos=[ game.map.llx + (game.map.cellsize * pos[0]) , game.map.lly + (game.map.cellsize * pos[1]) ]
		self.pos = pos
		self.alpha_scale = 1.0 / self.duration
		
	def draw (self):
		x = 1-self.time_alive * self.alpha_scale
		glColor4f (1,x,x,x)
		spark_big_sprite.blit ( self.pos[0] , self.pos[1] )
		glColor4f (1,1,1,1)
	
	def update (self, tick):
		self.time_alive += tick
		if self.time_alive < self.duration:
			self.pos[0]+=self.xdir * tick
			self.pos[1]+=self.ydir * tick
		else:
			game.particles.remove (self)
			
			
class particle_blue_trail(object):
	def __init__ (self, pos):
		#self.duration = random.random()*0.8
		self.duration = 0.4
		self.time_alive = 0
		self.pos=[ game.map.llx + (game.map.cellsize * pos[0]) , game.map.lly + (game.map.cellsize * pos[1]) ]
		self.alpha_scale = 1.0 / self.duration
		
	def draw (self):
		x = 1-self.time_alive * self.alpha_scale
		glColor4f (x,x,1,x)
		blue_particle_sprite.blit ( self.pos[0], self.pos[1])
		glColor4f (1,1,1,1)
	
	def update (self, tick):
		self.time_alive += tick
		if self.time_alive > self.duration:
			game.particles.remove (self)
			
			
class particle_white_trail(object):
	def __init__ (self, pos):
		#self.duration = random.random()*0.8
		self.duration = 0.4
		self.time_alive = 0
		self.pos=[ game.map.llx + (game.map.cellsize * pos[0]) , game.map.lly + (game.map.cellsize * pos[1]) ]
		self.alpha_scale = 1.0 / self.duration
		
	def draw (self):
		x = 1-self.time_alive * self.alpha_scale
		glColor4f (1,1,1,x)
		white_particle_sprite.blit ( self.pos[0], self.pos[1])
		glColor4f (1,1,1,1)
	
	def update (self, tick):
		self.time_alive += tick
		if self.time_alive > self.duration:
			game.particles.remove (self)
			
			
class particle_shockwave(object):
	def __init__ (self, pos, duration=0.5, accel=500):
		#self.duration = random.random()*0.8
		self.duration = duration
		self.time_alive = 0
		self.size = 1
		self.accel = accel
		self.pos=[ game.map.llx + (game.map.cellsize * pos[0]) , game.map.lly + (game.map.cellsize * pos[1]) ]
		self.alpha_scale = 1.0 / self.duration
		
	def draw (self):
		x = 1-self.time_alive * self.alpha_scale
		w = self.size
		o = w*0.5 #radius
		glColor4f (1,1,1,x)
		red_shockwave_sprite.blit ( -o + self.pos[0], -o+self.pos[1], width=w, height=w)
		glColor4f (1,1,1,1)
	
	def update (self, tick):
		self.time_alive += tick
		self.size += tick * self.accel
		if self.time_alive > self.duration:
			game.particles.remove (self)
			
class particle_purple_shockwave(object):
	def __init__ (self, pos, duration=0.2, accel=500):
		#self.duration = random.random()*0.8
		self.duration = duration
		self.time_alive = 0
		self.size = 1
		self.accel = accel
		#self.pos=[ game.map.llx + (game.map.cellsize * pos[0]) , game.map.lly + (game.map.cellsize * pos[1]) ]
		self.pos = pos
		self.alpha_scale = 1.0 / self.duration
		
	def draw (self):
		x = 1-self.time_alive * self.alpha_scale
		w = self.size
		o = w*0.5 #radius
		glColor4f (1,1,1,x)
		purple_shockwave_sprite.blit ( -o + self.pos[0], -o+self.pos[1], width=w, height=w)
		glColor4f (1,1,1,1)
	
	def update (self, tick):
		self.time_alive += tick
		self.size += tick * self.accel
		if self.time_alive > self.duration:
			game.particles.remove (self)
			
			
class particle_smoke(object):
	def __init__ (self, pos):
		#self.duration = random.random()*0.8
		self.duration = 3.0
		self.time_alive = 0
		self.size = 16
		self.pos=[ game.map.llx + (game.map.cellsize * pos[0])  ,  game.map.lly + (game.map.cellsize * pos[1])  ]
		self.alpha_scale = 1.0 / self.duration
		
	def draw (self):
		x = (1.0-self.time_alive * self.alpha_scale) 
		w = self.size
		o = w*0.5 #radius
		glColor4f (1,1,1,x)
		smoke_sprite.blit ( -o + self.pos[0], -o+self.pos[1], width=w, height=w)
		glColor4f (1,1,1,1)
	
	def update (self, tick):
		self.time_alive += tick
		self.size += tick * 80
		if self.time_alive > self.duration:
			game.particles.remove (self)
			
			
class particle_explosion(object):
	def __init__ (self, pos, count=50):
		self.duration = 1.1
		self.time_alive = 0
		self.particle_count = count
		self.dir=[]
		self.curpos=[]
		self.sprites=[]
		screenx=game.map.llx + (game.map.cellsize * pos[0])
		screeny=game.map.lly + (game.map.cellsize * pos[1])
		for i in xrange (0,self.particle_count):
			x = -333+random.random()*666
			y = -333+random.random()*666
			self.dir.append ([x,y])
			#b=copy.copy(pos)
			#self.curpos.append ([copy.copy(self.screenx),copy.copy(self.screeny)])
			self.curpos.append ([screenx,screeny])
			#self.sprites.append ( pyglet.sprite.Sprite(spark_pic, copy.copy(screenx), copy.copy(screeny), batch=batch) )
		self.alpha_scale = 1.0 / self.duration
		

		
	def draw_old (self):
		x = 1 - self.time_alive * self.alpha_scale
		glColor4f (1,1,1, x)
		t = 0
		# set up local variables for speed
		curpos=self.curpos
		s0=spark_big_sprite
		s1=spark_sprite
		s2=mote_sprite
		for i in xrange (0,self.particle_count):
			if t==0:
				s0.blit (curpos[i][0] , curpos[i][1] )
			elif t==1:
				s1.blit (curpos[i][0] , curpos[i][1] )
			else:
				s2.blit (curpos[i][0] , curpos[i][1] )
			t+=1
			if t>2: t=0
		glColor4f (1,1,1,1)
		
	def draw (self):
		x = 1 - self.time_alive * self.alpha_scale
		glColor4f (1,1,1, x)
		t = 0
		# set up local variables for speed
		curpos=self.curpos

		for i in xrange (0,self.particle_count):
			if t==0:
				glPushMatrix()
				glTranslatef (curpos[i][0], curpos[i][1],0)
				glCallList(4)
				glPopMatrix()
			elif t==1:
				glPushMatrix()
				glTranslatef (curpos[i][0], curpos[i][1],0)
				glCallList(2)
				glPopMatrix()
			else:
				glPushMatrix()
				glTranslatef (curpos[i][0], curpos[i][1],0)
				glCallList(3)
				glPopMatrix()
			t+=1
			if t>2: t=0
		glColor4f (1,1,1,1)
		
		
	
	def update (self, tick):
		self.time_alive += tick
		if self.time_alive < self.duration:
			omt = (1.0-tick*2.0)	# scaling factor for deceleration
			curpos=self.curpos
			dir=self.dir
			for i in xrange (0,self.particle_count):
				curpos[i][0]+=dir[i][0]*tick
				curpos[i][1]+=dir[i][1]*tick
				dir[i][0]*= omt 	# slows particles due to air density
				dir[i][1]*= omt 	# slows particles due to air density
		else:
			game.particles.remove (self)
		

		
		
		
		
		
		
		
		
		
		
		
		
		
		
class aGame(object):
	def __init__ (self, cellwidth=24):
		self.cw=cellwidth
		self.states={'paused':1, 'pregame':2, 'ingame':4, 'menu':8}
		self.state=self.states['menu'] | self.states['pregame']
		self.map = None
		self.towers=[]
		self.enemies=[]
		self.flying_enemies=[]
		self.projectiles=[]
		self.particles=[]
		self.score = 0
		self.bonus = 0
		self.credits = 595
		self.lives = 20
		self.create_level()
		self.selected = None
		self.highlighted = None
		self.deploying = None
		self.overlay = None	# menu, banner etc...
		self.sound_enabled = False
		
	def reset (self):
		self.towers=[]
		self.enemies=[]
		self.projectiles=[]
		self.particles=[]
		self.score=0
		score_label.text = "Score: 0"
		self.bonus=0
		self.lives=20
		self.credits = 90
		self.selected=None
		self.deploying=None
		self.highlighted=None
		self.state = self.state | self.states['pregame']
		self.create_level()

		global mymouse
		mymouse=amouse()
		
		
	def create_level (self):
		self.map = aMap(cellsize=self.cw, llx=self.cw * 2, lly=self.cw * 4)
		for route in self.map.routes:
			route.recalc()

			

@window.event
def on_key_release (symbol, modifiers):
	if game.state & game.states['ingame']:
		if game.selected and symbol==key.S:
			game.selected.sell()
		if symbol==key._1:
			cannon_tower_button.on_click(cannon_tower_button)
		if symbol==key.SPACE and game.map.swarms:
			game.map.time_passed += game.map.active_swarms[-1].time	# time remaining on last swarm to be taken off before popping next
			game.map.active_swarms.append ( game.map.swarms.pop(0) )
			
	
			
@window.event
def on_deactivate():
	# lost focus - pause if ingame
	if game.state & game.states['ingame'] and not game.state & game.states['paused']:
		game.state = game.state | game.states['paused']
		set_overlay ( PauseMenu() )
			
@window.event
def on_mouse_release (x,y,buttons,modifiers):
	if buttons & mouse.RIGHT:
		mymouse.rmb_clicked=True
	if buttons & mouse.LEFT:
		mymouse.lmb_clicked=True
	if buttons & mouse.MIDDLE:
		if game.state & game.states['ingame']:
			px=(x-game.map.llx)/float(game.map.cellsize)
			py=(y-game.map.lly)/float(game.map.cellsize)
			game.particles.append (particle_explosion( (px,py) ))
		
		
@window.event
def on_mouse_motion (x,y,dx,dy):
	mymouse.update_pos (x,y)
	#print x,y
	

	
@window.event
def on_draw():
	#window.invalid = False
	window.clear()
	#background_image.blit(0,0)

	if game.state & game.states['ingame']:
		# draw in height order, far to near
		game.map.draw()
		# draw appropriate ingame stuff
		
		# do swarm panel
		m = 4	# multiplier for width of sections - in pixels per second
		x = game.map.llx - (game.map.time_passed*m)
		y = 32
		h = 32
		
		for s in game.map.active_swarms:
			w = m*s.time_till_next_swarm # width is proportional to the time remaining
			swarm_lookup[s.type].blit (x,y,width=w)
			x += w+1
			
		for s in game.map.swarms:
			w = m*s.time_till_next_swarm # width is proportional to the time remaining
			swarm_lookup[s.type].blit (x,y,width=w)
			x += w+1
		
		lrx = game.map.llx + game.map.width * game.map.cellsize
		glDisable (GL_TEXTURE_2D)
		glBegin (GL_QUADS)
		glColor4f (0,0,0,0)
		glVertex2f (lrx-512, 0)
		glVertex2f (lrx-512, 64)
		glColor4f (0,0,0,1)
		glVertex2f (lrx,64)
		glVertex2f (lrx, 0)
		glVertex2f (lrx, 0)
		glVertex2f (lrx, 64)
		glVertex2f (window.width, 64)
		glVertex2f (window.width, 0)
		glEnd()
		glColor4f (1,1,1,1)
		
		#do dissolve
		glColor4f (0,0,0,1)
		glBegin (GL_QUADS)
		glVertex2f (0,0)
		glVertex2f (0,64)
		glVertex2f (game.map.llx,64)
		glVertex2f (game.map.llx,0)
		glVertex2f (game.map.llx,0)
		glVertex2f (game.map.llx,64)
		glColor4f (0,0,0,0)
		glVertex2f (game.map.llx+64,64)
		glVertex2f (game.map.llx+64,0)
		glEnd()
		glColor4f (1,1,1,1)
		
		glEnable (GL_TEXTURE_2D)
		# end of swarm panel
		
		# do info panels
		if game.deploying:
			type=game.deploying.__class__.__name__
			if type=="Cannon_1":
				cannon_info_label.draw()
			elif type=="Berserker_1":
				berserker_info_label.draw()
			elif type=="ICBM_1":
				icbm_info_label.draw()
			elif type=="Temporal_1":
				temporal_info_label.draw()
			elif type=="Tesla_1":
				tesla_info_label.draw()

				
		
		for tower in game.towers:
			tower.draw()
		if game.selected:
			#game.selected.draw_highlight()
			game.selected.draw()
			game.selected.draw_selection()
			# draw info panel
			type=game.selected.__class__.__name__
			if type=="Cannon_1":
				cannon_1_info_label.draw()
			elif type=="Cannon_2":
				cannon_2_info_label.draw()
			elif type=="Cannon_3":
				cannon_3_info_label.draw()
			elif type=="Berserker_1":
				berserker_1_info_label.draw()
			elif type=="Berserker_2":
				berserker_2_info_label.draw()
			elif type=="Berserker_3":
				berserker_3_info_label.draw()
			elif type=="ICBM_1":
				icbm_1_info_label.draw()
			elif type=="ICBM_2":
				icbm_2_info_label.draw()
			elif type=="ICBM_3":
				icbm_3_info_label.draw()
			elif type=="Temporal_1":
				temporal_1_info_label.draw()
			elif type=="Temporal_2":
				temporal_2_info_label.draw()
			elif type=="Temporal_3":
				temporal_3_info_label.draw()
			elif type=="Tesla_1":
				tesla_1_info_label.draw()
			elif type=="Tesla_2":
				tesla_2_info_label.draw()
		
		for enemy in game.enemies:
			enemy.draw()
			
		for enemy in game.flying_enemies:
			enemy.draw()
			
		if game.highlighted and game.highlighted.mouse_over and not game.deploying and not game.selected:
			# draw range highlight etc..
			game.highlighted.draw_highlight()
			# also draw info panel
			type=game.highlighted.__class__.__name__
			if type=="Cannon_1":
				cannon_1_info_label.draw()
			elif type=="Cannon_2":
				cannon_2_info_label.draw()
			elif type=="Cannon_3":
				cannon_3_info_label.draw()
			elif type=="Berserker_1":
				berserker_1_info_label.draw()
			elif type=="Berserker_2":
				berserker_2_info_label.draw()
			elif type=="Berserker_3":
				berserker_3_info_label.draw()
			elif type=="ICBM_1":
				icbm_1_info_label.draw()
			elif type=="ICBM_2":
				icbm_2_info_label.draw()
			elif type=="ICBM_3":
				icbm_3_info_label.draw()
			elif type=="Temporal_1":
				temporal_1_info_label.draw()
			elif type=="Temporal_2":
				temporal_2_info_label.draw()
			elif type=="Temporal_3":
				temporal_3_info_label.draw()
			elif type=="Tesla_1":
				tesla_1_info_label.draw()
			elif type=="Tesla_2":
				tesla_2_info_label.draw()
			
		
		for particle in game.particles:
			particle.draw()
			
		for proj in game.projectiles:
			proj.draw()
			

		credits_label.text = "Credits: " + str(game.credits)
		credits_label.draw()
		lives_label.draw()
		score_label.draw()
		
		# draw gui
		gui.draw()
	
	
	if game.overlay:
		game.overlay.draw()
			
	# draw mouse
	mymouse.draw()
	
	
	
def update(dt):
	#dt *= 0.5
	#print "FPS: ",pyglet.clock.get_fps()
	
	#if dt==0:
	#	dt+=1/120.0
	if game.state & game.states['ingame']:
		# while ingame...
		# update gui
		gui.update(dt)
		
		ai_frame.enabled=False	# make sure ai frame doesnt get stuck
		
		if game.selected:
			selected_frame.enabled = True
			if game.selected.target_mode:
				# has an ai - show frame, and show the correct one selected
				ai_frame.enabled=True
				for ai_button in ai_frame.widgets:
					if ai_frame.widgets.index(ai_button)==game.selected.target_mode-1:
						ai_button.selected=True
					else:
						ai_button.selected=False
			if game.selected.upgradeable and game.credits >= game.selected.upgrade_cost:
				upgrade_button.visible = True
			else:
				upgrade_button.visible = False
		else:
			selected_frame.enabled = False
			ai_frame.enabled=False
		
		if not game.state & game.states['paused']:

			# NOT PAUSED
			
			if not game.state & game.states['pregame']:
				# make sure swarms dont kick off until pregame is unset
				game.map.swarm_update (dt)
				game.map.time_passed+=dt
		
			#for proj in game.projectiles:
			#	proj.update (dt)
			map ( lambda i:i.update (dt), game.projectiles )
		
			#for enemy in game.enemies:
			#	enemy.update(dt)
			map ( lambda i:i.update (dt), game.enemies )
			
			#for enemy in game.flying_enemies:
			#	enemy.update(dt)
			map ( lambda i:i.update (dt), game.flying_enemies )
			
			#for tower in game.towers:
			#	tower.update (dt)
			map ( lambda i:i.update (dt), game.towers )
				
			#for particle in game.particles:
			#	particle.update (dt)
			map ( lambda i:i.update (dt), game.particles )
				
	mymouse.update()

	
	
	
# global instances of classes declared above

# create game singleton
game=aGame(24)

score_label = pyglet.text.Label ('Score: '+str(game.score),
						font_name=FONT_NAME, 
                          font_size=18,
						  width=window.width/2,
						  height=200,
						  multiline=True,
                          x=60, y=window.height-27,
                          anchor_x='left', anchor_y='top')

credits_label = pyglet.text.Label ('Credits: '+str(game.credits),
						font_name=FONT_NAME, 
                          font_size=18,
						  width=window.width/2,
						  height=200,
						  multiline=True,
                          x=560, y=window.height-27,
                          anchor_x='left', anchor_y='top')
						  
lives_label = pyglet.text.Label ('Lives: '+str(game.lives),
						font_name=FONT_NAME, 
                          font_size=18,
						  width=window.width/2,
						  height=200,
						  multiline=True,
                          x=360, y=window.height-27,
                          anchor_x='left', anchor_y='top')
						  
cannon_info_label = pyglet.text.HTMLLabel 	('<center><font size=5 color=white>Photon Cannon</font></center>'
											+'<font size=4 color=#ffff00>Cost: 5</font><br>'
											+'<font size=4 color=#5566ff>Range: 4</font><br>'
											+'<font size=4 color=#ff4455>Damage: 6</font><br><br>'
											+'<font size=4 color=white>A slow firing, but medium damage tower.  '
											+'Cheap to build, useful for shepherding enemies towards more powerful towers.<br><br>'
											+'Upgrades: Range, Damage - and at levels > 1 targetting AI.</font>' ,
						  width=240,
						  height=400,
						  multiline=True,
                          x=760, y=440,
                          anchor_x='left', anchor_y='top')
cannon_info_label.font_name=FONT_NAME

cannon_1_info_label = pyglet.text.HTMLLabel ('<center><font size=5 color=white>Photon Cannon<br>Level 1</font></center>'
											+'<font size=4 color=#5566ff>Range: 4</font><br>'
											+'<font size=4 color=#ff4455>Damage: 3</font><br><br>'
											+'<font size=4 color=#aaffaa><u>Upgrade Info</u></font><br><br>'
											+'<font size=4 color=#ffff00>Cost: 25</font><br>'
											+'<font size=4 color=#5566ff>Range: 5      (+1)</font><br>'
											+'<font size=4 color=#ff4455>Damage: 30   (+27)</font>' ,
						  width=240,
						  height=400,
						  multiline=True,
                          x=760, y=440,
                          anchor_x='left', anchor_y='top')
cannon_1_info_label.font_name=FONT_NAME

cannon_2_info_label = pyglet.text.HTMLLabel ('<center><font size=5 color=white>Photon Cannon<br>Level 2</font></center>'
											+'<font size=4 color=#5566ff>Range: 5</font><br>'
											+'<font size=4 color=#ff4455>Damage: 30</font><br><br>'
											+'<font size=4 color=#aaffaa><u>Upgrade Info</u></font><br><br>'
											+'<font size=4 color=#ffff00>Cost: 50</font><br>'
											+'<font size=4 color=#5566ff>Range: 5     (no change)</font><br>'
											+'<font size=4 color=#ff4455>Damage: 140   (+110)</font>' ,
						  width=240,
						  height=400,
						  multiline=True,
                          x=760, y=440,
                          anchor_x='left', anchor_y='top')
cannon_2_info_label.font_name=FONT_NAME

cannon_3_info_label = pyglet.text.HTMLLabel ('<center><font size=5 color=white>Photon Cannon<br>Level 3</font></center>'
											+'<font size=4 color=#5566ff>Range: 5</font><br>'
											+'<font size=4 color=#ff4455>Damage: 140</font><br><br>'
											+'<font size=4 color=#aaffaa><u>Upgrade Info</u></font><br><br>'
											+'<font size=4 color=#ffff00>Cost: na</font><br>'
											+'<font size=4 color=#5566ff>Range: na    </font><br>'
											+'<font size=4 color=#ff4455>Damage: na   </font>' ,
						  width=240,
						  height=400,
						  multiline=True,
                          x=760, y=440,
                          anchor_x='left', anchor_y='top')
cannon_3_info_label.font_name=FONT_NAME





berserker_info_label = pyglet.text.HTMLLabel 	('<center><font size=5 color=white>Berserker Tower</font></center>'
											+'<font size=4 color=#ffff00>Cost: 15</font><br>'
											+'<font size=4 color=#5566ff>Range: 4.5</font><br>'
											+'<font size=4 color=#ff4455>Damage: 3</font><br><br>'
											+'<font size=4 color=white>A rapid firing, indiscriminate rail gun with no AI.<br>'
											+'Low damage per hit is offset by rate of fire and range.'
											+'<br><br>Upgrades: Damage and Rate of Fire, and later massive Range increase.</font>' ,
						  width=240,
						  height=400,
						  multiline=True,
                          x=760, y=440,
                          anchor_x='left', anchor_y='top')
berserker_info_label.font_name=FONT_NAME	


berserker_1_info_label = pyglet.text.HTMLLabel ('<center><font size=5 color=white>Berserker Tower<br>Level 1</font></center>'
											+'<font size=4 color=#5566ff>Range: 4.5</font><br>'
											+'<font size=4 color=#ff4455>Damage: 3</font><br><br>'
											+'<font size=4 color=#aaffaa><u>Upgrade Info</u></font><br><br>'
											+'<font size=4 color=#ffff00>Cost: 65</font><br>'
											+'<font size=4 color=#5566ff>Range: 5      (+1)</font><br>'
											+'<font size=4 color=#ff4455>Damage: 15   (+33%)</font><br>'
											+'<font size=4 color=#7788ff>Rate of fire +50%</font>',
						  width=240,
						  height=400,
						  multiline=True,
                          x=760, y=440,
                          anchor_x='left', anchor_y='top')
berserker_1_info_label.font_name=FONT_NAME

berserker_2_info_label = pyglet.text.HTMLLabel ('<center><font size=5 color=white>Berserker Tower<br>Level 2</font></center>'
											+'<font size=4 color=#5566ff>Range: 5</font><br>'
											+'<font size=4 color=#ff4455>Damage: 15</font><br><br>'
											+'<font size=4 color=#aaffaa><u>Upgrade Info</u></font><br><br>'
											+'<font size=4 color=#ffff00>Cost: 165</font><br>'
											+'<font size=4 color=#5566ff>Range: 5      (+1)</font><br>'
											+'<font size=4 color=#ff4455>Damage: 40   (+285%)</font><br>'
											+'<font size=4 color=#7788ff>Rate of fire +20%</font>',
						  width=240,
						  height=400,
						  multiline=True,
                          x=760, y=440,
                          anchor_x='left', anchor_y='top')
berserker_2_info_label.font_name=FONT_NAME

berserker_3_info_label = pyglet.text.HTMLLabel ('<center><font size=5 color=white>Berserker Tower<br>Level 3</font></center>'
											+'<font size=4 color=#5566ff>Range: 5</font><br>'
											+'<font size=4 color=#ff4455>Damage: 40</font><br><br>'
											+'<font size=4 color=#aaffaa><u>Upgrade Info</u></font><br><br>'
											+'<font size=4 color=#ffff00>Cost: na</font><br>'
											+'<font size=4 color=#5566ff>Range: na      (+1)</font><br>'
											+'<font size=4 color=#ff4455>Damage: na   (+285%)</font><br>'
											+'<font size=4 color=#7788ff>Rate of fire +na%</font>',
						  width=240,
						  height=400,
						  multiline=True,
                          x=760, y=440,
                          anchor_x='left', anchor_y='top')
berserker_3_info_label.font_name=FONT_NAME

icbm_info_label = pyglet.text.HTMLLabel 	('<center><font size=5 color=white>Missile Launcher</font></center>'
											+'<font size=4 color=#ffff00>Cost: 50</font><br>'
											+'<font size=4 color=#5566ff>Max Range: 9</font><br>'
											+'<font size=4 color=#5566ff>Min Range: 5</font><br>'
											+'<font size=4 color=#ff4455>Damage: 50</font><br><br>'
											+'<font size=4 color=white>Long range missile launcher which damages all units in the blast area.<br>'
											+'Cannot hit targets close to launch platform.<br>Targets units nearest exit.<br><br>'
											+'Upgrades: Range, Damage, Damage area</font>' ,
						  width=240,
						  height=400,
						  multiline=True,
                          x=760, y=440,
                          anchor_x='left', anchor_y='top')
icbm_info_label.font_name=FONT_NAME

icbm_1_info_label = pyglet.text.HTMLLabel ('<center><font size=5 color=white>Missile Launcher<br>Level 1</font></center>'
											+'<font size=4 color=#5566ff>Max Range: 9</font><br>'
											+'<font size=4 color=#5566ff>Min Range: 5</font><br>'
											+'<font size=4 color=#ff4455>Damage: 50</font><br><br>'
											+'<font size=4 color=#aaffaa><u>Upgrade Info</u></font><br><br>'
											+'<font size=4 color=#ffff00>Cost: 150</font><br>'
											+'<font size=4 color=#5566ff>Max Range: 10      (+1)</font><br>'
											+'<font size=4 color=#ff4455>Damage: 150  (+100)</font><br>',
						  width=240,
						  height=400,
						  multiline=True,
                          x=760, y=440,
                          anchor_x='left', anchor_y='top')
icbm_1_info_label.font_name=FONT_NAME

icbm_2_info_label = pyglet.text.HTMLLabel ('<center><font size=5 color=white>Missile Launcher<br>Level 2</font></center>'
											+'<font size=4 color=#5566ff>Max Range: 10</font><br>'
											+'<font size=4 color=#5566ff>Min Range: 6</font><br>'
											+'<font size=4 color=#ff4455>Damage: 150</font><br><br>'
											+'<font size=4 color=#aaffaa><u>Upgrade Info</u></font><br><br>'
											+'<font size=4 color=#ffff00>Cost: 250</font><br>'
											+'<font size=4 color=#5566ff>Max Range: 11      (+1)</font><br>'
											+'<font size=4 color=#ff4455>Damage: 350  (+200)</font><br>',
						  width=240,
						  height=400,
						  multiline=True,
                          x=760, y=440,
                          anchor_x='left', anchor_y='top')
icbm_2_info_label.font_name=FONT_NAME

icbm_3_info_label = pyglet.text.HTMLLabel ('<center><font size=5 color=white>Missile Launcher<br>Level 3</font></center>'
											+'<font size=4 color=#5566ff>Max Range: 11</font><br>'
											+'<font size=4 color=#5566ff>Min Range: 4</font><br>'
											+'<font size=4 color=#ff4455>Damage: 350</font><br><br>'
											+'<font size=4 color=#aaffaa><u>Upgrade Info</u></font><br><br>'
											+'<font size=4 color=#ffff00>Cost: 550</font><br>'
											+'<font size=4 color=#5566ff>Max Range: 10      (+1)</font><br>'
											+'<font size=4 color=#ff4455>Damage: 650  (+300)</font><br>',
						  width=240,
						  height=400,
						  multiline=True,
                          x=760, y=440,
                          anchor_x='left', anchor_y='top')
icbm_3_info_label.font_name=FONT_NAME

			
temporal_info_label = pyglet.text.HTMLLabel 	('<center><font size=5 color=white>Temporal Disruptor</font></center>'
											+'<font size=4 color=#ffff00>Cost: 20</font><br>'
											+'<font size=4 color=#5566ff>Range: 4</font><br>'
											+'<font size=4 color=#ff4455>Speed: -25%</font><br>'
											+'<font size=4 color=#aaaaaa>Duration: 2secs</font><br><br>'
											+'<font size=4 color=white>Experimental structure that create a localised temporal anomaly.<br>'
											+'Slows time inside a small, short-lived bubble, making enemies travel slower for a spell.<br><br>'
											+'Upgrades: Range, Effect strength, and Duration</font>' ,
						  width=240,
						  height=400,
						  multiline=True,
                          x=760, y=440,
                          anchor_x='left', anchor_y='top')
temporal_info_label.font_name=FONT_NAME

temporal_1_info_label = pyglet.text.HTMLLabel ('<center><font size=5 color=white>Temporal Disruptor<br>Level 1</font></center>'
											+'<font size=4 color=#5566ff>Range: 4</font><br>'
											+'<font size=4 color=#ff4455>Speed: -25%</font><br>'
											+'<font size=4 color=#aaaaaa>Duration: 4secs</font><br><br>'
											+'<font size=4 color=#aaffaa><u>Upgrade Info</u></font><br><br>'
											+'<font size=4 color=#ffff00>Cost: 50</font><br>'
											+'<font size=4 color=#5566ff>Range: 5      (+1)</font><br>'
											+'<font size=4 color=#ff4455>Speed: -35%</font><br>'
											+'<font size=4 color=#aaaaaa>Duration: 3secs</font><br>'
											+'<font size=4 color=#aaaaaa>+ Small increase fire rate</font><br><br>',
						  width=240,
						  height=400,
						  multiline=True,
                          x=760, y=440,
                          anchor_x='left', anchor_y='top')
temporal_1_info_label.font_name=FONT_NAME

temporal_2_info_label = pyglet.text.HTMLLabel ('<center><font size=5 color=white>Temporal Disruptor<br>Level 2</font></center>'
											+'<font size=4 color=#5566ff>Range: 4</font><br>'
											+'<font size=4 color=#ff4455>Speed: -35%</font><br>'
											+'<font size=4 color=#aaaaaa>Duration: 4secs</font><br><br>'
											+'<font size=4 color=#aaffaa><u>Upgrade Info</u></font><br><br>'
											+'<font size=4 color=#ffff00>Cost: 150</font><br>'
											+'<font size=4 color=#5566ff>Range: 5      (+1)</font><br>'
											+'<font size=4 color=#ff4455>Speed: -55%</font><br>'
											+'<font size=4 color=#ffffaa>Rapid Fire Module</font><br>'
											+'<font size=4 color=#aaaaaa>Duration: 5secs</font><br><br>',
						  width=240,
						  height=400,
						  multiline=True,
                          x=760, y=440,
                          anchor_x='left', anchor_y='top')
temporal_2_info_label.font_name=FONT_NAME

temporal_3_info_label = pyglet.text.HTMLLabel ('<center><font size=5 color=white>Temporal Disruptor<br>Level 3</font></center>'
											+'<font size=4 color=#5566ff>Range: 5</font><br>'
											+'<font size=4 color=#ff4455>Speed: -55%</font><br>'
											+'<font size=4 color=#aaaaaa>Duration: 5secs</font><br><br>'
											+'<font size=4 color=#aaffaa><u>Upgrade Info</u></font><br><br>'
											+'<font size=4 color=#ffff00>Cost: 400</font><br>'
											+'<font size=4 color=#5566ff>Range: 5      (+1)</font><br>'
											+'<font size=4 color=#ff4455>Speed: -55%</font><br>'
											+'<font size=4 color=#aaaaaa>Duration: 5secs</font><br><br>',
						  width=240,
						  height=400,
						  multiline=True,
                          x=760, y=440,
                          anchor_x='left', anchor_y='top')
temporal_3_info_label.font_name=FONT_NAME


tesla_info_label = pyglet.text.HTMLLabel 	('<center><font size=5 color=white>Tesla Cannon</font></center>'
											+'<font size=4 color=#ffff00>Cost: 100</font><br>'
											+'<font size=4 color=#5566ff>Range: 3</font><br>'
											+'<font size=4 color=#ff4455>Chain hits: 3</font><br>'
											+'<font size=4 color=#aaaaaa>Duration: 2secs</font><br><br>'
											+'<font size=4 color=white>Slow charging, short range electrical cannon.<br>'
											+'Discharges high voltage bolt into nearby enemies<br>'
											+'Damage takes effect over time, so don`t place too near exits!<br><br>'
											+'Upgrades: Effect strength, Duration, and Chain length.</font>' ,
						  width=240,
						  height=400,
						  multiline=True,
                          x=760, y=440,
                          anchor_x='left', anchor_y='top')
tesla_info_label.font_name=FONT_NAME

tesla_1_info_label = pyglet.text.HTMLLabel ('<center><font size=5 color=white>Tesla Cannon<br>Level 1</font></center>'
											+'<font size=4 color=#5566ff>Range: 3</font><br>'
											+'<font size=4 color=#ff4455>Chain Hits: 3</font><br>'
											+'<font size=4 color=#aaaaaa>Duration: 6secs</font><br><br>'
											+'<font size=4 color=#aaffaa><u>Upgrade Info</u></font><br><br>'
											+'<font size=4 color=#ffff00>Cost: 250</font><br>'
											+'<font size=4 color=#5566ff>Range: 3      (+1)</font><br>'
											+'<font size=4 color=#ff4455>Chain hits: 4</font><br>'
											+'<font size=4 color=#aaaaaa>Duration: 8secs</font><br><br>',
						  width=240,
						  height=400,
						  multiline=True,
                          x=760, y=440,
                          anchor_x='left', anchor_y='top')
tesla_1_info_label.font_name=FONT_NAME

tesla_2_info_label = pyglet.text.HTMLLabel ('<center><font size=5 color=white>Tesla Cannon<br>Level 2</font></center>'
											+'<font size=4 color=#5566ff>Range: 3</font><br>'
											+'<font size=4 color=#ff4455>Chain Hits: 4</font><br>'
											+'<font size=4 color=#aaaaaa>Duration: 8secs</font><br><br>'
											+'<font size=4 color=#aaffaa><u>Upgrade Info</u></font><br><br>'
											+'<font size=4 color=#ffff00>Cost: 250</font><br>'
											+'<font size=4 color=#5566ff>Range: 4      (+1)</font><br>'
											+'<font size=4 color=#ff4455>Chain hits: 5</font><br><br>',
						  width=240,
						  height=400,
						  multiline=True,
                          x=760, y=440,
                          anchor_x='left', anchor_y='top')
tesla_2_info_label.font_name=FONT_NAME

						
def cannon_button_on_click (button):
	# unselect all buttons in same frame
	for widget in button.parent.widgets:
		widget.selected=False
	# select button clicked
	button.selected=True
	# update game selected - which in turn drives the mouse draw icon
	game.deploying = Cannon_1 ()
	# make sure nothing selected
	if game.selected:
		game.selected=None
	
def berserker_button_on_click (button):
	# unselect all buttons in same frame
	for widget in button.parent.widgets:
		widget.selected=False
	# select button clicked
	button.selected=True
	# update game selected - which in turn drives the mouse draw icon
	game.deploying = Berserker_1 ()
	# make sure nothing selected
	if game.selected:
		game.selected=None
		
def icbm_button_on_click (button):
	# unselect all buttons in same frame
	for widget in button.parent.widgets:
		widget.selected=False
	# select button clicked
	button.selected=True
	# update game selected - which in turn drives the mouse draw icon
	game.deploying = ICBM_1 ()
	# make sure nothing selected
	if game.selected:
		game.selected=None
		
def temporal_button_on_click (button):
	# unselect all buttons in same frame
	for widget in button.parent.widgets:
		widget.selected=False
	# select button clicked
	button.selected=True
	# update game selected - which in turn drives the mouse draw icon
	game.deploying = Temporal_1 ()
	# make sure nothing selected
	if game.selected:
		game.selected=None
		
def tesla_button_on_click (button):
	# unselect all buttons in same frame
	for widget in button.parent.widgets:
		widget.selected=False
	# select button clicked
	button.selected=True
	# update game selected - which in turn drives the mouse draw icon
	game.deploying = Tesla_1 ()
	# make sure nothing selected
	if game.selected:
		game.selected=None
		
def aa_button_on_click (button):
	# unselect all buttons in same frame
	for widget in button.parent.widgets:
		widget.selected=False
	# select button clicked
	button.selected=True
	# update game selected - which in turn drives the mouse draw icon
	game.deploying = AA_1 ()
	# make sure nothing selected
	if game.selected:
		game.selected=None
	
def start_button_on_click (button):
	# disable start button
	gui.widgets.remove(button)
	# flip pregame state
	game.state = game.state ^ game.states['pregame']
	# start swarms
	game.map.active_swarms.append (game.map.swarms.pop(0))
	
	
def sell_button_on_click (button):
	if game.selected:
		game.selected.sell()
		
def pause_button_on_click (button):
	game.state = game.state ^ game.states['paused'] #flip paused flag
	set_overlay ( PauseMenu() )	# overlay paused menu
	
def ai_button_on_click (button):
	for b in button.parent.widgets:
		# for all other ai buttons in frame
		if b is not button:
			b.selected=False
		button.selected=True
	game.selected.target_mode = button.parent.widgets.index(button)+1
	
	
def upgrade_button_on_click (button):
	if game.selected.upgradeable and game.credits>= game.selected.upgrade_cost:
		if audio: audio_upgrade.play()
		game.credits -= game.selected.upgrade_cost
		credits_label.text = "Credits: " + str(game.credits)
		game.selected.upgrade()
	else:
		pass


#window = pyglet.window.Window(800, 600,"test",True, style='borderless')

	
		

		
mymouse=amouse()
gui=GUI()

start_button = Button (gui, pos=(850,24), rmb_clears=False, background=button_start_pic)
start_button.on_click = start_button_on_click

pause_button = Button (gui, pos=(930, 24), rmb_clears=False, background=button_pause_pic)
pause_button.on_click = pause_button_on_click 

selected_frame = Frame ( pos=(game.cw*3+(game.map.width*game.cw), game.cw*4 + 32) , width = 300, height = 300, background_colour=(0,0,0,0))
upgrade_button = Button (selected_frame, pos=(0,0), background=upgrade_pic)
sell_button = Button (selected_frame, pos=(141, 0), background=sell_pic)
sell_button.on_click = sell_button_on_click 
upgrade_button.on_click = upgrade_button_on_click
selected_frame.enabled=False

pixels_between_ai_buttons = 44
ai_frame = Frame ( pos=(game.cw*3+(game.map.width*game.cw), game.cw*8-16), width = 300, height=300, background_colour=(0,0,0,0))
x=0
ai_strong_button=Button (ai_frame, pos=(x,0), rmb_clears=False, background=button_ai_strong_off_pic, background_selected=button_ai_strong_on_pic)
ai_strong_button.on_click = ai_button_on_click
x+=pixels_between_ai_buttons
ai_weak_button=Button (ai_frame, pos=(x,0), rmb_clears=False, background=button_ai_weak_off_pic, background_selected=button_ai_weak_on_pic)
ai_weak_button.on_click = ai_button_on_click
x+=pixels_between_ai_buttons
ai_fast_button=Button (ai_frame, pos=(x,0), rmb_clears=False, background=button_ai_fast_off_pic, background_selected=button_ai_fast_on_pic)
ai_fast_button.on_click = ai_button_on_click
x+=pixels_between_ai_buttons
ai_slow_button=Button (ai_frame, pos=(x,0), rmb_clears=False, background=button_ai_slow_off_pic, background_selected=button_ai_slow_on_pic)
ai_slow_button.on_click = ai_button_on_click
x+=pixels_between_ai_buttons
ai_near_button=Button (ai_frame, pos=(x,0), rmb_clears=False, background=button_ai_near_off_pic, background_selected=button_ai_near_on_pic)
ai_near_button.on_click = ai_button_on_click
x+=pixels_between_ai_buttons
ai_far_button=Button (ai_frame, pos=(x,0), rmb_clears=False, background=button_ai_far_off_pic, background_selected=button_ai_far_on_pic)
ai_far_button.on_click = ai_button_on_click
ai_frame.enabled=False

tower_frame = Frame ( pos=(60+(game.map.width*game.map.cellsize),600), width=250, height=150, background_colour=(0,0,0,0) )
cannon_tower_button = Button (tower_frame, pos=(10,10), background=button_cannon_tower_pic, background_selected=button_cannon_tower_selected_pic, background_mouseover=button_cannon_tower_mouseover_pic)
cannon_tower_button.on_click = cannon_button_on_click
berserker_tower_button = Button (tower_frame, pos=(80,10), background=button_berserker_tower_pic, background_selected=button_berserker_tower_selected_pic, background_mouseover=button_berserker_tower_mouseover_pic)
berserker_tower_button.on_click = berserker_button_on_click
icbm_tower_button = Button (tower_frame, pos=(150,10), background=button_icbm_tower_pic, background_selected=button_icbm_tower_selected_pic, background_mouseover=button_icbm_tower_mouseover_pic)
icbm_tower_button.on_click = icbm_button_on_click
temporal_tower_button = Button (tower_frame, pos=(220,10), background=button_temporal_tower_pic, background_selected=button_temporal_tower_selected_pic, background_mouseover=button_temporal_tower_mouseover_pic)
temporal_tower_button.on_click = temporal_button_on_click
tesla_tower_button = Button (tower_frame, pos=(10,70), background=button_tesla_tower_pic, background_selected=button_tesla_tower_selected_pic, background_mouseover=button_tesla_tower_mouseover_pic)
tesla_tower_button.on_click = tesla_button_on_click
aa_tower_button = Button (tower_frame, pos=(80,70), background=button_aa_tower_pic, background_selected=button_aa_tower_selected_pic, background_mouseover=button_aa_tower_mouseover_pic)
aa_tower_button.on_click = aa_button_on_click

set_overlay(MainMenu())


#pyglet.clock.schedule(update)
pyglet.clock.schedule_interval(update,1/120.)	
pyglet.app.run()
