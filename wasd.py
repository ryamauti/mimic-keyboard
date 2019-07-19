import keyboard
import time

def press_release(k):
    keyboard.press(k)
    time.sleep(0.5)
    keyboard.release(k)

while True:
    press_release('w')
    time.sleep(1)
    press_release('a')
    time.sleep(1)
    press_release('s')
    time.sleep(1)
    press_release('d')
    time.sleep(1)
