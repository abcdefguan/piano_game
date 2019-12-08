import pygame
from components import Btn, ImageBtn, Text, Line, Image, Stage
from music import NoteImgCache, AudioPlayer
from piano import PianoMode
from score_select import ScoreSelect
from training import TrainingScore
from game import GameScore
from input import KeyboardInput, BtnInput

class MainUI:
	def __init__(self, note_img, player, key_input, scores, fps):
		self.fps = fps
		self.note_img_cache = note_img
		self.player = player
		self.key_input = key_input
		self.scores = scores

		self.quit = False
		training_btn = Btn("Training", (250, 40), on_click = \
			self.on_training_btn_click)
		game_btn = Btn("Play", (250, 80), on_click = \
			self.on_play_btn_click)
		piano_btn = Btn("Piano", (250, 120), on_click = \
			self.on_piano_btn_click)
		exit_btn = Btn("Quit", (250, 200), on_click = \
			self.on_exit_btn_click)
		piano_game_txt = Text("Piano Game", (100, 40))
		dev_by_txt = Text("By Guanqun Wu, Zhaopeng Xu", (100, 80), \
			font_size = 20)

		self.stage = Stage()
		self.stage.add_btn(training_btn)
		self.stage.add_btn(game_btn)
		self.stage.add_btn(piano_btn)
		self.stage.add_btn(exit_btn)
		self.stage.add_elt(piano_game_txt)
		self.stage.add_elt(dev_by_txt)

	def bind_screen(self, parent_screen):
		self.parent_screen = parent_screen

	def draw(self, screen):
		self.stage.draw(screen)

	def handle_click(self, pos):
		self.stage.handle_click(pos)

	def advance_time(self, fps):
		return True

	def on_training_btn_click(self, btn, pos):
		select = ScoreSelect(self.note_img_cache, self.player, self.key_input, \
			self.scores, self.fps, True)
		self.parent_screen.add_child(select)

	def on_play_btn_click(self, btn, pos):
		select = ScoreSelect(self.note_img_cache, self.player, self.key_input, \
			self.scores, self.fps, False)
		self.parent_screen.add_child(select)

	def on_piano_btn_click(self, btn, pos):
		piano = PianoMode(self.player, self.key_input)
		self.parent_screen.add_child(piano)

	def on_exit_btn_click(self, btn, pos):
		self.quit = True

	def has_quit(self):
		return self.quit