#!/usr/bin/python3

import pygame,os,signal,random,re,json
import RPi.GPIO as GPIO
from os import walk
from time import sleep

def handler(signum, frame):
    print ("Got a {} signal. Doing nothing".format(signum))

signal.signal(signal.SIGHUP, handler)

pygame.init()
os.putenv('SDL_VIDEODRIVER', 'dummy')
pygame.display.init()
screen = pygame.display.set_mode((1,1))

tag_id = ""
tagpipe = os.open('/tmp/rfidpipe', os.O_RDONLY | os.O_NONBLOCK)

SONG_END = pygame.USEREVENT + 1
pygame.mixer.music.set_endevent(SONG_END)

pygame.mixer.init()

current_music_idx = 0
now_playing = -1
music_counter = 0
music = [os.path.join(r,file) for r,d,f in os.walk("/mnt/music") for file in f]
random.shuffle(music)
print ("Found {} music file".format(len(music)))
playlist = music

cards = json.load(open('/mnt/music/cards.json'))
print ("Found {} cards".format(len(cards)))

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

############# GPIO Init

GPIO.setmode(GPIO.BOARD)
GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def button_event(channel):
    # print("channel: {}".format(channel))
    if GPIO.input(8) == False:
        print("Stop")
    if GPIO.input(10) == False:
        print("Play")
    if GPIO.input(12) == False:
        print("Next")
    if GPIO.input(16) == False:
        print("Prev")

    if GPIO.input(18) == False:
        print("Louder")
    if GPIO.input(24) == False:
        print("Quieter")

    if channel == 22:
        if GPIO.input(22) == True:
            print("Off")
        if GPIO.input(22) == False:
            print("On")

GPIO.add_event_detect(8, GPIO.RISING, callback=button_event, bouncetime=50)
GPIO.add_event_detect(10, GPIO.RISING, callback=button_event, bouncetime=50)
GPIO.add_event_detect(12, GPIO.RISING, callback=button_event, bouncetime=50)
GPIO.add_event_detect(16, GPIO.RISING, callback=button_event, bouncetime=50)

GPIO.add_event_detect(18, GPIO.RISING, callback=button_event, bouncetime=50)
GPIO.add_event_detect(22, GPIO.RISING, callback=button_event, bouncetime=50)

GPIO.add_event_detect(24, GPIO.RISING, callback=button_event, bouncetime=50)

# you can continue doing other stuff here
while True:
    pass
