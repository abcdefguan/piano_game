import pygame
from components import Btn, ImageBtn, Text, Line, Image, Stage
from music import RenderedScore

#This class implements the training mode
class TrainingScore(RenderedScore):
	"""
	[__init__ self note_imgs player key_input score] creates a new
	training score with specified
	[note_imgs] a NoteImgCache
	[player] an AudioPlayer
	[key_input] an Input (KeyboardInput / BtnInput)
	[score] a Score
	"""
	def __init__(self, note_imgs, player, key_input, score = None):
		super().__init__(note_imgs, player, score)
		self.colors['green'] = (14, 230, 71)
		self.colors['red'] = (224, 9, 9)
		#Take in key inputs
		self.key_input = key_input
		self.playable_pitches = key_input.get_playable_pitches()
		self.quit = False
		self.paused = False
		self.playback_rate_idx = 4
		self.playback_rates = [0.25, 0.33, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
		#Set of currently played pitches
		self.played_pitches = set()
		#Construct buttons
		self.play_btn = ImageBtn('./img/pause.png', (80, 200), on_click = \
			self.on_play_btn_click, dimen = (20, 20))
		self.exit_btn = Btn("Exit", (40, 200), on_click = \
			self.on_exit_btn_click)
		self.slow_btn = ImageBtn('./img/slow.png', (120, 200), \
			on_click = self.on_slow_btn_click, dimen = (20, 20))
		self.ffwd_btn = ImageBtn('./img/fast_forward.png', (160, 200), \
			on_click = self.on_ffwd_btn_click, dimen = (20, 20))
		self.pace_txt = Text("1.0x Pace", (240, 200), font_size = 20)
		self.stage.add_btn(self.play_btn)
		self.stage.add_btn(self.exit_btn)
		self.stage.add_btn(self.slow_btn)
		self.stage.add_btn(self.ffwd_btn)
		self.stage.add_elt(self.pace_txt)

	"""
	[on_play_btn_click self btn pos] is called when the play/pause
	button is clicked
	"""
	def on_play_btn_click(self, btn, pos):
		if not self.paused:
			self.paused = True
			self.advance_rate = 0.0
			self.has_started = False
			self.player.stop_all()
			self.play_btn.change_img('./img/play.png', dimen = (20, 20))
		else:
			self.paused = False
			self.player.stop_all()
			self.advance_rate = self.playback_rates[self.playback_rate_idx]
			self.play_btn.change_img('./img/pause.png', dimen = (20, 20))

	"""
	[on_exit_btn_click self btn pos] is called when the exit button is clicked
	"""
	def on_exit_btn_click(self, btn, pos):
		self.quit = True

	"""
	[on_ffwd_btn_click self btn pos] is called when the faster
	button is clicked
	"""
	def on_ffwd_btn_click(self, btn, pos):
		self.adjust_pace(1)

	"""
	[on_slow_btn_click self btn pos] is called when the slower button
	is clicked
	"""
	def on_slow_btn_click(self, btn, pos):
		self.adjust_pace(-1)

	"""
	[adjust_pace self adjust] adjusts the pace based on the defined paces
	and ensures that the pace never goes too low. It adjusts the index of the
	defined paces list by [adjust]
	"""
	def adjust_pace(self, adjust):
		self.playback_rate_idx += adjust
		if self.playback_rate_idx < 0:
			self.playback_rate_idx = 0
		elif self.playback_rate_idx >= len(self.playback_rates):
			self.playback_rate_idx = len(self.playback_rates) - 1
		if not self.paused:
			self.advance_rate = self.playback_rates[self.playback_rate_idx]
		self.pace_txt.text = "{}x Pace" \
		.format(self.playback_rates[self.playback_rate_idx])

	#[on_note_stop self pitches treble] is called when we transition
	#between bars or between notes. [pitches] refer to the pitches which
	#are stopped and [treble] refers to the clef (Treble if True, Bass if False)
	def on_note_stop(self, pitches, treble):
		#Discard all played pitches
		for pitch in pitches:
			if pitch in self.played_pitches:
				self.played_pitches.remove(pitch)

	#[advance_time self fps] steps through one frame at [fps] frames
	#per second. This causes the playback to advance according to
	#[self.advance_rate]
	def advance_time(self, fps):
		if not self.paused:
			super().advance_time(fps)
		#Consume updates from input
		#Use input directly when paused
		self.key_input.poll()
		updates = self.key_input.get_updates()
		for pitch, is_pressed in updates.items():
			#print("Update: {}, {}".format(pitch, is_pressed))
			if is_pressed:
				self.played_pitches.add(pitch)
				if self.paused:
					self.player.play_note([pitch])
			elif pitch in self.played_pitches:
				self.played_pitches.remove(pitch)
				if self.paused:
					self.player.stop_note([pitch])
		#Get current pitches
		if self.has_quit():
			return
		treble_pitches = self.get_curr_pitches(True)
		bass_pitches = self.get_curr_pitches(False)
		corr_pitches = set()
		wrong_pitches = set()
		for pitch in treble_pitches + bass_pitches:
			if pitch not in self.playable_pitches:
				corr_pitches.add(pitch)
			elif pitch in self.played_pitches:
				corr_pitches.add(pitch)
			else:
				wrong_pitches.add(pitch)
		self.change_curr_pitch_color(corr_pitches, self.colors['green'])
		self.change_curr_pitch_color(wrong_pitches, self.colors['red'])

	#[has_quit self] queries whether this score has quitted
	def has_quit(self):
		if super().has_quit():
			return True
		else:
			return self.quit