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

GPIO.add_event_detect(8, GPIO.RISING, callback=button_event, bouncetime=50)
GPIO.add_event_detect(10, GPIO.RISING, callback=button_event, bouncetime=50)
GPIO.add_event_detect(12, GPIO.RISING, callback=button_event, bouncetime=50)
GPIO.add_event_detect(16, GPIO.RISING, callback=button_event, bouncetime=50)

GPIO.add_event_detect(18, GPIO.RISING, callback=button_event, bouncetime=50)
GPIO.add_event_detect(22, GPIO.RISING, callback=button_event, bouncetime=50)

GPIO.add_event_detect(24, GPIO.RISING, callback=button_event, bouncetime=50)

# ----------------- main functions

def play_music():
    global now_playing
    global music_counter
    try:
        pygame.mixer.music.load(playlist[current_music_idx])
        pygame.mixer.music.play()
        now_playing = current_music_idx
    except Exception as inst:
        print(inst)

def play_music_card():
    global playlist
    global cards
    global current_music_idx
    if (tag_id not in cards): 
        return
    if ('file' in cards[tag_id]):
        playlist = [ cards[tag_id]['file'] ]
    if ('folder' in cards[tag_id]):
        print ("playing folder {}".format(cards[tag_id]['folder']))
        playlist = [os.path.join(r,file) for r,d,f in os.walk(cards[tag_id]['folder']) for file in f]
        playlist.sort()
        current_music_idx = 0
    play_music()

def stop_music():
    global now_playing
    pygame.mixer.music.stop()
    now_playing = -1

def play_music_next():
    global now_playing
    global current_music_idx
    global music_counter
    try:
        current_music_idx += 1
        current_music_idx = current_music_idx % len(playlist)
        pygame.mixer.music.load(playlist[current_music_idx])
        pygame.mixer.music.play()
        now_playing = current_music_idx
    except:
        play_music_next()

def play_music_prev():
    global now_playing
    global current_music_idx
    global music_counter
    try:
        current_music_idx -= 1
        if (current_music_idx < 0):
            current_music_idx = len(playlist) - 1
        pygame.mixer.music.load(playlist[current_music_idx])
        pygame.mixer.music.play()
        now_playing = current_music_idx
    except:
        print("Error prev")

def button_event(channel):
    # print("channel: {}".format(channel))
    if GPIO.input(8) == False:
        print("Stop")
        if (now_playing != -1):
            stop_music()

    if GPIO.input(10) == False:
        print("Play")
        if (now_playing == -1):
            music_counter = 0
            playlist = music
            play_music()

    if GPIO.input(12) == False:
        print("Next")
        music_counter = 0
        play_music_next()

    if GPIO.input(16) == False:
        print("Prev")
        music_counter = 0
        play_music_prev()

    if GPIO.input(18) == False:
        print("Louder")
    if GPIO.input(24) == False:
        print("Quieter")

    if channel == 22:
        if GPIO.input(22) == True:
            print("Off")
            stop_music()
        if GPIO.input(22) == False:
            print("On")


# -------- Main Program Loop -----------
#Loop until the user clicks the close button.
done = False
while done==False:
    try:
        tag_id = os.read(tagpipe, 1024)
    except OSError as err:
        print ("Error reading pipe: {}".format(err.errno))
    if len(tag_id) != 0:
        tag_id = tag_id.decode().strip()
        print ("Tag: ", tag_id)
        play_music_card()
    # Limit to 20 frames per second
    clock.tick(20)


os.close(tagpipe)
# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit ()
