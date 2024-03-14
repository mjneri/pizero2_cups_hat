#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# cups_hat_display.py - A simple menu/display for a CUPS Hat
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Author: mjneri
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Module Name: cups_hat_display.py
# Description: Displays information on a 128x32 OLED display.
#
# Revisions:
# Revision 0.01 - File Created (January 14, 2024)
# Additional Comments:
#
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Module Includes
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

import time                 # Used for delays
import subprocess           # Used for getting outputs of shell commands
import busio                # Used for the I2C bus
import adafruit_ssd1306     # Used to drive the SSD1306 OLED
import RPi.GPIO as io       # Used to setup IO on the Pi Zero 2
import enum                 # Used to create enumerations
import os                   # Used to execute shell commands

from PIL import Image, ImageDraw, ImageFont, ImageOps     # Used for image processing
from board import SCL, SDA                      # Used with the I2C bus.

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Class Defines
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

"""
There are definitely better ways of implementing this project.
For now, this will do. Feel free to leave comments/raise issues
if you have any improvement ideas to suggest.
"""

class CUPS_Hat:
    # Define class constants
    OLED_WIDTH = 128
    OLED_HEIGHT = 32

    OLED_TEXT_BOX_WIDTH = 80
    OLED_TEXT_BOX_HEIGHT = 26

    # Define X-Y COORDS Constants
    # TODO: FINISH THESE DEFINES
    POS_OLED_ICON = (14, 8)         # for the icon
    POS_OLED_NAVI_LEFT = (1, 12)
    POS_OLED_NAVI_RIGHT = (119, 12)
    POS_OLED_TEXT_BOX = (36, 5)

    POS_OLED_TEXT_BOX_LINE1 = (3, -2)
    POS_OLED_TEXT_BOX_LINE2 = (3, 9)

    # Define something...
    # TODO: FINISH THIS ENUM DEFINITION
    class asset_indx(enum.IntEnum):
        ASSET_ICON_REBOOT        = 0
        ASSET_ICON_PRINTER       = 1
        ASSET_ICON_POWER         = 2
        ASSET_ICON_PRINTER_INFO  = 3
        ASSET_ICON_INFO          = 4

        ASSET_NAVI_RIGHT        = 0
        ASSET_NAVI_LEFT         = 1

    def __init__(self):
        """
        Define all the attributes
        """
        #TODO: Initialize some of the attributes below straight from shell commands instead of 0 at first.
        self.is_idle = False        # Bool that indicates whether the system is idle
        self.current_menu = self.asset_indx.ASSET_ICON_PRINTER_INFO     # Default menu at startup.
        self.printer_status = 0     # 0 is ok, -1 not ok.
        self.sys_ip_address = 0
        self.sys_temperature = 0
        self.is_startup = True      # TODO: FIND OUT WTF THIS IS.
        self.is_command = False     # Sticky bit that indicates whether a command was executed.

        """ Raspberry Pi GPIOs """
        self.btn_left = 5       # GPIO5
        self.btn_enter = 6      # GPIO6
        self.btn_right = 26     # GPIO26
        self.led_green = 23     # GPIO23
        self.led_orange = 24    # GPIO24
        self.led_red = 25       # GPIO25

        # Initialize the IOs
        io.setmode(io.BCM)
        io.setup(self.led_green, io.OUT)
        io.setup(self.led_orange, io.OUT)
        io.setup(self.led_red, io.OUT)

        # Reference for code below is from link: https://raspberrypihq.com/use-a-push-button-with-raspberry-pi-gpio/
        # Enable internal pull ups
        io.setup(self.btn_left, io.IN, pull_up_down=io.PUD_UP)
        io.setup(self.btn_enter, io.IN, pull_up_down=io.PUD_UP)
        io.setup(self.btn_right, io.IN, pull_up_down=io.PUD_UP)

        # Register event detection
        while True:
            try:
                io.add_event_detect(self.btn_left, io.FALLING, bouncetime=200)
            except:
                pass
            else:
                break

        while True:
            try:
                io.add_event_detect(self.btn_enter, io.RISING, bouncetime=200)      # Execute command only when button is let go
            except:
                pass
            else:
                break

        while True:
            try:
                io.add_event_detect(self.btn_right, io.FALLING, bouncetime=200)
            except:
                pass
            else:
                break
        
        """ ENDOF Raspberry Pi GPIOs """


        """ OLED Initialization """
        self.oled_obj = adafruit_ssd1306.SSD1306_I2C(self.OLED_WIDTH, self.OLED_HEIGHT, busio.I2C(SCL, SDA))
        self.oled_obj.fill(0)
        self.oled_obj.show()

        # Create framebuffer using Pillow
        # Make sure to create frameBuffer with mode '1' for 1-bit color.
        self.img_framebuffer = Image.new("1", (self.OLED_WIDTH, self.OLED_HEIGHT))
        
        # Get drawing object to draw on frameBuffer & draw black box to clear it.
        self.img_draw_handle = ImageDraw.Draw(self.img_framebuffer)
        self.img_draw_handle.rectangle((0, 0, self.OLED_WIDTH, self.OLED_HEIGHT), outline=0, fill=0)

        # Create Framebuffer for the text box.
        self.text_framebuffer = Image.new("1", (self.OLED_TEXT_BOX_WIDTH, self.OLED_TEXT_BOX_HEIGHT))
        self.text_draw_handle = ImageDraw.Draw(self.text_framebuffer)
        """ ENDOF OLED Initialization """


        # TODO: Add Attributes for tick rates here.
        self.start_time = 0
        self.current_time = 0
        self.flag_tick_heartbeat = False
        self.flag_tick_oled_update = False
        
        # Load default font
        self.img_font = ImageFont.truetype("fonts/PixelOperator.ttf", size=16)

        # Load all assets
        self.asset_list = [
            Image.open("assets/reboot icon.png").convert("1"),
            Image.open("assets/printer icon.png").convert("1"),
            Image.open("assets/power icon.png").convert("1"),
            Image.open("assets/printer info icon.png").convert("1"),
            Image.open("assets/info icon.png").convert("1")
        ]

        self.invert_asset_list = [
            ImageOps.invert(self.asset_list[self.asset_indx.ASSET_ICON_REBOOT]),
            ImageOps.invert(self.asset_list[self.asset_indx.ASSET_ICON_PRINTER]),
            ImageOps.invert(self.asset_list[self.asset_indx.ASSET_ICON_POWER]),
            ImageOps.invert(self.asset_list[self.asset_indx.ASSET_ICON_PRINTER_INFO]),
            ImageOps.invert(self.asset_list[self.asset_indx.ASSET_ICON_INFO])
        ]

        self.navi_asset_list = [
            Image.open("assets/right_icon.png").convert("1"),
            Image.open("assets/left icon.png").convert("1")
        ]

        self.invert_navi_asset_list = [
            ImageOps.invert(self.navi_asset_list[self.asset_indx.ASSET_NAVI_RIGHT]),
            ImageOps.invert(self.navi_asset_list[self.asset_indx.ASSET_NAVI_LEFT])
        ]

        self.menu_item_names_list = [
            "Reboot",
            "Print\nTest Page",
            "Shutdown",
            "Printer\nInfo",
            "System\nInfo"
        ]
    

    def display_startup(self):
        """
        Display startup animation to show during bootup.
        """
        # TODO: Improve this one. Create new logos?
        self.framebuffer_clear()
        self.text_draw_handle.text(self.POS_OLED_TEXT_BOX_LINE1, "Welcome!\nStartup!", font=self.img_font, fill=255, spacing=-2)

        self.img_framebuffer.paste(self.asset_list[self.asset_indx.ASSET_ICON_PRINTER], self.POS_OLED_ICON)
        self.img_framebuffer.paste(self.text_framebuffer, self.POS_OLED_TEXT_BOX)

        self.oled_update()

        time.sleep(0.2)

        for i in range (175, 0, -5):
            self.oled_obj.contrast(i)
            time.sleep(0.01)

        for i in range (0, 175):
            self.oled_obj.contrast(i)
            time.sleep(0.01)

        time.sleep(0.2)
        self.oled_clear()

    def display_shutdown(self):
        """
        Display a closing animation.
        """
        self.framebuffer_clear()
        self.text_draw_handle.text(self.POS_OLED_TEXT_BOX_LINE1, "Goodbye!\nShutdown!", font=self.img_font, fill=255, spacing=-2)

        self.img_framebuffer.paste(self.asset_list[self.asset_indx.ASSET_ICON_POWER], self.POS_OLED_ICON)
        self.img_framebuffer.paste(self.text_framebuffer, self.POS_OLED_TEXT_BOX)

        self.oled_update()

        time.sleep(0.2)

        for i in range (175, 0, -1):
            self.oled_obj.contrast(i)
            time.sleep(0.01)

        time.sleep(0.2)
        self.oled_clear()

    def oled_update(self):
        """
        Refresh the OLED
        """
        self.oled_obj.image(self.img_framebuffer)
        self.oled_obj.show()

    def oled_clear(self):
        """
        Clear the OLED
        """
        self.oled_obj.fill(0)
        self.oled_obj.show()

    # TODO: Improve the comment below.
    def is_button_pressed(self, button) -> bool:
        """
        Check if button is pressed.
        button == self.btn_left, etc.
        """
        if io.input(button) == io.LOW:
            return True
        else:
            return False

    # TODO: Improve the comment below.
    def is_button_held(self, button) -> bool:
        """
        Check if button is held.
        button == self.btn_left, etc.
        """

    def is_command_executed(self) -> bool:
        """
        Sticky bit - returns true only on first call.
        """
        retval = self.is_command
        self.is_command = False
        return retval

    # TODO: Complete this function.
    def run_command(self):
        """
        Run a command based on the current menu.
        """
        match self.current_menu:
            case self.asset_indx.ASSET_ICON_REBOOT:
                #os("reboot")
                print("REBOOT!")
                os.system("vcgencmd measure_temp")
            case self.asset_indx.ASSET_ICON_PRINTER:
                # Print Test page...
                #os("lp -d WiFi_HP_Ink_Tank_115 /usr/share/cups/data/testprint")
                print("TEST PRINT")
            case self.asset_indx.ASSET_ICON_POWER:
                # Shutdown...
                #os("poweroff")
                print("POWEROFF!")
                exit()
            case self.asset_indx.ASSET_ICON_PRINTER_INFO:
                # Get printer info using shell commands...
                print("PRINTER INFO!")
                pass
            case self.asset_indx.ASSET_ICON_INFO:
                # Get other info (ip address, temp etc)
                print("SYSTEM INFO!")
                pass

    def framebuffer_clear(self):
        """
        Clear the framebuffers
        """
        self.img_draw_handle.rectangle((0, 0, self.OLED_WIDTH, self.OLED_HEIGHT), outline=0, fill=0)
        self.text_draw_handle.rectangle((0, 0, self.OLED_TEXT_BOX_WIDTH, self.OLED_TEXT_BOX_HEIGHT), outline=0, fill=0)

    def heartbeat(self):
        """
        Periodically blink the heartbeat LED.
        """

    def millis(self) -> int:
        """
        Non-blocking timer-check function.
        Similar to millis() in Arduino
        """
        # Multiply by 1000 to get time in ms.
        return round(time.time() * 1000)

    # TODO: Define all task methods with "task_" before the name
    # Refer to Task State Diagram in OneNote
    def task_oled_update(self):
        self.oled_update()

    def task_oled_prepare_framebuffer(self):
        """
        Paste Icons and text box to the frame buffer
        depending on the current menu selected.
        """
        # Empty the framebuffers first.
        self.framebuffer_clear()

        # Prepare contents of the text box first.
        # TODO: Display different text depending on whether is_command_executed returned true.
        # Ex: if user selects Print Test Page, it should display "Printing test page..." for a few seconds...
        self.text_draw_handle.text(self.POS_OLED_TEXT_BOX_LINE1, self.menu_item_names_list[self.current_menu], font=self.img_font, fill=255, spacing=-2)

        # Prepare the Icon
        if self.is_button_pressed(self.btn_enter) == True:
            self.img_framebuffer.paste(self.invert_asset_list[self.current_menu], self.POS_OLED_ICON)
        else:    
            self.img_framebuffer.paste(self.asset_list[self.current_menu], self.POS_OLED_ICON)

        # Paste text box to the main frame buffer.
        self.img_framebuffer.paste(self.text_framebuffer, self.POS_OLED_TEXT_BOX)

        if self.is_button_pressed(self.btn_left) == True:
            self.img_framebuffer.paste(self.invert_navi_asset_list[self.asset_indx.ASSET_NAVI_LEFT], self.POS_OLED_NAVI_LEFT)
        else:
            self.img_framebuffer.paste(self.navi_asset_list[self.asset_indx.ASSET_NAVI_LEFT], self.POS_OLED_NAVI_LEFT)

        if self.is_button_pressed(self.btn_right) == True:
            self.img_framebuffer.paste(self.invert_navi_asset_list[self.asset_indx.ASSET_NAVI_RIGHT], self.POS_OLED_NAVI_RIGHT)
        else:
            self.img_framebuffer.paste(self.navi_asset_list[self.asset_indx.ASSET_NAVI_RIGHT], self.POS_OLED_NAVI_RIGHT)


    def task_check_inputs(self):
        """
        Non-blocking task that checks button inputs and updates current menu and other attributes
        """
        # Check LEFT button
        if io.event_detected(self.btn_left):
            if self.current_menu == self.asset_indx.ASSET_ICON_REBOOT:
                self.current_menu = self.asset_indx.ASSET_ICON_INFO
            else:
                self.current_menu = self.current_menu - 1
        else:
            pass

        # Check RIGHT button
        if io.event_detected(self.btn_right):
            if self.current_menu == self.asset_indx.ASSET_ICON_INFO:
                self.current_menu = self.asset_indx.ASSET_ICON_REBOOT
            else:
                self.current_menu = self.current_menu + 1
        else:
            pass

        # Check ENTER button
        if io.event_detected(self.btn_enter):
            self.run_command()
        else:
            pass

    def task_tick_updater(self):
        """
        Task that updates flag variables
        to represent the tick rate for other tasks.
        """
        # if self.millis() - self.tick_init

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Main Application
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# Define the Class instance as a global variable to allow methods to be called during Keyboard Interrupts
cups_hat = CUPS_Hat()

def main():
    """ Main application """
    cups_hat.display_startup()

    while True:
        # Call each task
        cups_hat.task_check_inputs()
        cups_hat.task_oled_prepare_framebuffer()
        cups_hat.task_oled_update()




if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nEnding test....")
        cups_hat.display_shutdown()
    except SystemExit:
        #TODO: Replace or remove this SystemExit processing later.
        #NOTE: SystemExit is the exception result of calling exit()
        print("Byeee")
        cups_hat.display_shutdown()