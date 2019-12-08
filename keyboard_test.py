from input import BtnInput, KeyboardInput
from music import AudioPlayer
from time import sleep
import pygame

REFRESH_RATE = 30.0



#Setup pygame stuff
pygame.init()

#Specify size of game display
#size = width, height = 320,240

#Generate the display surface
#screen = pygame.display.set_mode(size)

test_input = KeyboardInput() #BtnInput()
player = AudioPlayer()

#Specify size of game display
size = width, height = 320,240

#Generate the display surface
screen = pygame.display.set_mode(size)

while True:
	screen.fill((255,255,255))
	test_input.poll()
	updates = test_input.get_updates()
	pygame.event.get()
	for pitch, is_pressed in updates.items():
		if is_pressed:
			player.play_note([pitch])
		else:
			player.stop_note([pitch])
	pygame.display.flip()
	sleep(1.0 / REFRESH_RATE)