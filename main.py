import sys
import time
import threading
import pygame
import os
import RPi.GPIO as GPIO
from main_ui import MainUI
from components import Btn, ImageBtn, Text, Line, Image, Stage, Screen
from music import NoteImgCache, AudioPlayer, Score
from piano import PianoMode
from score_select import ScoreSelect
from training import TrainingScore
from game import GameScore
from input import KeyboardInput, BtnInput

#Declare environment variables to drive output onto PiTFT Screen
os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb1')
os.putenv('SDL_MOUSEDRV', 'TSLIB')
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

#Define some colors
black = (0,0,0)
white = (255,255,255)

#Setup GPIO
GPIO.setmode(GPIO.BCM)

#An event listener for the quit button that quits the program
def quit_game(channel):
	global should_quit
	should_quit = True

quit_pin = 17
#Setup Pin
GPIO.setup(quit_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
#Setup Callbacks
GPIO.add_event_detect(quit_pin, GPIO.FALLING, callback = quit_game)

#Setup pygame stuff
pygame.init()

#Specify size of game display
size = width, height = 320,240

#Generate the display surface
screen = pygame.display.set_mode(size)

#Flag to check if we're done
should_quit = False
#Set framerate
fps = 30

#Obtain scores
note_img_cache = NoteImgCache()
player = AudioPlayer()
key_input = KeyboardInput()

scores = []
for file_name in os.listdir("./scores"):
	if file_name.endswith(".scr"):
		score = Score("./scores/" + file_name, note_img_cache, player)
		if not score.valid:
			print("{} is invalid. Error: {}".format(file_name, score.reason))
		else:
			scores.append(score)

#Get a training mode score
#main_disp = Screen(TrainingScore(note_img_cache, player, \
#	key_input, score = scores[1]))
#main_disp = Screen(GameScore(note_img_cache, player, \
#	key_input, score = scores[0]))
#main_disp = Screen(ScoreSelect(note_img_cache, player, \
#	key_input, scores, fps, train_mode = False))
main_disp = Screen(MainUI(note_img_cache, player, key_input, scores, fps))
#main_disp = Screen(TrainingScore(note_img_cache, player, \
#	key_input, score = scores[1]))
#Setup button objects
#stage = Stage([])

#Start the pygame clock
clock = pygame.time.Clock()
while (not main_disp.has_quit() and not should_quit):
	#Do stuff
	screen.fill(white)
	#Draw stage objects
	#stage.draw(screen)
	#Move training display forward
	main_disp.advance_time(fps)

	#Handle clicks
	for evt in pygame.event.get():
		#If mouse button pressed down
		if (evt.type == pygame.MOUSEBUTTONDOWN):
			main_disp.handle_click(evt.pos)

	#Draw training display
	main_disp.draw(screen)

	pygame.display.flip()
	#Wait until the next frame
	clock.tick(fps)

#Cleanup when done
GPIO.cleanup()
