#This is a deprecated library that works with Python 2 and does not
#require circuitPy
import Adafruit_GPIO.MCP230xx as MCP230XX # Import Adafruit MCP23017 Library
import pygame

#An input class that provides input through physical buttons using the MCP230XX
class BtnInput:
	"""
	[__init__] saves the bindings from keys to pitches and initialises
	the state of the input
	"""
	def __init__(self):
		#2 frames at 30fps (~66ms)
		self.debounce = 2
		#I2C addresses where we can find our port expander
		addresses = [0x20, 0x21]
		self.mcps = [MCP230XX.MCP23017(address = addr) for addr in addresses]
		#port mappings
		self.port_mappings = [{'C4': 4, 'C#4': 8, 'D4': 3, 'D#4': 9, \
		'E4': 15, 'F4': 14, 'F#4': 10,'G4': 13, 'G#4': 7, 'A4': 12,\
		'A#4': 6, 'B4': 11},{'C3': 13, 'C#3': 0, 'D3': 12, 'D#3': 1, \
		'E3': 11, 'F3': 10, 'F#3': 2, 'G3': 9, 'G#3': 15, 'A3': 8,\
		'A#3': 14, 'B3': 3}]
		self.LOW = 0
		self.HIGH = 1
		#current state
		self.state = []
		#cooldowns
		self.cooldown = []
		self.updates = {}
		for mcp,mappings in zip(self.mcps, self.port_mappings):
			state = {}
			cooldown = {}
			for _,pin in mappings.items():
				#Setup pin as input
				mcp.setup(pin, MCP230XX.GPIO.IN)
				mcp.pullup(pin, 1)
    			#Create initial state and cooldown
				state[pin] = self.HIGH
				cooldown[pin] = self.debounce
			self.state.append(state)
			self.cooldown.append(cooldown)

	"""
	[get_playable_pitches self] returns the set of playable pitches that
	this input maps to
	"""
	def get_playable_pitches(self):
		ans = set()
		for port_mapping in self.port_mappings:
			for pitch,_ in port_mapping.items():
				ans.add(pitch)
		return ans

	"""
	[poll self] polls the inputs for updates and updates the state.
	This needs to be called every game frame.
	"""
	def poll(self):
		for mcp,mappings,state,cooldown in \
		zip(self.mcps, self.port_mappings, self.state, self.cooldown):
			for pitch,pin in mappings.items():
				#Decrement cooldowns
				if cooldown[pin] > 0:
					cooldown[pin] -= 1
				#Check for changed pins, update them and push updates
				if mcp.input(pin) != state[pin] and \
				cooldown[pin] == 0:
					state[pin] = mcp.input(pin)
					#Not because we're active low
					self.updates[pitch] = not mcp.input(pin)

	#[has_updates self] returns whether this object has any updates
	def has_updates(self):
		return len(self.updates) > 1

	#[get_updates self] returns a dictionary mapping pitches to new state
	#(True = Active, False = Inactive) indicating updates since the
	#previous call to [get_updates]
	def get_updates(self):
		updates = self.updates
		self.updates = {}
		return updates

#An input class that provides input through the keyboard
class KeyboardInput:
	"""
	[__init__] saves the bindings from keys to pitches and initialises
	the state of the input
	"""
	def __init__(self):
		#Bindings from keys to pitches
		self.port_mappings = {'G3': pygame.K_a, 'G#3': pygame.K_w,\
		'A3': pygame.K_s, 'A#3': pygame.K_e, 'B3': pygame.K_d, \
		'C4': pygame.K_f, 'C#4': pygame.K_t, \
		'D4': pygame.K_g, 'D#4': pygame.K_y,'E4': pygame.K_h, \
		'F4': pygame.K_j, 'F#4': pygame.K_i, 'G4': pygame.K_k, \
		'G#4': pygame.K_o, 'A4': pygame.K_l,\
		'A#4': pygame.K_p, 'B4': pygame.K_SEMICOLON}
		self.state = pygame.key.get_pressed()
		self.updates = {}

	"""
	[get_playable_pitches self] returns the set of playable pitches that
	this input maps to
	"""
	def get_playable_pitches(self):
		ans = set()
		for pitch,_ in self.port_mappings.items():
			ans.add(pitch)
		return ans

	"""
	[poll self] polls the inputs for updates and updates the state.
	This needs to be called every game frame.
	"""
	def poll(self):
		new_state = pygame.key.get_pressed()
		for pitch,key in self.port_mappings.items():
			if new_state[key] != self.state[key]:
				self.updates[pitch] = new_state[key]
		self.state = new_state

	#[has_updates self] returns whether this object has any updates
	def has_updates(self):
		return len(self.updates) > 1

	#[get_updates self] returns a dictionary mapping pitches to new state
	#(True = Active, False = Inactive) indicating updates since the
	#previous call to [get_updates]
	def get_updates(self):
		updates = self.updates
		self.updates = {}
		#print(updates)
		return updates
