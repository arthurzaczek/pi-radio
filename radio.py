#!/usr/bin/python3

import os,signal,random,re,json
from os import walk
from time import sleep
import subprocess

def handler(signum, frame):
    print ("Got a {} signal. Doing nothing".format(signum))

signal.signal(signal.SIGHUP, handler)


# ----------------- Init constants
music_folder = "/mnt/music/"

# ----------------- Init globals
cards = []

def load_music():
    global cards
    
    cards = json.load(open(music_folder + "cards.json"))
    print ("Found {} cards".format(len(cards)))

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
        subprocess.call(["mpc", "add", cards[tag_id]['file']])
    if ('folder' in cards[tag_id]):
        print ("playing folder {}".format(cards[tag_id]['folder']))
        subprocess.call(["mpc",  "add", cards[tag_id]['folder']])
    if ('radio' in cards[tag_id]):
        print ("playing radio {}".format(cards[tag_id]['radio']))
        subprocess.call(["mpc", "load", cards[tag_id]['radio']])

    play_music()

def stop_music():
    subprocess.call( "mpc stop", shell=True)

def play_music_next():
    subprocess.call( "mpc next", shell=True)

def play_music_prev():
    subprocess.call( "mpc prev", shell=True)

def main():

    load_music()

    tagpipe = open('/tmp/rfidpipe', 'r')

    print("Running radio")
    
    # -------- Main Program Loop -----------
    #Loop until the user clicks the close button.
    done = False
    tag_id = ""
    while done==False:
        try:
            tag_id = tagpipe.readline()
        except OSError as err:
            print ("Error reading pipe: {}".format(err.errno))
        
        if len(tag_id) != 0:
            tag_id = tag_id.strip()
            print ("Tag: ", tag_id)
            play_music_card(tag_id)

        # Limit to 20 frames per second
        sleep(20)

    os.close(tagpipe)

if __name__ == '__main__':
    main()
