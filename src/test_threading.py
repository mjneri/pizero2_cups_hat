import threading
import time

# Global var
isThreadExit = False

def timer1():
    while True:
        print("ONE")
        time.sleep(1)

        if isThreadExit is True:
            print("Timer1 Closed")
            break

def timer2():
    while not isThreadExit:
        print("TWO")
        time.sleep(2)
    
    print("Timer2 Closed")

# Reference -https://www.geeksforgeeks.org/multithreading-python-set-1/
if __name__ == '__main__':
    t1 = threading.Thread(target=timer1, args=())
    t2 = threading.Thread(target=timer2, args=())
 
    t1.start()
    t2.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        isThreadExit = True
        t1.join()
        t2.join()
        print("DONE")