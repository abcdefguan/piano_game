import pygame
from components import Btn, ImageBtn, Text, Line, Image, Stage

#This is used to render the performance information after completing
#game mode. This implements a UI element required by components/Screen.
#Please refer to components/Screen for documentation on each of the methods.
class AssignScore:
	def __init__(self, wrong_notes, early_notes, timing, score, fps):
		#Various settings
		self.stage = Stage()

		self.colors = {}
		self.colors["blue"] = (39, 117, 242)
		self.colors["black"] = (0, 0, 0)
		self.colors['green'] = (14, 230, 71)
		self.colors['red'] = (224, 9, 9)

		self.quit = False
		self.stage = Stage()
		self.exit_btn = Btn("Exit", (40, 200), on_click = \
			self.on_exit_btn_click)
		expected_dur = 0.0
		num_notes = 0
		total_bars = score.get_total_bars()
		for i in range(total_bars):
			curr_bar = score.get_bar(i)
			expected_dur += curr_bar.get_length() * 60.0 * fps \
			/ curr_bar.get_bpm()
			num_notes += len(curr_bar.get_treble())
			num_notes += len(curr_bar.get_bass())
		used_dur = float(timing)
		pct_time = used_dur / expected_dur * 100
		pct_early = float(early_notes) / num_notes * 100
		pct_wrong = float(wrong_notes) / num_notes * 100
		wrong_notes_txt = Text("Wrong Notes: {}".format(wrong_notes), \
			(20, 20), centering = "topleft")
		early_notes_txt = Text("Early Notes: {0:} ({1:.2f}%)"\
			.format(early_notes, pct_early), (20, 50), centering = "topleft")
		timing_txt = Text("Time Used: {0:.2f}s ({1:.2f}%)" \
			.format(used_dur / fps, pct_time), \
			(20, 80), centering = "topleft")
		expected_time = Text("Expected: {0:.2f}s".format(expected_dur / fps), \
			(20, 110), centering = "topleft")
		#cutoff (pct_wrong, pct_early, pct_time)
		grade_cutoff = [('S', 1.0, 1.0, 110.0), \
		('A', 5.0, 5.0, 125.0), \
		('B', 15.0, 15.0, 140.0), \
		('C', 30.0, 30.0, 180.0), \
		('D', 50.0, 50.0, 200.0)]
		grade = 'F'
		for (cutoff_grade, wrong_cutoff, early_cutoff, time_cutoff) \
		in grade_cutoff:
			if pct_wrong <= wrong_cutoff and pct_early <= early_cutoff and \
			pct_time <= time_cutoff:
				grade = cutoff_grade
				break
		#Assign grade
		grade_txt = Text("{}".format(grade), \
			(160, 140), centering = "center", font_size = 48)

		self.stage.add_btn(self.exit_btn)
		self.stage.add_elt(wrong_notes_txt)
		self.stage.add_elt(early_notes_txt)
		self.stage.add_elt(timing_txt)
		self.stage.add_elt(grade_txt)

	def bind_screen(self, parent_screen):
		self.parent_screen = parent_screen

	def draw(self, screen):
		self.stage.draw(screen)

	def handle_click(self, pos):
		self.stage.handle_click(pos)

	def advance_time(self, fps):
		return True

	def on_exit_btn_click(self, btn, pos):
		self.quit = True

	def has_quit(self):
		return self.quit