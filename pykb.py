#!/usr/bin/env python3

import pygame, sys
from pygame.locals import *
import os, string, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ExifTags
from collections import defaultdict
import argparse
from pprint import pformat

# where to store/find our images and sounds
mediadir = Path.home() / "pykb-media"

# which keycaps to process
all_keycaps = string.ascii_lowercase + "0123456789"

# media file extensions
EXT_IMG = (".jpg",".png",".gif",".jpeg")
# note: for best results, sound files should have built-in silence at end to allow for measured looping
#  author has only had success with .ogg files, your mileage may vary
EXT_SND = (".wav", ".ogg", ".mp3")

media_options = {}
# indexes into media options list for each keycap dict value
MEDIA_IMG = 0
MEDIA_SND = 1

# define colours
BG = (0,0,0)
FG = (255,255,255)

# image size
IMG_X = 500
IMG_Y = 500

# wait this long (in milliseconds) after any acceptable keypress before continuing with event loop
#  to avoid bounces and spamming
DURATION_MS = 1500
HYSTERESIS_MS = 30

# FPS for display update rate, 60 for minimal responsiveness
FPS = 60

# which key values are accepted for feedback
numpad_keys = list(range(K_KP1,K_KP0 + 1))
alpha_keys = list(range(ord('a'),ord('z')+1))
number_keys = list(range(ord('0'),ord('9')+1))
allowed_keys = alpha_keys + number_keys + numpad_keys
numpad_to_number = {
        K_KP1:ord('1'),
        K_KP2:ord('2'),
        K_KP3:ord('3'),
        K_KP4:ord('4'),
        K_KP5:ord('5'),
        K_KP6:ord('6'),
        K_KP7:ord('7'),
        K_KP8:ord('8'),
        K_KP9:ord('9'),
        K_KP0:ord('0'),
}

# prevent key bounce, spamming
active_key = None
active_keypress_time = 0





parser = argparse.ArgumentParser(description="Keyboard Playground")
parser.add_argument("-C","--cache",action="store_true",default=False,help="Cache media in memory")
parser.add_argument("-f","--font",help=f"Specify font name")
parser.add_argument("-m","--mediadir",help=f"Alternate media directory (instead of {mediadir})")
parser.add_argument("-d","--duration",default=DURATION_MS,help=f"Minimum duration (in milliseconds) to display image")
parser.add_argument("-D","--debug",action="store_true",default=False,help="Debug")
args = parser.parse_args()

def dprint(*dprint_args,**dprint_kwargs):
    if args.debug:
        print(*dprint_args,**dprint_kwargs)

if args.mediadir:
    if os.path.isdir(args.mediadir):
        mediadir=Path(args.mediadir)
    else:
        print(f"{args.mediadir} is not a directory.")
        exit(1)

for EXIFTAG_ORIENTATION in ExifTags.TAGS.keys():
    if ExifTags.TAGS[EXIFTAG_ORIENTATION]=='Orientation':
        break

# font to use for default keycap images
font_preferences = ['Monaco.ttf', 'Keyboard.ttf']
if args.font:
    font_preferences.insert(0, args.font)
found_font = None
found_font_name = None
for try_font in font_preferences:
    try:
        found_font = ImageFont.truetype(try_font, size=IMG_Y)
        found_font_name = try_font
        break
    except OSError:
        continue
if not found_font:
    print(f"Could not find any of these fonts: {font_preferences}")
    exit(1)
dprint(f"Using font: {found_font_name}")

for keycap in all_keycaps:

    """
        media_options = {
            "keycap_name1": {
                "basename1":["image_filename1", "sound_filename1"], # None if no such file
                "basename2":["image_filename2", "sound_filename2"],
                ...
            }
        }
    """
    media_options[keycap] = defaultdict(lambda: [[], []])

    # by default we create a PNG font image for each keycap
    keycap_repr = keycap.upper()
    keycap_mediadir = mediadir / f"{keycap}"
    keycap_font_imagefile = keycap_mediadir / f"{keycap}.png"
    os.makedirs(keycap_mediadir,exist_ok=True)
    if not os.path.exists(keycap_font_imagefile):
        image = Image.new('RGB', (IMG_X, IMG_Y))
        dl = ImageDraw.Draw(image)
        (width,height)=found_font.getsize(keycap_repr)
        xoff=int((IMG_X-width)/2)
        yoff=int((IMG_Y-height)/2)-50
        dl.text((xoff,yoff), keycap_repr, font=found_font, fill=FG)
        image.save(str(keycap_font_imagefile),"PNG")

    for (dirpath, dirnames, filenames) in os.walk(keycap_mediadir):
        for filename in filenames:
            extension=Path(filename).suffix
            colonparts=Path(filename).stem.split(':')
            fullpath=str(keycap_mediadir / f"{filename}")
            if extension in EXT_IMG:
                media_options[keycap][colonparts[0]][MEDIA_IMG].append(fullpath)
            elif extension in EXT_SND:
                media_options[keycap][colonparts[0]][MEDIA_SND].append(fullpath)
            else:
                print(f"Unrecognized filename extension: {fullpath}")

    # if we have an image without an associated sound (basename is same), then
    #  assign the keycap's default / self-named sound file (ideally the keycap's label voiced aloud)
    if media_options[keycap][keycap][MEDIA_SND]:
        for basename in media_options[keycap]:
            if basename == keycap:
                continue
            if not media_options[keycap][basename][MEDIA_SND]:
                media_options[keycap][basename][MEDIA_SND] = media_options[keycap][keycap][MEDIA_SND]

dprint(f"media_options:\n{pformat(media_options)}")

pygame.init()
pygame.mixer.init()

# calculate sizes
display_info = pygame.display.Info()
display_width=display_info.current_w
display_height=display_info.current_h
vertical_margin=100
keycap_height=int(display_height-(vertical_margin*2))
horizontal_margin=int((display_width-keycap_height)/2)
screen = pygame.display.set_mode((display_width,display_height))

# window title
pygame.display.set_caption("pykb")

clock = pygame.time.Clock()

keycap_media = [None, None]
while True:

    events = pygame.event.get()

    for event in events:
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == KEYDOWN:
            if event.mod:
                continue
            if event.key in allowed_keys:
                # if this is a second (or greater) keypress then ignore
                if active_key:
                    continue
                if active_keypress_time > 0 and (pygame.time.get_ticks() - active_keypress_time < (args.duration + HYSTERESIS_MS)):
                    continue
                if event.key in numpad_keys:
                    event.key = numpad_to_number[event.key]
                active_key = event.key
                active_keypress_time = pygame.time.get_ticks()
                screen.fill(BG)
                keycap_random_basename = random.choice(list(media_options[chr(active_key)].keys()))
                keycap_media = media_options[chr(active_key)][keycap_random_basename]
                if len(keycap_media[MEDIA_IMG]):
                    keycap_image_filename = keycap_media[MEDIA_IMG][0]
                    exiftags = Image.open(keycap_image_filename).getexif()
                    keycap_image = pygame.image.load(keycap_image_filename)
                    if EXIFTAG_ORIENTATION in exiftags:
                        if exiftags[EXIFTAG_ORIENTATION] == 3:
                            keycap_image=pygame.transform.rotate(keycap_image, 180)
                        elif exiftags[EXIFTAG_ORIENTATION] == 6:
                            keycap_image=pygame.transform.rotate(keycap_image, 270)
                        elif exiftags[EXIFTAG_ORIENTATION] == 8:
                            keycap_image=pygame.transform.rotate(keycap_image, 90)

                    (img_x, img_y) = keycap_image.get_size()
                    img_max = max(img_x, img_y)
                    img_ratio_x = img_x / img_max
                    img_ratio_y = img_y / img_max
                    keycap_image = pygame.transform.scale(keycap_image, (int(IMG_X * img_ratio_x), int(IMG_Y * img_ratio_y)))
                    screen.blit(keycap_image, (horizontal_margin,vertical_margin))
                if len(keycap_media[MEDIA_SND]):
                    pygame.mixer.music.load(random.choice(keycap_media[MEDIA_SND]))
                    pygame.mixer.music.play(1)
                pygame.display.update()
                pygame.time.wait(args.duration)

        if event.type == KEYUP:
            if event.key in numpad_keys:
                event.key = numpad_to_number[event.key]
            if event.key != active_key:
                continue
            active_key = None
            screen.fill(BG)
            pygame.display.update()
            if keycap_media[MEDIA_SND]:
                pygame.mixer.music.stop()

    clock.tick(FPS)
