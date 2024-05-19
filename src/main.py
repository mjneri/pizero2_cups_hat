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
    hat = cups_hat

    # TODO: Clean up the code here because it will get messy once I add logic for processing different menus.
    # Step 1: Empty the framebuffers first.
    hat.framebuffer_clear()

    # Step 2: Prepare contents of the text box.
    # TODO: Display different text depending on whether is_command_executed returned true.
    # Ex: if user selects Print Test Page, it should display "Printing test page..." for a few seconds...
    if hat.current_menu in range(hat.MENU_SUB_SYSINFO_P1, hat.MENU_SUB_SYSINFO_P2 + 1):
        # TODO: Consider running commands for the Sys Info sub menu to periodically get temperatures, mem info, etc.
        # TODO: Consider creating a new text box for sub menus...
        # TODO: Use ImageFont.load_default() for the Sys Info sub-menu to use smaller text.
        hat.img_draw_handle.text((10, 1), "This is temporary\nText.", font=hat.img_font, fill=255, spacing=-2)
    else:
        hat.text_draw_handle.text(hat.POS_OLED_TEXT_BOX_LINE1, hat.menu_item_names_list[hat.current_menu], font=hat.img_font, fill=255, spacing=-2)

    # Step 3: Prepare the icon
    if hat.current_menu in range(hat.MENU_MAIN_REBOOT, hat.MENU_MAIN_SYS_INFO + 1):
        if hat.is_button_pressed(hat.btn_enter) == True:
            hat.img_framebuffer.paste(hat.invert_asset_list[hat.current_menu], hat.POS_OLED_ICON)
        else:    
            hat.img_framebuffer.paste(hat.asset_list[hat.current_menu], hat.POS_OLED_ICON)

    # Step 4: Paste text box to the main frame buffer.
    if hat.current_menu in range(hat.MENU_MAIN_REBOOT, hat.MENU_MAIN_SYS_INFO + 1):
        hat.img_framebuffer.paste(hat.text_framebuffer, hat.POS_OLED_TEXT_BOX)

    # Step 5: Invert left/right icons depending on the menu.
    # TODO: Display only right icon for MENU_SUB_SYSINFO_P1, and left icon only for MENU_SUB_SYSINFO_P2.
    if hat.is_button_pressed(hat.btn_left) == True:
        hat.img_framebuffer.paste(hat.invert_navi_asset_list[hat.ASSET_NAVI_LEFT], hat.POS_OLED_NAVI_LEFT)
    else:
        hat.img_framebuffer.paste(hat.navi_asset_list[hat.ASSET_NAVI_LEFT], hat.POS_OLED_NAVI_LEFT)

    if hat.is_button_pressed(hat.btn_right) == True:
        hat.img_framebuffer.paste(hat.invert_navi_asset_list[hat.ASSET_NAVI_RIGHT], hat.POS_OLED_NAVI_RIGHT)
    else:
        hat.img_framebuffer.paste(hat.navi_asset_list[hat.ASSET_NAVI_RIGHT], hat.POS_OLED_NAVI_RIGHT)
# END OF def task_oled_prepare_framebuffer()

def task_check_inputs(cups_hat: CUPS_Hat):
    """
    Non-blocking task that checks button inputs and updates current menu and other attributes
    """
    btn_left = cups_hat.btn_left
    btn_right = cups_hat.btn_right
    btn_enter = cups_hat.btn_enter
    cur_menu = cups_hat.current_menu

    # Check LEFT button
    if cups_hat.is_button_ev_det(btn_left):
        match cur_menu:
            # Cycle through main menu only if the current_menu value is within the MENU_MAIN_... range.
            case cur_menu if cur_menu in range(cups_hat.MENU_MAIN_REBOOT, cups_hat.MENU_MAIN_SYS_INFO + 1):
                if cur_menu == cups_hat.MENU_MAIN_REBOOT:
                    cur_menu = cups_hat.MENU_MAIN_SYS_INFO
                else:
                    cur_menu = cur_menu - 1
            
            # Cycle through System Info sub menu
            case cur_menu if cur_menu in range(cups_hat.MENU_SUB_SYSINFO_P1, cups_hat.MENU_SUB_SYSINFO_P2 + 1):
                if cur_menu == cups_hat.MENU_SUB_SYSINFO_P2:
                    cur_menu = cups_hat.MENU_SUB_SYSINFO_P1
                else:
                    pass
    else:
        pass

    # Check RIGHT button
    if cups_hat.is_button_ev_det(btn_right):
        match cur_menu:
            # Cycle through main menu only if the current_menu value is within the MENU_MAIN_... range.
            case cur_menu if cur_menu in range(cups_hat.MENU_MAIN_REBOOT, cups_hat.MENU_MAIN_SYS_INFO + 1):
                if cur_menu == cups_hat.MENU_MAIN_SYS_INFO:
                    cur_menu = cups_hat.MENU_MAIN_REBOOT
                else:
                    cur_menu = cur_menu + 1
            
            # Cycle through System Info sub menu
            case cur_menu if cur_menu in range(cups_hat.MENU_SUB_SYSINFO_P1, cups_hat.MENU_SUB_SYSINFO_P2 + 1):
                if cur_menu == cups_hat.MENU_SUB_SYSINFO_P1:
                    cur_menu = cups_hat.MENU_SUB_SYSINFO_P2
                else:
                    pass
    else:
        pass

    # Check ENTER button
    if cups_hat.is_button_ev_det(btn_enter):
        match cur_menu:
            case cups_hat.MENU_MAIN_SYS_INFO:
                cur_menu = cups_hat.MENU_SUB_SYSINFO_P1

            case cur_menu if cur_menu in range(cups_hat.MENU_SUB_SYSINFO_P1, cups_hat.MENU_SUB_SYSINFO_P2 + 1):
                cur_menu = cups_hat.MENU_MAIN_SYS_INFO

        # TODO: Figure out when to execute commands... on button press, or periodically (i.e., for System Info)?
        if cur_menu in range(cups_hat.MENU_MAIN_REBOOT, cups_hat.MENU_MAIN_SYS_INFO + 1):
                cups_hat.run_command()
    else:
        pass

    # Copy cur_menu value back to cups_hat.current_menu
    cups_hat.current_menu = cur_menu
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
        print("Test 2024-05-19 3.37pm: Starting display...")

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