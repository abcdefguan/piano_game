import pygame
from components import Btn, ImageBtn, Text, Line, Image, Stage
from training import TrainingScore
from game import GameScore
from assign_score import AssignScore

#This is used to select a score to be played in either training mode or game
#mode. This implements a UI element required by components/Screen.
#Please refer to components/Screen for documentation on each of the methods.
class ScoreSelect:
	def __init__(self, note_img_cache, player, key_input, scores \
		, fps, train_mode = True):
		#Various settings
		self.stage = Stage()
		self.scores_per_page = 4

		#Set various attributes
		self.scores = scores
		self.img_cache = note_img_cache
		self.player = player
		self.key_input = key_input
		self.train_mode = train_mode
		self.fps = fps

		self.colors = {}
		self.colors["blue"] = (39, 117, 242)
		self.colors["black"] = (0, 0, 0)

		self.quit = False
		self.score_btns = {}
		self.score_to_idx = {}
		self.curr_idx = 0
		self.sel_idx = -1
		self.return_from_mode = False
		self.stage = Stage()
		self.exit_btn = Btn("Exit", (40, 200), on_click = \
			self.on_exit_btn_click)
		self.select_btn = Btn("Select", (260, 180), on_click = \
			self.on_select_btn_click)
		self.up_btn = ImageBtn("./img/up.png", (260, 40), on_click = \
			self.on_up_btn_click, dimen = (20, 20))
		self.down_btn = ImageBtn("./img/down.png", (260, 120), on_click = \
			self.on_down_btn_click, dimen = (20, 20))
		self.stage.add_btn(self.exit_btn)
		self.stage.add_btn(self.up_btn)
		self.stage.add_btn(self.down_btn)
		self.stage.add_btn(self.select_btn)
		self.refresh_scores()

	def bind_screen(self, parent_screen):
		self.parent_screen = parent_screen

	def draw(self, screen):
		self.stage.draw(screen)

	def handle_click(self, pos):
		self.stage.handle_click(pos)

	def refresh_scores(self):
		for _,btn in self.score_btns.items():
			self.stage.remove_btn(btn)
		#Maps index to button objects
		self.score_btns = {}
		#Maps score name to index
		self.score_to_idx = {}
		for i in range(self.curr_idx, min(self.curr_idx + \
			self.scores_per_page, len(self.scores))):
			score_name = self.scores[i].get_metadata()["name"]
			score_btn = Btn(score_name, (130, 40 + \
				(i - self.curr_idx) * 30), \
				on_click = self.on_score_btn_click, \
				font_size = 24)
			self.stage.add_btn(score_btn)
			#Make blue if selected
			if i == self.sel_idx:
				score_btn.color = self.colors["blue"]
			self.score_to_idx[score_name] = i
			self.score_btns[i] = score_btn

	def advance_time(self, fps):
		if self.return_from_mode:
			self.return_from_mode = False
			info = self.parent_screen.get_info()
			if "early_notes" in info:
				score_disp = AssignScore(info.pop("wrong_notes"), \
					info.pop("early_notes"), info.pop("frames_used"), \
					self.scores[self.sel_idx], fps)
				self.parent_screen.add_child(score_disp)

	def on_exit_btn_click(self, btn, pos):
		self.quit = True

	def on_up_btn_click(self, btn, pos):
		if self.curr_idx - self.scores_per_page >= 0:
			self.curr_idx -= self.scores_per_page
			self.sel_idx = -1
		self.refresh_scores()

	def on_down_btn_click(self, btn, pos):
		if self.curr_idx + self.scores_per_page < len(self.scores):
			self.curr_idx += self.scores_per_page
			self.sel_idx = -1
		self.refresh_scores()

	def on_select_btn_click(self, btn, pos):
		if self.sel_idx != -1:
			score = self.scores[self.sel_idx]
			if self.train_mode:
				train = TrainingScore(self.img_cache, self.player, \
					self.key_input, score = score)
				#This passes off control to the training screen
				self.parent_screen.add_child(train)
				self.return_from_mode = True
			else:
				game = GameScore(self.img_cache, self.player, \
					self.key_input, score = score)
				#This passes off control to the training screen
				self.parent_screen.add_child(game)
				self.return_from_mode = True

	def on_score_btn_click(self, btn, pos):
		btn_idx = self.score_to_idx[btn.text]
		if self.sel_idx in self.score_btns:
			self.score_btns[self.sel_idx].color = self.colors["black"]
		self.sel_idx = btn_idx
		self.score_btns[self.sel_idx].color = self.colors["blue"]

	def has_quit(self):
		return self.quit