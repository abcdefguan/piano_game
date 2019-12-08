import pygame
from components import Btn, Text, Line, Image, Stage
import simpleaudio as sa
import os

def float_eq(f1, f2):
	return abs(f1 - f2) <= 1e-4

class Bar:
	def __init__(self, bpm, timing, treble, bass):
		self.bpm = bpm
		self.timing = timing
		self.treble = treble
		self.bass = bass

	def get_length(self):
		ans = 0
		for (_, dur) in self.treble:
			ans += dur
		return ans

	def note_at_time(self, time, treble):
		accl = 0
		if treble:
			notes = self.treble
		else:
			notes = self.bass
		for (idx,(_, dur)) in zip(range(len(notes)), notes):
			accl += dur
			if accl >= time:
				return idx
		return len(notes) - 1

	def end_duration(self, idx, treble):
		accl = 0
		if treble:
			notes = self.treble
		else:
			notes = self.bass
		for i in range(idx + 1):
			accl += notes[i][1]
		return accl

	def get_treble(self):
		return self.treble

	def get_bass(self):
		return self.bass

	def get_bpm(self):
		return self.bpm

	def get_timing(self):
		return self.timing

class Score:
	def __init__(self, file_name, note_imgs, player):
		self.note_imgs = note_imgs
		self.player = player
		try:
			with open(file_name, 'r') as file:
				lines = file.readlines()
				#To make sure the last bar is read
				lines.append('\n')
				self.num_bars = 0
				self.valid = True
				self.reason = "File is good"
				#Read metadata
				self.name = lines[0].strip()
				bpm = int(lines[1])
				timing_split = lines[2].strip().split(' ')
				timing = (int(timing_split[0]), int(timing_split[1]))
				#Read score
				#Stores a tuple of <note name> (ie 'A4') and duration (ie 1)
				#A list of lists of tuples (organised by bars)
				#Use sharp to store notes, not flat (ie 'A#4')
				self.bars = []
				bar_no = 1
				bar_treble = []
				bar_bass = []
				bar_treble_len = 0
				bar_bass_len = 0
				#Requires a newline between every bar
				for line_no, note in zip(range(4, len(lines)), lines[4:]):
					note = note.upper()
					#Lines that start with # are comments
					if note.strip().startswith("#"):
						continue
					#New bar number
					elif note == '\n':
						#Assert previous bar is good
						timing_len = timing[0] / timing[1] * 4.0
						if not float_eq(bar_treble_len, timing_len) \
						or not float_eq(bar_bass_len, timing_len):
							self.valid = False
							self.reason = "Bar {} (line {}) appears to \
							be invalid (wrong timing)".format(bar_no, line_no)
							return
						#Add bars to treble and bass, increment bar no
						bar = Bar(bpm, timing, bar_treble, bar_bass)
						self.bars.append(bar)
						bar_treble = []
						bar_bass = []
						bar_treble_len = 0
						bar_bass_len = 0
						bar_no += 1
					elif note.startswith("CHANGE"):
						#Change pace or change timing
						note_split = note.strip().split(' ')
						if (note_split[1] == 'PACE'):
							bpm = int(note_split[2])
						elif (note_split[1] == 'TIMING'):
							timing = (int(note_split[2]), int(note_split[3]))
					else:
						#Parse a normal note
						note_split = note.strip().split(' ')
						if len(note_split) < 3:
							self.valid = False
							self.reason = "Bar {} (line {}) appears to \
							be invalid".format(bar_no, line_no)
							return
						clef = note_split[0]
						#Have commas no spaces for multiple notes
						pitches = note_split[1].split(",")
						for pitch in pitches:
							if not self.player.has_note(pitch):
								self.valid = False
								self.reason = "Note {} in Bar {} (line {}) is not \
								playable".format(pitch, bar_no, line_no)
								return
						duration = float(note_split[2])
						if not self.note_imgs.has_note(duration):
							self.valid = False
							self.reason = "Duration {0:.2f} in Bar {1:} (line {2:}) \
							cannot be displayed".format(duration, bar_no, line_no)
							return
						if clef == 'B':
							bar_bass.append((pitches, duration))
							bar_bass_len += duration
						else:
							bar_treble.append((pitches, duration))
							bar_treble_len += duration
				self.num_bars = bar_no - 1
		except FileNotFoundError:
			self.valid = False
			self.reason = "File not found"
		#except:
		#	self.valid = False
		#	self.reason = "An exception occurred while parsing the file"

	def get_metadata(self):
		return {"name" : self.name}

	def get_total_bars(self):
		return self.num_bars

	def get_bar(self, bar):
		return self.bars[bar]

class RenderedScore:
	def __init__(self, note_imgs, player, score = None):
		self.colors = {"yellow": (244, 247, 35), "black": (0,0,0), \
		"dark_blue": (47, 29, 245)}
		self.note_imgs = note_imgs
		self.player = player
		self.num_bars = 2
		#Used to mark previous notes as black
		self.mark_black = True
		#Used to notate whether to play notes
		self.play_notes = True
		if score == None:
			self.score = None
		else:
			self.replace_score(score)

	def bind_screen(self, parent_screen):
		self.parent_screen = parent_screen

	def replace_score(self, new_score):
		self.score = new_score
		#Advance at 1.0 pace
		self.advance_rate = 1.0
		#Stage with no elements
		self.stage = Stage()
		#Keep track of current state
		#Start at the 0th bar
		self.curr_bar_idx = 0
		#Have not started playing music, set to False when paused
		self.has_started = False
		#Grab current bar
		self.bars = self.get_bars()
		#The current timing in the current bar (based on bar timing and bpm)
		self.curr_timing = 0.0
		#1.0 for normal, -<sth> for rewind, +<sth> for ffwd, 0 for pause
		self.advance_pace = 1.0
		#Add stage elements
		#Add trigger points
		self.left_margin = 10
		self.start_left_margin = 50
		self.right_margin = 310
		self.treble_begin = 70
		self.treble_increment = 10
		self.bass_begin = 160
		self.bass_increment = 10
		#Precompute adjustments
		self.bass_adj = self.get_adj(False)
		self.treble_adj = self.get_adj(True)
		#Add Treble Lines, Clef and Timing
		self.treble_lines = []
		self.treble_clef = Image("img/treble_clef.png", (20, 50), (35, 70))
		self.stage.add_elt(self.treble_clef)
		#30 up to 70
		for i in range(self.treble_begin - 4 * self.treble_increment, \
			self.treble_begin + self.treble_increment, self.treble_increment):
			line = Line((self.left_margin, i), (self.right_margin, i))
			self.treble_lines.append(line)
			self.stage.add_elt(line)
		#Add Bass Lines, Clef and Timing
		self.bass_lines = []
		self.bass_clef = Image("img/bass_clef.png", (25, 135), (35, 35))
		self.stage.add_elt(self.bass_clef)
		#120 up to 160
		for i in range(self.bass_begin - 4 * self.bass_increment, \
			self.bass_begin + self.bass_increment, self.bass_increment):
			line = Line((self.left_margin, i), (self.right_margin, i))
			self.bass_lines.append(line)
			self.stage.add_elt(line)
		#Add bar lines
		#Generate bar lines for left and right edges
		self.bar_lines = [\
		Line((self.left_margin, self.treble_begin - 4 * self.treble_increment),\
		 (self.left_margin,self.treble_begin)), \
		Line((self.left_margin, self.bass_begin - 4 * self.bass_increment),\
		 (self.left_margin,self.bass_begin))]
		
		#Draw bar lines (no changes)
		for bar_idx, bar in zip(range(len(self.bars)), self.bars):
			#Add bar lines
			end_x = self.get_bar_start_x(bar_idx + 1)
			self.bar_lines.append(Line((end_x, self.treble_begin \
			- 4 * self.treble_increment),(end_x,self.treble_begin)))
			self.bar_lines.append(Line((end_x, self.bass_begin \
			- 4 * self.bass_increment),(end_x,self.bass_begin)))
		for bar_line in self.bar_lines:
			self.stage.add_elt(bar_line)
		#Draw current position line
		play_line_pos = self.get_note_horizontal_pos(self.curr_bar_idx, \
			self.curr_timing) + 5
		self.play_line = Line((play_line_pos, self.treble_begin - \
			5 * self.treble_increment), (play_line_pos, self.bass_begin + \
			self.bass_increment))
		self.stage.add_elt(self.play_line)
		#Grab new timings
		self.refresh_timings()

	def refresh_timings(self):
		self.stage.clear_tmp_elts()
		self.bar_numbers = []
		self.timings = []
		self.pace_text = []
		#Grab current bar
		self.bars = self.get_bars()
		prev_timing = (None, None)
		prev_pace = None
		for bar_idx, bar in zip(range(len(self.bars)), self.bars):
			bar_timings = []
			top_timing, bottom_timing = bar.get_timing()
			curr_pace = bar.get_bpm()
			start_x = self.get_bar_start_x(bar_idx)
			bar_idx_norm = self.curr_bar_idx - self.curr_bar_idx % 2
			bar_num = bar_idx_norm + bar_idx + 1
			self.bar_numbers.append(Text(str(bar_num), (start_x + 5, \
				self.treble_begin - 4 * self.treble_increment - 10), \
				font_size = 20))
			if prev_timing != (top_timing, bottom_timing):
				top_timing = str(top_timing)
				bottom_timing = str(bottom_timing)
				bar_timings.append(Text(top_timing, (start_x + 10, 40), \
					font_size = 42))
				bar_timings.append(Text(bottom_timing, (start_x + 10, 62), \
					font_size = 42))
				bar_timings.append(Text(top_timing, (start_x + 10, 130), \
					font_size = 42))
				bar_timings.append(Text(bottom_timing, (start_x + 10, 152), \
					font_size = 42))
			if prev_pace != curr_pace:
				self.pace_text.append(Text(self.pace_to_str(curr_pace), \
					(start_x + 70, self.treble_begin - 4 * \
					self.treble_increment - 10), font_size = 20))
			#Add timings
			prev_timing = bar.get_timing()
			prev_pace = curr_pace
			self.timings.append(bar_timings)
			for timing in bar_timings:
				self.stage.add_tmp_elt(timing)
		for bar_number in self.bar_numbers:
			self.stage.add_tmp_elt(bar_number)
		for text in self.pace_text:
			self.stage.add_tmp_elt(text)
		self.refresh_notes()

	def refresh_notes(self):
		#Draw the notes
		#Stored by bar in same order as self.bars, then list of pitches for
		#each note, then a list of Components for each pitch
		#the note Image is always the last element in the list of Components
		self.treble_note_imgs = []
		self.bass_note_imgs = []
		for bar_idx, bar in zip(range(self.num_bars), self.bars):
			self.treble_bar_imgs = []
			self.add_notes_from_clef(bar_idx, bar.get_treble(), True, \
				self.treble_bar_imgs)
			self.bass_bar_imgs = []
			self.add_notes_from_clef(bar_idx, bar.get_bass(), False, \
				self.bass_bar_imgs)
			self.treble_note_imgs.append(self.treble_bar_imgs)
			self.bass_note_imgs.append(self.bass_bar_imgs)
		for bar in self.treble_note_imgs + self.bass_note_imgs:
			for pitches in bar:
				for pitch in pitches:
					for component in pitch:
						self.stage.add_tmp_elt(component)

	def add_notes_from_clef(self, bar_idx, notes, treble, append_to):
		curr_dur = 0.0
		for pitches, duration in notes:
			note_imgs = []
			x_pos = self.get_note_horizontal_pos(self.curr_bar_idx + bar_idx, \
				curr_dur)
			#print("x_pos: {}".format(x_pos))
			should_force_flip = False
			for pitch in pitches:
				_,_,should_flip = self.pitch_adj_flip(pitch, treble)
				if should_flip:
					should_force_flip = True
					break
			for pitch in pitches:
				note_imgs.append(self.get_note_images(pitch, duration, \
					x_pos, treble, force_flip = should_force_flip))
			append_to.append(note_imgs)
			curr_dur += duration

	def pace_to_str(self, pace):
		pace_text = [(24, "Larghissimo"), (40, "Grave"), (60, "Largo"), \
		(76, "Adagio"), (108, "Andante"), (120, "Moderato"), \
		(156, "Allegro"), (176, "Vivace"), (200, "Presto")]
		pace_name = "Prestissimo"
		for (max_pace, name) in pace_text:
			if pace <= max_pace:
				pace_name = name
				break
		return "{} {}".format(pace_name, int(pace))

	def get_bars(self):
		bars = []
		bar_idx = self.curr_bar_idx - (self.curr_bar_idx % self.num_bars)
		for i in range(bar_idx, min(bar_idx + 2, \
			self.score.get_total_bars())):
			bars.append(self.score.get_bar(i))
		return bars

	def get_bar_start_x(self, bar_idx):
		return self.start_left_margin + \
		float(self.right_margin - self.start_left_margin) * bar_idx \
		/ self.num_bars

	def get_note_horizontal_pos(self, bar_idx, duration):
		bar_pos = bar_idx % self.num_bars
		start_x = self.get_bar_start_x(bar_pos)
		#print("bar_idx: {}, result: {}".format(bar_idx, start_x))
		#Consider position occupied by timing
		if bar_pos == 0 or self.bars[bar_pos].get_timing() \
		!= self.bars[bar_pos - 1].get_timing():
			start_x += 20
		end_x = self.get_bar_start_x(bar_pos + 1)
		bar_duration = self.bars[bar_pos].get_length()
		return start_x + float(end_x - start_x) * duration / bar_duration

	def get_adj(self, treble):
		clef_adj = {'-' : self.treble_increment * 2}
		if treble:
			alphabet = 'F'
			octave = 3
			adj = -6 * float(self.treble_increment) / 2
		else:
			alphabet = 'E'
			octave = 2
			adj = -2 * float(self.bass_increment) / 2
		while octave < 7:
			clef_adj[alphabet + str(octave)] = adj
			alphabet = chr(ord(alphabet) + 1)
			if alphabet > 'G':
				alphabet = 'A'
			if alphabet == 'C':
				octave += 1
			adj += float(self.treble_increment) / 2
		return clef_adj

	def get_note_images(self, pitch, duration, x_pos, treble, force_flip = False):
		#May have to return additional lines to draw certain notes
		images = []
		#Pitch => ie 'A4', duration => ie 1.0
		is_sharp = pitch.find("#") != -1
		is_pause = pitch == '-'
		is_flipped = False
		if force_flip:
			is_flipped = True
		#Remove any sharps
		pitch = pitch.replace("#", "")
		duration = round(duration, 3)
		#Adjust x-axis by 10
		x_pos += 10
		adj = [0, 0]
		pitch_adj = 0
		#Adjust for position
		#if treble:
		#	pitch_adj = self.treble_adj[pitch]
		#	adj[1] = self.treble_begin - pitch_adj
		#else:
		#	pitch_adj = self.bass_adj[pitch]
		#	adj[1] = self.bass_begin - pitch_adj
		#Adjust for flipping
		#if pitch_adj >= 2 * self.treble_increment:
		#	is_flipped = True
		(adj, pitch_adj, should_flip) = self.pitch_adj_flip(pitch, treble)
		if should_flip:
			is_flipped = True
		#Draw extra lines if note is too low
		num_adj_lines = - int(pitch_adj) // int(self.treble_increment)
		for i in range(num_adj_lines):
			if treble:
				images.append(Line((x_pos - 10, self.treble_begin + (i + 1) * \
					self.treble_increment), (x_pos + 10, self.treble_begin + \
					(i + 1) * self.treble_increment)))
			else:
				images.append(Line((x_pos - 10, self.bass_begin + (i + 1) * \
					self.bass_increment), (x_pos + 10, self.bass_begin + \
					(i + 1) * self.bass_increment)))
		#Draw extra lines if note is too high
		num_adj_lines = (int(pitch_adj) - 4 * int(self.treble_increment)) // \
		int(self.treble_increment)
		for i in range(num_adj_lines):
			if treble:
				images.append(Line((x_pos - 10, self.treble_begin - (i + 5) * \
					self.treble_increment), (x_pos + 10, self.treble_begin - \
					(i + 5) * self.treble_increment)))
			else:
				images.append(Line((x_pos - 10, self.bass_begin - (i + 5) * \
					self.bass_increment), (x_pos + 10, self.bass_begin - \
					(i + 5) * self.bass_increment)))
		#Adjust for image
		img_adjustments = {1.0 : [(0, -13), (0, +14), (0, 0)], \
		2.0: [(0, -13), (0, +14), (0, -2)], \
		3.0: [(0, -13), (0, +14), (0, -2)], \
		4.0: [(0, 0), (0, 0), (0, -7)], \
		1.5: [(0, -13), (0, +14), (0, 0)], \
		0.5: [(+4, -13), (-4, +14), (0, 0)], \
		0.75: [(+4, -13), (-4, +14), (0, 0)], \
		0.25: [(+4, -13), (-4, +14), (0, 0)]}
		img_adj = (0, 0)
		if duration in img_adjustments:
			if not is_flipped and not is_pause:
				#Normal Note
				img_adj = img_adjustments[duration][0]
			elif is_pause:
				img_adj = img_adjustments[duration][2]
			else:
				img_adj = img_adjustments[duration][1]
			
		adj[0] += img_adj[0]
		adj[1] += img_adj[1]
		#Adjust for sharp
		if is_sharp:
			images.append(Text("#", (x_pos - 10, adj[1] - img_adj[1]),\
			 font_size = 20))
			#adj[0] += 10
		#Grab image and adjust
		img_surf = self.note_imgs.get_note(duration, rest = is_pause, \
			flip = is_flipped)
		images.append(Image(img_surf, (x_pos + adj[0], adj[1]), \
			from_surf = True))
		return images

	def pitch_adj_flip(self, pitch, treble):
		#Remove any sharps
		pitch = pitch.replace("#", "")
		adj = [0,0]
		is_flipped = False
		#Adjust for position
		if treble:
			pitch_adj = self.treble_adj[pitch]
			adj[1] = self.treble_begin - pitch_adj
		else:
			pitch_adj = self.bass_adj[pitch]
			adj[1] = self.bass_begin - pitch_adj
		#Adjust for flipping
		if pitch_adj >= 2 * self.treble_increment:
			is_flipped = True
		return (adj, pitch_adj, is_flipped)

	def adjust_pace(self, new_pace):
		#1.0 for normal, -<sth> for rewind, +<sth> for ffwd, 0 for pause
		self.advance_rate = new_pace

	def advance_time(self, fps):
		#Check if completed
		if self.curr_bar_idx >= self.score.get_total_bars():
			return
		#Move play line
		play_line_pos = self.get_note_horizontal_pos(self.curr_bar_idx, \
			self.curr_timing) + 5
		self.play_line.change_x(play_line_pos, play_line_pos)
		curr_bar = self.score.get_bar(self.curr_bar_idx)
		#Resume the piece
		if not self.has_started:
			self.has_started = True
			treble_pitches = self.get_curr_pitches(True)
			bass_pitches = self.get_curr_pitches(False)
			if self.play_notes:
				self.player.play_note(treble_pitches)
				self.player.play_note(bass_pitches)
			#Mark the playing notes as dark blue
			self.change_timing_note_color(self.curr_timing, \
				self.colors["dark_blue"], True)
			self.change_timing_note_color(self.curr_timing, \
				self.colors["dark_blue"], False)
		else:
			#Advance the current time
			bpm = curr_bar.get_bpm()
			prev_timing = self.curr_timing
			prev_treble = curr_bar.note_at_time(self.curr_timing, True)
			prev_bass = curr_bar.note_at_time(self.curr_timing, False)
			self.curr_timing += float(self.advance_rate) * bpm / 60.0 / fps
			new_treble = curr_bar.note_at_time(self.curr_timing, True)
			new_bass = curr_bar.note_at_time(self.curr_timing, False)
			treble = curr_bar.get_treble()
			bass = curr_bar.get_bass()
			#Transition notes when changing timing
			if prev_treble != new_treble:
				prev_treble_pitches = treble[prev_treble][0]
				if self.play_notes:
					self.player.stop_note(prev_treble_pitches)
				self.on_note_stop(prev_treble_pitches, True)
				if self.play_notes:
					self.player.play_note(treble[new_treble][0])
				if self.mark_black:
					self.change_timing_note_color(prev_timing, \
					self.colors["black"], True)
				self.change_timing_note_color(self.curr_timing, \
					self.colors["dark_blue"], True)
			if prev_bass != new_bass:
				prev_bass_pitches = bass[prev_bass][0]
				if self.play_notes:
					self.player.stop_note(prev_bass_pitches)
				self.on_note_stop(prev_bass_pitches, False)
				if self.play_notes:
					self.player.play_note(bass[new_bass][0])
				if self.mark_black:
					self.change_timing_note_color(prev_timing, \
					self.colors["black"], False)
				self.change_timing_note_color(self.curr_timing, \
					self.colors["dark_blue"], False)
		#Move to next bar when available
		if self.curr_timing > curr_bar.get_length():
			#Stop current notes
			prev_treble_pitches = self.get_curr_pitches(True)
			prev_bass_pitches = self.get_curr_pitches(False)
			if self.play_notes:
				self.player.stop_note(prev_treble_pitches)
				self.player.stop_note(prev_bass_pitches)
				self.player.stop_all()
			self.on_note_stop(prev_treble_pitches, True)
			self.on_note_stop(prev_bass_pitches, False)
			#Mark the stopped notes as black
			if self.mark_black:
				self.change_timing_note_color(self.curr_timing, \
					self.colors["black"], True)
				self.change_timing_note_color(self.curr_timing, \
					self.colors["black"], False)
			self.curr_timing -= curr_bar.get_length()
			self.curr_bar_idx += 1
			#Update notes if required
			if self.curr_bar_idx % self.num_bars == 0 and \
			self.curr_bar_idx < self.score.get_total_bars():
				self.refresh_timings()
			#Play treble and bass notes for next bar if possible
			if self.curr_bar_idx < self.score.get_total_bars():
				if self.play_notes:
					self.player.play_note(self.get_curr_pitches(True))
					self.player.play_note(self.get_curr_pitches(False))
				#Mark the playing notes as yellow
				self.change_timing_note_color(self.curr_timing, \
					self.colors["dark_blue"], True)
				self.change_timing_note_color(self.curr_timing, \
					self.colors["dark_blue"], False)

	#Called after all the notes and bars have changed
	def on_note_stop(self, pitches, treble):
		return True

	def get_curr_pitches(self, treble):
		curr_bar = self.score.get_bar(self.curr_bar_idx)
		if treble:
			notes = curr_bar.get_treble()
		else:
			notes = curr_bar.get_bass()
		pitches,_ = notes[curr_bar.note_at_time(self.curr_timing, treble)]
		return pitches

	def jump_to_next_timing(self):
		#print("Changing color")
		bar_idx = self.curr_bar_idx % self.num_bars
		curr_bar = self.score.get_bar(self.curr_bar_idx)
		treble_idx = curr_bar.note_at_time(self.curr_timing, True)
		bass_idx = curr_bar.note_at_time(self.curr_timing, False)
		treble_dur = curr_bar.end_duration(treble_idx, True)
		bass_dur = curr_bar.end_duration(bass_idx, False)
		timing_jump = min(treble_dur, bass_dur) + 0.01 - self.curr_timing
		self.curr_timing += timing_jump
		self.on_early_note_release(timing_jump)

	def on_early_note_release(self, timing_jump):
		return True

	def change_timing_note_color(self, timing, new_color, treble):
		#print("Changing color")
		bar_idx = self.curr_bar_idx % self.num_bars
		curr_bar = self.score.get_bar(self.curr_bar_idx)
		#print(self.treble_note_imgs)
		#print("Timing: {}".format(timing))
		if treble:
			treble_idx = curr_bar.note_at_time(timing, True)
			for pitch in self.treble_note_imgs[bar_idx][treble_idx]:
				pitch[-1].change_color(new_color)
		else:
			bass_idx = curr_bar.note_at_time(timing, False)
			for pitch in self.bass_note_imgs[bar_idx][bass_idx]:
				pitch[-1].change_color(new_color)

	def change_curr_pitch_color(self, pitches, new_color):
		bar_idx = self.curr_bar_idx % self.num_bars
		curr_bar = self.score.get_bar(self.curr_bar_idx)
		timing = self.curr_timing
		treble_idx = curr_bar.note_at_time(timing, True)
		treble = curr_bar.get_treble()
		bass = curr_bar.get_bass()
		for pitch, imgs in zip(treble[treble_idx][0], \
			self.treble_note_imgs[bar_idx][treble_idx]):
			if pitch in pitches:
				imgs[-1].change_color(new_color)
		bass_idx = curr_bar.note_at_time(timing, False)
		for pitch, imgs in zip(bass[bass_idx][0], \
			self.bass_note_imgs[bar_idx][bass_idx]):
			if pitch in pitches:
				imgs[-1].change_color(new_color)

	def handle_click(self, pos):
		self.stage.handle_click(pos)

	def draw(self, screen):
		#TODO: Move stage elements to correct position, update stage state
		self.stage.draw(screen)

	def has_quit(self):
		return self.curr_bar_idx >= self.score.get_total_bars()

#class Training

class NoteImgCache:
	def __init__(self):

		def to_flipped_arr(path):
			res = [path]
			split_idx = path.find('.', 1)
			file_name = path[:split_idx]
			extension = path[split_idx:]
			res.append(file_name + "_flip" + extension)
			res.append(file_name + "_rest" + extension)
			return res

		def to_surface(path):
			img = pygame.image.load(path)
			#Change the size of note if required to fit the divisions
			#print(transform_path)
			#print(path)
			if path in transform_path:
				img = pygame.transform.scale(img, transform_path[path])
			return img.convert_alpha()

		#Manually calibrate all the note images
		base_path = './img/'
		note_path = {0.25: 'semiquaver.png', 0.375: 'semiquaver_dot.png', \
		0.5: 'quaver.png', 0.75: 'quaver_dot.png', 1.0: 'crotchet.png', \
		1.5: 'crotchet_dot.png', 2.0 : 'minim.png', 3.0: 'minim_dot.png', \
		4.0: 'semibreve.png'}
		transform_path = {}
		for note in ['crotchet.png', 'crotchet_flip.png', \
		'minim.png', 'minim_flip.png']:
			transform_path[base_path + note] = (10, 36)#(15, 45)'
		for note in ['minim_dot.png', 'minim_dot_flip.png', \
		'crotchet_dot.png', 'crotchet_dot_flip.png']:
			transform_path[base_path + note] = (16, 36)
		for note in ['semibreve.png', 'semibreve_flip.png']:
			transform_path[base_path + note] = (12, 10)
		for note in ['semibreve_rest.png', 'minim_rest.png', \
		'minim_dot_rest.png']:
			transform_path[base_path + note] = (10, 6)
		for note in ['minim_dot_rest.png']:
			transform_path[base_path + note] = (14, 6)
		for note in ['crotchet_rest.png']:
			transform_path[base_path + note] = (15, 40)
		for note in ['quaver.png', 'quaver_flip.png']:
			transform_path[base_path + note] = (20, 36)
		for note in ['crotchet_dot_rest.png']:
			transform_path[base_path + note] = (20, 40)
		for note in ['quaver_rest.png', 'semiquaver_rest.png']:
			transform_path[base_path + note] = (12, 20)
		for note in ['quaver_dot.png', 'quaver_dot_flip.png']:
			transform_path[base_path + note] = (25, 36)
		for note in ['quaver_dot_rest.png']:
			transform_path[base_path + note] = (16, 20)
		for note in ['semiquaver.png', 'semiquaver_flip.png']:
			transform_path[base_path + note] = (25, 36)

		self.notes = {dur: [to_surface(p) for p in \
		to_flipped_arr(base_path + path)] for (dur,path) in note_path.items()}

	def has_note(self, dur):
		return round(dur, 3) in self.notes

	def get_note(self, dur, rest = False, flip = False):
		fail = [None, None, None]
		if rest:
			return self.notes.get(round(dur, 3), fail)[2]
		elif flip:
			return self.notes.get(round(dur, 3), fail)[1]
		else:
			return self.notes.get(round(dur, 3), fail)[0]

class AudioPlayer:
	def __init__(self):
		self.note_wav = {}
		self.playing = {}
		#Load all the sound files into wave objects (cached)
		sound_dir = "./sound"
		for file_name in os.listdir(sound_dir):
			if file_name.endswith(".wav"):
				ext_pos = file_name.find(".wav")
				note_name = file_name[:ext_pos]
				wav_obj = sa.WaveObject.from_wave_file(sound_dir + "/" + file_name)
				self.note_wav[note_name] = wav_obj

	def __del__(self):
		sa.stop_all()

	def has_note(self, pitch):
		if pitch == '-':
			return True
		return pitch in self.note_wav

	def play_note(self, pitches):
		for pitch in pitches:
			if pitch in self.playing:
				self.stop_note(pitch)
			if pitch in self.note_wav:
				self.playing[pitch] = self.note_wav[pitch].play()

	def stop_note(self, pitches):
		for pitch in pitches:
			if pitch in self.playing:
				self.playing.pop(pitch).stop()

	def stop_all(self):
		sa.stop_all()
		self.playing = {}

	def finish(self):
		sa.stop_all()
		self.playing = {}