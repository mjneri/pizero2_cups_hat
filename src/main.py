#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# main.py - Application code for the CUPS Hat
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Author: mjneri
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Module Name: main.py
# Description: Displays information on a 128x32 OLED display.
#
# Revisions:
# Revision 0.01 - File Created (March 24, 2024)
# Additional Comments:
#
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Module Includes
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

import cups_hat_display as CUPS_Hat
import time
import threading

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Global Variables
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

flag_tick_heartbeat = False
flag_tick_oled_update = False

# Tick rates
tick_rate_oled_update = 0.1        # Refresh rate - 10Hz
tick_rate_heartbeat = 0.25         # Blink LED every 250ms

# Kill threads?
flag_kill_threads = False

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Application tasks
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# TODO: Complete this function
def app_cleanup():
    """
    Function is called before shutting down or exiting the app
    """
# END OF def app_cleanup()

# TODO: Define all task methods with "task_" before the name
# Refer to Task State Diagram in OneNote
def task_oled_update(cups_hat: CUPS_Hat):
    global flag_tick_oled_update
    if flag_tick_oled_update is True:
        flag_tick_oled_update = False
        cups_hat.oled_update()
# END OF def task_oled_update()

def task_oled_prepare_framebuffer(cups_hat: CUPS_Hat):
    """
    Paste Icons and text box to the frame buffer
    depending on the current menu selected.
    """
    cups_hat.menu_prepare_framebuffer()

# END OF def task_oled_prepare_framebuffer()

def task_check_inputs(cups_hat: CUPS_Hat):
    """
    Non-blocking task that checks button inputs and updates current menu and other attributes
    """
    btn_left = cups_hat.btn_left
    btn_right = cups_hat.btn_right
    btn_enter = cups_hat.btn_enter

    # Check LEFT button
    if cups_hat.is_button_ev_det(btn_left):
        cups_hat.menu_change_left()
    else:
        pass

    # Check RIGHT button
    if cups_hat.is_button_ev_det(btn_right):
        cups_hat.menu_change_right()
    else:
        pass

    # Check ENTER button
    if cups_hat.is_button_ev_det(btn_enter):
        # TODO: Figure out when to execute commands... on button press, or periodically (i.e., for System Info)?
        if cups_hat.current_menu in range(CUPS_Hat.MENU_MAIN_FIRST, CUPS_Hat.MENU_MAIN_LIMIT):
                cups_hat.run_command()

        cups_hat.menu_change_enter()
    else:
        pass

# END OF def task_check_inputs()

def task_led_status(cups_hat: CUPS_Hat):
    """
    Task that updates the LEDs/Neopixels to indicate system status
    """
    global flag_tick_heartbeat
    if flag_tick_heartbeat is True:
        flag_tick_heartbeat = False
        cups_hat.heartbeat()
# END OF def task_led_status()

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Thread functions
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

def thread_oled_timer(tick_rate):
    global flag_tick_oled_update
    while not flag_kill_threads:
        flag_tick_oled_update = True
        time.sleep(tick_rate)

def thread_heartbeat_timer(tick_rate):
    global flag_tick_heartbeat
    while not flag_kill_threads:
        flag_tick_heartbeat = True
        time.sleep(tick_rate)


#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Main Application
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# Define the Class instance as a global variable to allow methods to be called during Keyboard Interrupts
cups_hat = CUPS_Hat.CUPS_Hat()

if __name__ == '__main__':
    try:
        """ Main application """
        # Start threads
        thread_1 = threading.Thread(target=thread_oled_timer, args=(tick_rate_oled_update,))
        thread_2 = threading.Thread(target=thread_heartbeat_timer, args=(tick_rate_heartbeat,))

        thread_1.start()
        thread_2.start()

        cups_hat.display_startup()
        print("Starting display...")

        while True:
            # Call each task
            task_check_inputs(cups_hat)
            task_oled_prepare_framebuffer(cups_hat)
            task_oled_update(cups_hat)
            task_led_status(cups_hat)

    except KeyboardInterrupt:
        flag_kill_threads = True
        thread_1.join()
        thread_2.join()

        print("\nEnding test....")
        cups_hat.display_shutdown()

    except SystemExit:
        #TODO: Replace or remove this SystemExit processing later.
        #NOTE: SystemExit is the exception result of calling exit()
        flag_kill_threads = True
        thread_1.join()
        thread_2.join()

        print("Byeee")
        cups_hat.display_shutdown()