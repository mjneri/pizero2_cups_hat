#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# test_button.py
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Author: mjneri
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Module Name: test_button.py
# Description:
#
# Revisions:
# Revision 0.01 - File Created (January 2, 2024)
# Additional Comments:
#
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# Library imports
import time
import subprocess
import busio
import adafruit_ssd1306
import RPi.GPIO as io

from PIL import Image, ImageDraw, ImageFont
from board import SCL, SDA

# -------- Setup Code ----------
io.setmode(io.BCM)
ledstat = 1

btn_left = 5 #GPIO5
btn_enter = 6 #GPIO6
btn_right = 26 #GPIO26

led_green = 23
led_orange = 24
led_red = 25

io.setup(led_green, io.OUT)
io.setup(led_orange, io.OUT)
io.setup(led_red, io.OUT)

# Reference for init code is from link below
# https://raspberrypihq.com/use-a-push-button-with-raspberry-pi-gpio/
io.setup(btn_left, io.IN, pull_up_down=io.PUD_UP)
io.setup(btn_enter, io.IN, pull_up_down=io.PUD_UP)
io.setup(btn_right, io.IN, pull_up_down=io.PUD_UP)

# Create the I2C interface for the OLED
i2c = busio.I2C(SCL, SDA)

# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height.  Change these
# to the right size for your display!
disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

# Clear display.
disp.fill(0)
disp.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new("1", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0


# Load default font.
font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 9)

while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # Shell scripts for system monitoring from here:
    # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
    # cmd = "hostname -I | cut -d' ' -f1"
    # IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
    # cmd = 'cut -f 1 -d " " /proc/loadavg'
    # CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
    MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
    # cmd = 'df -h | awk \'$NF=="/"{printf "Disk: %d/%d GB  %s", $3,$2,$5}\''
    # Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")

    # Display button status
    stat_left = "released"
    stat_enter = "released"
    stat_right = "released"

    if io.input(btn_left) == io.LOW:
        stat_left = "pressed"
        io.output(led_green, 1)
    else:
        io.output(led_green, 0)

    if io.input(btn_enter) == io.LOW:
        stat_enter = "pressed"

    if io.input(btn_right) == io.LOW:
        stat_right = "pressed"
        io.output(led_red, 1)
    else:
        io.output(led_red, 0)

    # Write four lines of text.

    # draw.text((x, top + 0), "IP: " + IP, font=font, fill=255)
    # draw.text((x, top + 0), "CPU load: " + CPU, font=font, fill=255)
    draw.text((x, top + 0), MemUsage, font=font, fill=255)
    # draw.text((x, top + 25), Disk, font=font, fill=255)
    draw.text((x, top + 8), "Left: " + stat_left, font=font, fill=255)
    draw.text((x, top + 16), "Enter: " + stat_enter, font=font, fill=127)
    draw.text((x, top + 24), "Right: " + stat_right, font=font, fill=255)

    # Display image.
    disp.image(image)
    disp.show()

    # Blink LED
    io.output(led_orange, ledstat)
    ledstat = ledstat ^ 1
    time.sleep(0.1)
