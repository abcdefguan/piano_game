import pygame
from components import Btn, ImageBtn, Text, Line, Image, Stage

#This enables the user to play the game like a normal piano
#This simply implements the UI elem required by components/Screen
class PianoMode:
	def __init__(self, player, key_input):
		self.stage = Stage()
		self.player = player
		self.key_input = key_input
		self.playable_pitches = key_input.get_playable_pitches()
		#Set of currently played pitches
		self.played_pitches = set()
		#Various parameters
		self.quit = False
		#Construct buttons
		self.exit_btn = Btn("Exit", (40, 200), on_click = \
			self.on_exit_btn_click)
		self.piano_mode_txt = Text("Piano Mode", (160, 20))
		self.notes_played_txt = Text("", (20, 100), centering = "topleft")
		self.stage.add_btn(self.exit_btn)
		self.stage.add_elt(self.piano_mode_txt)
		self.stage.add_elt(self.notes_played_txt)

	def on_exit_btn_click(self, btn, pos):
		self.quit = True

	def advance_time(self, fps):
		#Consume updates from input
		#print(self.key_input)
		self.key_input.poll()
		updates = self.key_input.get_updates()
		for pitch, is_pressed in updates.items():
			#print("Update: {}, {}".format(pitch, is_pressed))
			if is_pressed:
				self.played_pitches.add(pitch)
				self.player.play_note([pitch])
			elif pitch in self.played_pitches:
				self.played_pitches.remove(pitch)
				self.player.stop_note([pitch])
		if (len(updates) > 0):
			notes_played = ""
			for pitch in self.played_pitches:
				notes_played += pitch
				notes_played += " "
			self.notes_played_txt.text = notes_played

	def bind_screen(self, parent_screen):
		self.parent_screen = parent_screen

	def draw(self, screen):
		#print("Drawing")
		self.stage.draw(screen)

	def handle_click(self, pos):
		self.stage.handle_click(pos)

	def has_quit(self):
		return self.quit