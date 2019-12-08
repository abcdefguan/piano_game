import pygame

#Define some colors
black = (0,0,0)
white = (255,255,255)

#[Btn] specifies a class that represents a button object drawn on the stage
class Btn:
	"""[__init__ self, text, center, on_click, font_size, color, bg_color]
	specifies a button with
	[text] as its display text
	[center] as the tuple (x,y) of the position of its center
	[on_click] as a lambda that takes two arguments, the first of type [Btn] 
	referring to this button object and the second as a tuple (x,y) of the
	mouse click position which would be called when this button is clicked
	[font_size] which specifies the font size of this button
	[color] which specifies the text color of this button
	[bg_color] which specifies the background color of this button
	"""
	def __init__(self, text, center, on_click = None, \
		font_size = 30, color = black, bg_color = white):
		self.text = text
		self.color = color
		self.bg_color = bg_color
		self.center = center
		self.on_click = on_click
		self.font = pygame.font.Font(None, font_size)

	#[draw self, screen] draws this button onto the surface [screen]
	def draw(self, screen):
		self.surf = self.font.render(self.text, True, self.color \
			, self.bg_color)
		self.rect = self.surf.get_rect(center = self.center)
		screen.blit(self.surf, self.rect)

	#[is_clicked self, mouse] returns whether this button has been clicked
	#if the mouse is clicking at the (x,y) position specified by [mouse]
	def is_clicked(self, mouse):
		mouse_x,mouse_y = mouse
		if self.rect == None:
			return False
		if self.rect.left <= mouse_x and mouse_x <= self.rect.right \
		and self.rect.top <= mouse_y and mouse_y <= self.rect.bottom:
			return True
		return False
	"""
	[handle_click self, mouse] checks whether this button has been clicked
	if the mouse is clicking at the (x,y) position specified by [mouse]
	If it has been clicked, it'll run the [on_click] callback if it's
	available and then return true
	Otherwise, it'll return false and not execute the callback
	"""
	def handle_click(self, mouse):
		if self.is_clicked(mouse):
			if self.on_click != None:
				self.on_click(self, mouse)
			return True
		return False

class ImageBtn:
	"""[__init__ self, text, center, on_click, font_size, color, bg_color]
	specifies a button with
	[text] as its display text
	[center] as the tuple (x,y) of the position of its center
	[on_click] as a lambda that takes two arguments, the first of type [Btn] 
	referring to this button object and the second as a tuple (x,y) of the
	mouse click position which would be called when this button is clicked
	[font_size] which specifies the font size of this button
	[color] which specifies the text color of this button
	[bg_color] which specifies the background color of this button
	"""
	def __init__(self, img, center, on_click = None, dimen = None, \
		color = black, bg_color = white):
		self.surf = pygame.image.load(img)
		self.center = center
		#Transform image if dimensions specified
		if dimen != None:
			self.surf = pygame.transform.scale(self.surf, dimen)
		self.surf = self.surf.convert_alpha()
		self.color = color
		self.bg_color = bg_color
		self.center = center
		self.on_click = on_click

	def change_img(self, new_img, dimen = None):
		self.surf = pygame.image.load(new_img)
		if dimen != None:
			self.surf = pygame.transform.scale(self.surf, dimen)
		self.surf = self.surf.convert_alpha()

	#[draw self, screen] draws this button onto the surface [screen]
	def draw(self, screen):
		self.rect = self.surf.get_rect(center = self.center)
		screen.blit(self.surf, self.rect)

	#[is_clicked self, mouse] returns whether this button has been clicked
	#if the mouse is clicking at the (x,y) position specified by [mouse]
	def is_clicked(self, mouse):
		mouse_x,mouse_y = mouse
		if self.rect == None:
			return False
		if self.rect.left <= mouse_x and mouse_x <= self.rect.right \
		and self.rect.top <= mouse_y and mouse_y <= self.rect.bottom:
			return True
		return False
	"""
	[handle_click self, mouse] checks whether this button has been clicked
	if the mouse is clicking at the (x,y) position specified by [mouse]
	If it has been clicked, it'll run the [on_click] callback if it's
	available and then return true
	Otherwise, it'll return false and not execute the callback
	"""
	def handle_click(self, mouse):
		if self.is_clicked(mouse):
			if self.on_click != None:
				self.on_click(self, mouse)
			return True
		return False

class Text:
	def __init__(self, text, center, font_size = 30, color = black, \
		centering = "center"):
		self.text = text
		self.color = color
		self.center = center
		self.centering = centering
		self.font = pygame.font.Font(None, font_size)

	#[draw self, screen] draws this button onto the surface [screen]
	def draw(self, screen):
		self.surf = self.font.render(self.text, True, self.color)
		if self.centering == "center":
			self.rect = self.surf.get_rect(center = self.center)
		elif self.centering == "topleft":
			self.rect = self.surf.get_rect(topleft = self.center)
		screen.blit(self.surf, self.rect)

class Line:
	def __init__(self, start_pos, end_pos, color = black, width = 1):
		self.color = color
		self.start_pos = start_pos
		self.end_pos = end_pos
		self.width = width

	def change_x(self, start_x, end_x):
		self.start_pos = (start_x, self.start_pos[1])
		self.end_pos = (end_x, self.end_pos[1])

	def draw(self, screen):
		pygame.draw.line(screen, self.color, self.start_pos, self.end_pos, \
			self.width)

class Image:
	def __init__(self, img, center, dimen = None, from_surf = False):
		if not from_surf:
			self.surf = pygame.image.load(img)
		else:
			self.surf = img
		self.center = center
		self.color = None
		#Transform image if dimensions specified
		if dimen != None:
			self.surf = pygame.transform.scale(self.surf, dimen)
		self.surf = self.surf.convert_alpha()
		self.rect = self.surf.get_rect()

	def change_color(self, new_color):
		#Don't color if already this color
		if self.color == new_color:
			return
		#Otherwise, color
		r,g,b = new_color
		self.surf.fill((0,0,0,255), special_flags = pygame.BLEND_RGBA_MULT)
		self.surf.fill((r,g,b,0), special_flags = pygame.BLEND_RGBA_ADD)
		self.color = new_color

	def draw(self, screen):
		self.rect.center = self.center
		screen.blit(self.surf, self.rect)

"""
[Stage] specifies a class that represents a stage onto which objects are drawn
Objects on the stage must implement the following methods:
[draw self screen] which draws the object onto the screen
Buttons on the stage must additionally implement the following methods:
[handle_click self mouse] which handles a click event on the (x,y) position
specified by [mouse] and returns whether the mouse has clicked on that object
"""
class Stage:
	#[__init__ self] creates a new stage with a list of Btn [btns]
	def __init__(self):
		self.btns = []
		self.elts = []
		self.tmp_elts = []

	#[add_btn self btn] adds the Btn [btn] onto the stage
	def add_btn(self, btn):
		self.btns.append(btn)

	#[remove_btn self btn] removes the Btn [btn] from the stage
	def remove_btn(self, btn):
		if btn in self.btns:
			self.btns.remove(btn)

	def add_elt(self, elt):
		self.elts.append(elt)

	def remove_elt(self, elt):
		if elt in self.elts:
			self.elts.remove(elt)

	def add_tmp_elt(self, tmp_elt):
		self.tmp_elts.append(tmp_elt)

	def clear_tmp_elts(self):
		self.tmp_elts = []

	#[draw self, screen] draws all the elements on the stage onto the Surface
	#[screen]
	def draw(self, screen):
		for tmp_elt in self.tmp_elts:
			tmp_elt.draw(screen)
		for elt in self.elts:
			elt.draw(screen)
		for btn in self.btns:
			btn.draw(screen)

	#[handle_click self, mouse] handles a click event from a mouse click
	#at the (x,y) position specified by [mouse]. It returns True if the event
	#is handled, and False otherwise.
	def handle_click(self, mouse):
		for i in range(len(self.btns) - 1, -1, -1):
			btn = self.btns[i]
			if btn.handle_click(mouse):
				return True
		return False

class Screen:
	def __init__(self, elem, parent = None, child = None):
		self.quit = False
		self.parent = parent
		self.child = None
		self.elem = elem
		self.elem.bind_screen(self)
		self.info = {}

	def draw(self, screen):
		if self.child != None:
			self.child.draw(screen)
		else:
			self.elem.draw(screen)

	def advance_time(self, fps):
		if self.child != None:
			self.child.advance_time(fps)
		else:
			self.elem.advance_time(fps)
			#If my elem has quit
			if self.elem.has_quit():
				if self.parent != None:
					self.parent.on_child_quit()
				self.quit = True

	def handle_click(self, pos):
		if self.child != None:
			self.child.handle_click(pos)
		else:
			self.elem.handle_click(pos)

	def add_child(self, elem):
		child_screen = Screen(elem, parent = self)
		self.child = child_screen

	def get_info(self):
		return self.info

	def put_info(self, new_info):
		self.info = new_info

	def has_quit(self):
		return self.quit

	def on_child_quit(self):
		self.info = self.child.get_info()
		self.child = None
