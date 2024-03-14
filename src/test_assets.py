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

from PIL import Image, ImageDraw, ImageFont, ImageOps
from board import SCL, SDA

# -------- Setup Code ----------
io.setmode(io.BCM)
ledstat = 1

btn_left = 5 #GPIO5
btn_enter = 6 #GPIO6
btn_right = 26 #GPIO26
# Reference for init code is from link below
# https://raspberrypihq.com/use-a-push-button-with-raspberry-pi-gpio/
io.setup(btn_left, io.IN, pull_up_down=io.PUD_UP)
io.setup(btn_enter, io.IN, pull_up_down=io.PUD_UP)
io.setup(btn_right, io.IN, pull_up_down=io.PUD_UP)

# led_green = 23
# led_orange = 24
# led_red = 25

# Create the I2C interface for the OLED
i2c = busio.I2C(SCL, SDA)

# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height.  Change these
# to the right size for your display!
oledObj = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

# Clear display.
oledObj.fill(0)
oledObj.show()

# Create blank image frame buffer for drawing.
# Make sure to create frameBuffer with mode '1' for 1-bit color.
img_framebuffer = Image.new("1", (oledObj.width, oledObj.height))

# Get drawing object to draw on frameBuffer.
drawHandle = ImageDraw.Draw(img_framebuffer)

# Draw a black filled box to clear the frameBuffer.
drawHandle.rectangle((0, 0, oledObj.width, oledObj.height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
# padding = -2
# top = padding
# bottom = oledObj.height - padding
# # Move left to right keeping track of the current x position for drawing shapes.
# x = 0


# Load default font.
font = ImageFont.truetype("fonts/PixelOperator.ttf", size=16)

# 2024-01-06: Logo test. Load all logos
# Ref: https://github.com/adafruit/Adafruit_CircuitPython_SSD1306/blob/main/examples/ssd1306_pillow_image_display.py
# NOTE TO SELF: For the actual application, "#define" the 2-tuples for the coordinates below.
# display icons first + inverted versions
logo_reboot = Image.open("assets/reboot icon.png").convert("1")
logo_printer = Image.open("assets/printer icon.png").convert("1")
logo_power = Image.open("assets/power icon.png").convert("1")
logo_printer_info = Image.open("assets/printer info icon.png").convert("1")
logo_info = Image.open("assets/info icon.png").convert("1")

asset_list = [Image.open("assets/printer icon.png").convert("1"), 
              Image.open("assets/printer info icon.png").convert("1"), 
              Image.open("assets/info icon.png").convert("1")]

# 2024-01-08: Invert test
inv_logo_reboot =       ImageOps.invert(logo_reboot)
inv_logo_printer =      ImageOps.invert(logo_printer)
inv_logo_power =        ImageOps.invert(logo_power)
inv_logo_printer_info = ImageOps.invert(logo_printer_info)
inv_logo_info =         ImageOps.invert(logo_info)


# navigation icons next w/ inverted versions
ico_right = Image.open("assets/right_icon.png").convert("1")
ico_left = Image.open("assets/left icon.png").convert("1")

inv_ico_right = ImageOps.invert(ico_right)
inv_ico_left = ImageOps.invert(ico_left)

# drawHandle.text((36, 5), "Test Page", font=font, fill=255)

# 2024-01-08 New Test: Create separate "image" for the text.
# Create blank image frame buffer for drawing text and manipulating image. Make sure to create frameBuffer with mode '1' for 1-bit color.
text_framebuffer = Image.new("1", (80, 26))
text_drawhandle = ImageDraw.Draw(text_framebuffer)        # Get drawing object to draw on frameBuffer.
text_drawhandle.text((3, -2), "Print", font=font, fill=255)     # This seems to match what I have in the .psd file - found via trial and error. Will keep this
text_drawhandle.text((3, 9), "Test Page", font=font, fill=255)  # 2-tuple value.
# inverted_text = ImageOps.invert(text_framebuffer)


# 2024-1-08: Put stuff on the framebuffer
# #img_framebuffer.paste(logo_reboot, (4,4))
# # img_framebuffer.paste(logo_printer, (16,5))
# 2024-01-08 Default icon to display is printer logo.
current_icon = logo_printer

img_framebuffer.paste(current_icon, (14,8))
img_framebuffer.paste(ico_left, (1,12))
img_framebuffer.paste(ico_right, (119,12))
# img_framebuffer.paste(inverted_text, (36, 5))
img_framebuffer.paste(text_framebuffer, (36, 5))

# Show the framebuffer contents on the OLED
oledObj.image(img_framebuffer)
oledObj.show()

# 2024-01-08 User Input and basic navigation test.
while True:
    # Draw a black filled box to clear the image.
    drawHandle.rectangle((0, 0, oledObj.width, oledObj.height), outline=0, fill=0)

    # Display button status
    if io.input(btn_left) == io.LOW:
        img_framebuffer.paste(inv_ico_left, (1,12))
        current_icon = logo_reboot
        text_drawhandle.rectangle((0, 0, 80, 26), outline=0, fill=0)
        text_drawhandle.text((3, 4), "Reboot", font=font, fill=255)
    else:
        img_framebuffer.paste(ico_left, (1,12))


    if io.input(btn_enter) == io.LOW:
        img_framebuffer.paste(inv_logo_printer, (14,8))
        current_icon = asset_list[0]
    else:
        img_framebuffer.paste(logo_printer, (14,8))
        current_icon = asset_list[1]


    if io.input(btn_right) == io.LOW:
        img_framebuffer.paste(inv_ico_right, (119,12))
        current_icon = logo_power
        text_drawhandle.rectangle((0, 0, 80, 26), outline=0, fill=0)
        text_drawhandle.text((3, 4), "Shutdown", font=font, fill=255)
    else:
        img_framebuffer.paste(ico_right, (119,12))

    # Prepare and paste text to framebuffer
    # text_drawhandle.text((3, -2), "Print", font=font, fill=255)     # This seems to match what I have in the .psd file - found via trial and error. Will keep this
    # text_drawhandle.text((3, 9), "Test Page", font=font, fill=255)  # 2-tuple value.
    # 2024-01-08: Multiline text test instead of printing two lines individually like above.
    # text_drawhandle.multiline_text((3,-2), "Print\nTest Page", font=font, fill=255, spacing=-2)
    #inverted_text = ImageOps.invert(text_framebuffer)
    img_framebuffer.paste(text_framebuffer, (36, 5))

    
    img_framebuffer.paste(current_icon, (14,8))

    # Display image.
    oledObj.image(img_framebuffer)
    oledObj.show()
