##
 # Maker's Digest
 #
 # MCP23017 GPIO Expander Example
 #
 # Dont forget to install the libraries! See README.md for details.
##
from time import sleep          # Import sleep from time
import Adafruit_GPIO.MCP230xx as MCP230XX # Import Adafruit MCP23017 Library

mcp = MCP230XX.MCP23017(address = 0x21)       # Instantiate mcp object
REFRESH_RATE = 30.0                      # Set delay of 1/4 second
quit_pin = 9
prev_low = {0 : False, 1 : False, 2: False, 3: False, 4: False, 5: False, 
			6: False, 7: False, 8: False, 9: False, 10: False, 11: False, 12: False, 13: False
			, 14: False, 15: False, 16: False}

# Setup Outputs. 
# We loop through all 16 GPIO to set them as GPIO.OUT, which
# needs to be referenced as MCP230XX.GPIO.OUT.
#
# If you are only using one or two of the GPIO pins on the 
# mcp23017, you can set them up for outputs individually as:
# mcp.setup(0, MCP230XX.GPIO.OUT)
# OR
# mcp.setup(0, MCP230XX.GPIO.IN)
#
# See Adafruit_Python_GPIO on github for more details on 
# using this library.
for x in range(0, 16):
    mcp.setup(x, MCP230XX.GPIO.IN)
    mcp.pullup(x, 1)

# Main Program
# Loop through all 16 GPIO to set high, then low.
while True:
	done = False
	sleep(1.0 / REFRESH_RATE)
	for pin in range(0 , 16):
		if (not mcp.input(pin)):
			if prev_low[pin] == False:
				print (" ")
				print("Button {} has been pressed".format(pin))
				if pin == quit_pin:
					done = True
		prev_low[pin] = not mcp.input(pin)
	if (done):
		break
