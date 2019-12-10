import pygame
from components import Btn, ImageBtn, Text, Line, Image, Stage
from music import RenderedScore

#This class plays out the game mode
class GameScore(RenderedScore):
	"""
	[__init__ self note_imgs player key_input score] creates a new
	game mode using the specified
	[note_imgs] a NoteImgCache object
	[player] an AudioPlayer object
	[key_input] either a KeyboardInput / BtnInput
	[score] a Score object
	"""
	def __init__(self, note_imgs, player, key_input, score = None):
		super().__init__(note_imgs, player, score)
		#Leave previous notes as is
		self.mark_black = False
		#Don't play notes on advance
		self.play_notes = False
		#Various parameters
		#tolerance of 0.2 notes
		self.early_tolerance = 0.2
		
		self.colors['green'] = (14, 230, 71)
		self.colors['red'] = (224, 9, 9)
		#Take in key inputs
		self.key_input = key_input
		self.playable_pitches = key_input.get_playable_pitches()
		#Set of currently played pitches
		self.played_pitches = set()
		#Various parameters
		self.early_notes = 0
		self.wrong_notes = 0
		self.frames_used = 0
		#FSM State
		self.WAITING = 0
		self.PLAYING = 1
		self.fsm_state = self.WAITING
		self.quit = False
		#Construct buttons
		self.exit_btn = Btn("Exit", (40, 200), on_click = \
			self.on_exit_btn_click)
		self.stage.add_btn(self.exit_btn)

	#[on_exit_btn_click self btn pos] is called when the exit
	#button is called
	def on_exit_btn_click(self, btn, pos):
		self.quit = True
		info = self.parent_screen.get_info()
		#Remove these information from info
		remove_elems = ["early_notes", "wrong_notes", "frames_used"]
		for elem in remove_elems:
			if elem in info:
				info.pop(elem)

	#[on_early_note_release self timing_jump] is triggered when a note is
	#released early by the player. [timing_jump] is the amount of crotchets
	#missed when we jump to the next note.
	def on_early_note_release(self, timing_jump):
		if timing_jump >= self.early_tolerance:
			#print("Early Note!!")
			self.early_notes += 1
			#Stop all non playable notes

	#[on_note_stop self pitches treble] is called when we transition
	#between bars or between notes. [pitches] refer to the pitches which
	#are stopped and [treble] refers to the clef (Treble if True, Bass if False)
	def on_note_stop(self, pitches, treble):
		#Change to waiting state
		self.fsm_state = self.WAITING
		#print("Stopping")
		#Discard all played pitches
		for pitch in pitches:
			if pitch in self.played_pitches:
				self.played_pitches.remove(pitch)
			#Stop all non playable notes
			if pitch not in self.playable_pitches:
				self.player.stop_note([pitch])

	#[advance_time self fps] steps through one frame at [fps] frames
	#per second. This causes the playback to advance according to
	#[self.advance_rate]
	def advance_time(self, fps):
		self.frames_used += 1
		#Consume updates from input
		#Use input directly when paused
		#Get current pitches
		if self.has_quit():
			return
		treble_pitches = self.get_curr_pitches(True)
		bass_pitches = self.get_curr_pitches(False)
		expected_pitches = treble_pitches + bass_pitches

		self.key_input.poll()
		updates = self.key_input.get_updates()
		for pitch, is_pressed in updates.items():
			#print("Update: {}, {}".format(pitch, is_pressed))
			if is_pressed:
				self.played_pitches.add(pitch)
				self.player.play_note([pitch])
				if pitch not in expected_pitches:
					#print("Wrong Note!!")
					self.wrong_notes += 1
			elif pitch in self.played_pitches:
				self.played_pitches.remove(pitch)
				self.player.stop_note([pitch])
			else:
				self.player.stop_note([pitch])
		
		corr_pitches = set()
		missing_pitches = set()
		extra_pitches = set()
		unplayable_pitches = set()
		for pitch in expected_pitches:
			if pitch not in self.playable_pitches:
				corr_pitches.add(pitch)
				unplayable_pitches.add(pitch)
			elif pitch in self.played_pitches:
				corr_pitches.add(pitch)
			else:
				missing_pitches.add(pitch)
		for pitch in self.played_pitches:
			if pitch not in expected_pitches:
				extra_pitches.add(pitch)
		#transition into playing state if every note is good
		self.change_curr_pitch_color(corr_pitches, self.colors['green'])
		self.change_curr_pitch_color(missing_pitches, self.colors['red'])
		if self.fsm_state == self.WAITING and len(missing_pitches) == 0 \
		and len(extra_pitches) == 0:
			self.fsm_state = self.PLAYING
			#Play any non playable notes
			for pitch in unplayable_pitches:
				self.player.play_note([pitch])
		elif self.fsm_state == self.PLAYING and len(missing_pitches) != 0:
			#print("Early Stop!!")
			self.early_notes += 1
			self.fsm_state = self.WAITING
			#Stop unplayable pitches
			for pitch in unplayable_pitches:
				self.player.stop_note([pitch])
			self.jump_to_next_timing()
			super().advance_time(fps)
		elif self.fsm_state == self.PLAYING:
			super().advance_time(fps)
		if super().has_quit():
			info = self.parent_screen.get_info()
			info["early_notes"] = self.early_notes
			info["wrong_notes"] = self.wrong_notes
			info["frames_used"] = self.frames_used

	#[has_quit self] queries whether this score has quitted
	def has_quit(self):
		if super().has_quit():
			return True
		else:
			return self.quit