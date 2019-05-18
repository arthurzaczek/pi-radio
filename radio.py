#!/usr/bin/python3

import pygame,os,signal,random,re,json
import RPi.GPIO as GPIO
import vlc
import time
from os import walk
from time import sleep

def handler(signum, frame):
    print ("Got a {} signal. Doing nothing".format(signum))

signal.signal(signal.SIGHUP, handler)


# ----------------- Init constants
music_folder = "/mnt/music/"

# ----------------- Init globals
SONG_END = pygame.USEREVENT + 1

current_music_idx = 0
now_playing = -1

music = []
playlist = []
cards = []
volume = 0.8

# ----------------- Init vlc
vlc_instance = vlc.Instance('--input-repeat=-1', '--fullscreen', '-A', 'alsa,none', '--alsa-audio-device', 'default')
vlc_player=vlc_instance.media_player_new()

def load_music():
    global music
    global playlist
    global cards
    
    music = [os.path.join(r,file) for r,d,f in os.walk(music_folder) for file in f]
    random.shuffle(music)
    print ("Found {} music file".format(len(music)))
    playlist = music

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
    global now_playing
    global vlc_player
    try:
        print ("Playing {} songs".format(len(playlist)))
        vlc_player.stop()
        pygame.mixer.music.load(playlist[current_music_idx])
        pygame.mixer.music.play()
        now_playing = current_music_idx
    except Exception as inst:
        print(inst)

def play_music_card(tag_id):
    global playlist
    global cards
    global current_music_idx
    global vlc_player
    global vlc_instance

    vlc_player.stop()

    if (tag_id not in cards):       
        return
    if ('file' in cards[tag_id]):
        playlist = [ music_folder + cards[tag_id]['file'] ]
        current_music_idx = 0
    if ('folder' in cards[tag_id]):
        print ("playing folder {}".format(music_folder + cards[tag_id]['folder']))
        playlist = [os.path.join(r,file) for r,d,f in os.walk(music_folder + cards[tag_id]['folder']) for file in f]
        playlist.sort()
        current_music_idx = 0
    if ('radio' in cards[tag_id]):
        print ("playing radio {}".format(cards[tag_id]['radio']))
        playlist = [ ]
        current_music_idx = 0
        url = cards[tag_id]['radio']
        media=vlc_instance.media_new(url)
        vlc_player.set_media(media)
        vlc_player.play()
        return

    play_music()

def stop_music():
    global now_playing
    global vlc_player
    if (now_playing != -1):
        pygame.mixer.music.stop()
        now_playing = -1
    vlc_player.stop()

def play_music_next():
    global now_playing
    global current_music_idx
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
    global volume
    global playlist
    # print("channel: {}".format(channel))
    if GPIO.input(8) == False:
        print("Stop")
        stop_music()

    if GPIO.input(10) == False:
        print("Play")
        if (now_playing == -1):
            playlist = music
            play_music()

    if GPIO.input(12) == False:
        print("Next")
        play_music_next()

    if GPIO.input(16) == False:
        print("Prev")
        play_music_prev()

    if GPIO.input(18) == False:
        print("Louder")
        volume += 0.1
        if(volume > 1.0):
            volume = 1
        pygame.mixer.music.set_volume(volume)

    if GPIO.input(24) == False:
        print("Quieter")
        volume -= 0.1
        if(volume < 0): 
            volume = 0
        pygame.mixer.music.set_volume(volume)

    if channel == 22:
        if GPIO.input(22) == True:
            print("Off")
            stop_music()
        if GPIO.input(22) == False:
            print("On")

def main():
    pygame.init()
    os.putenv('SDL_VIDEODRIVER', 'dummy')
    pygame.display.init()
    screen = pygame.display.set_mode((1,1))
    
    pygame.mixer.music.set_endevent(SONG_END)
    pygame.mixer.init()
    pygame.mixer.music.set_volume(volume)

    load_music()
    init_gpio()

    clock = pygame.time.Clock()
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
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # If user clicked close
                done=True # Flag that we are done so we exit this loop
            if event.type == SONG_END:
                play_music_next()
            
        # Limit to 20 frames per second
        clock.tick(20)

    os.close(tagpipe)
    pygame.quit ()

if __name__ == '__main__':
    main()
