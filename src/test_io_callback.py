import RPi.GPIO as io       # Used to setup IO on the Pi Zero 2

i = 0

"""
Main references:
https://sourceforge.net/p/raspberry-gpio-python/wiki/Inputs/
https://tieske.github.io/rpi-gpio/modules/GPIO.html
"""

def test_callback(channel):
    global i
    i = i + 1
    print(i)

def main():
    """ Main application """
    io.setmode(io.BCM)
    btn_left = 5 #GPIO5
    btn_enter = 6 #GPIO6
    btn_right = 26 #GPIO26

    # Reference for init code is from link below
    # https://raspberrypihq.com/use-a-push-button-with-raspberry-pi-gpio/
    io.setup(btn_left, io.IN, pull_up_down=io.PUD_UP)
    io.setup(btn_enter, io.IN, pull_up_down=io.PUD_UP)
    io.setup(btn_right, io.IN, pull_up_down=io.PUD_UP)

    # Handle error to ensure we get event detection
    while True:
        try:
            io.add_event_detect(btn_left, io.FALLING, callback=test_callback, bouncetime=300)
        except:
            print(Exception)
        else:
            break
    io.add_event_detect(btn_enter, io.FALLING, bouncetime=300)
    io.add_event_detect(btn_right, io.RISING, bouncetime=300)

    print("はじめ！")

    while True:
        if io.event_detected(btn_enter):
            print("ENTER!")
        if io.event_detected(btn_right):
            print("RIGHT!")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nEnding demo.....")