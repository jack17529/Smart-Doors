# buttonInput.py
import RPi.GPIO as GPIO
import os
import time
from time import sleep

GPIO.setmode(GPIO.BCM)

sleepTime = 0.1

# GPIO Pin of the component
lightPin = 4
buttonPin = 17

GPIO.setup(lightPin, GPIO.OUT)
GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.output(lightPin, False)

pressed = 0

try:
    while True:
        b = GPIO.input(buttonPin)
        if b == 0:
            # print(b)
            pressed = pressed + 1
            if pressed == 1:
                GPIO.output(lightPin, not b)
                sleep(0.1)
                GPIO.output(lightPin, False)
                os.system("python TheDoor.py")
                print("runcomplete")
                # GPIO.output(lightPin,False)
                time.sleep(5)
                print("slept for 5 secs")
                # pressed = 0
                # continue
            pressed = 0
        GPIO.output(lightPin, not b)
        sleep(0.1)

except KeyboardInterrupt:
    print("interrupted!")

finally:

    # button.py:15: RuntimeWarning: This channel is already in use, continuing anyway.
    # Use GPIO.setwarnings(False) to disable warnings.
    # GPIO.setup(lightPin,GPIO.OUT)

    GPIO.output(lightPin, False)
    GPIO.cleanup()
