#!/usr/bin/python3

import os,signal,random,re,json
import RPi.GPIO as GPIO
from os import walk
from time import sleep
import subprocess

def handler(signum, frame):
    print ("Got a {} signal. Doing nothing".format(signum))

signal.signal(signal.SIGHUP, handler)


# ----------------- Init constants
# music_folder = "/var/music/"
music_folder = "/mnt/music/"

# ----------------- Init globals
cards = []

def load_music():
    global cards
    
    cards = json.load(open(music_folder + "cards.json"))
    print ("Found {} cards".format(len(cards)))

# ----------------- GPIO Init
def init_gpio():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(8, GPIO.RISING, callback=button_event, bouncetime=50)
    GPIO.add_event_detect(10, GPIO.RISING, callback=button_event, bouncetime=50)
    GPIO.add_event_detect(12, GPIO.RISING, callback=button_event, bouncetime=50)
    GPIO.add_event_detect(16, GPIO.RISING, callback=button_event, bouncetime=50)

    GPIO.add_event_detect(18, GPIO.RISING, callback=button_event, bouncetime=50)
    GPIO.add_event_detect(22, GPIO.RISING, callback=button_event, bouncetime=50)

    GPIO.add_event_detect(24, GPIO.RISING, callback=button_event, bouncetime=50)


# ----------------- music functions
def play_music():
    subprocess.call( "mpc play", shell=True)

def play_music_card(tag_id):
    global cards
    if (tag_id not in cards):       
        return

    subprocess.call( "mpc clear", shell=True)

    if ('file' in cards[tag_id]):
        print ("playing file {}".format(cards[tag_id]['folder']))
        subprocess.call("mpc add \"{}\"".format(cards[tag_id]['file']), shell=True)
    if ('folder' in cards[tag_id]):
        print ("playing folder {}".format(cards[tag_id]['folder']))
        subprocess.call("mpc add \"{}\"".format(cards[tag_id]['folder']), shell=True)
    if ('radio' in cards[tag_id]):
        print ("playing radio {}".format(cards[tag_id]['radio']))
        subprocess.call("mpc load \"{}\"".format(cards[tag_id]['radio']), shell=True)

    play_music()

def stop_music():
    subprocess.call( "mpc stop", shell=True)

def play_music_next():
    subprocess.call( "mpc next", shell=True)

def play_music_prev():
    subprocess.call( "mpc prev", shell=True)

def button_event(channel):
    global volume
    # print("channel: {}".format(channel))
    if GPIO.input(8) == False:
        print("Stop")
        stop_music()

    if GPIO.input(10) == False:
        print("Play")
        play_music()

    if GPIO.input(12) == False:
        print("Next")
        play_music_next()

    if GPIO.input(16) == False:
        print("Prev")
        play_music_prev()

    if GPIO.input(18) == False:
        print("Louder")
        subprocess.call( "mpc volume +5", shell=True)

    if GPIO.input(24) == False:
        print("Quieter")
        subprocess.call( "mpc volume -5", shell=True)

    if channel == 22:
        if GPIO.input(22) == True:
            print("Off")
            stop_music()
        if GPIO.input(22) == False:
            print("On")

def main():

    load_music()
    init_gpio()

    tagpipe = os.open('/tmp/rfidpipe', os.O_RDONLY | os.O_NONBLOCK)

    print("Running radio")
    
    # -------- Main Program Loop -----------
    #Loop until the user clicks the close button.
    done = False
    tag_id = ""
    while done==False:
        try:
            tag_id = os.read(tagpipe, 1024)
        except OSError as err:
            print ("Error reading pipe: {}".format(err.errno))
        
        if len(tag_id) != 0:
            tag_id = tag_id.decode().strip()
            print ("Tag: ", tag_id)
            play_music_card(tag_id)

        sleep(.020)

    os.close(tagpipe)

if __name__ == '__main__':
    main()
