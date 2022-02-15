#!/usr/bin/env python3

import pygame, sys
from pygame.locals import *
import os, string, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ExifTags
from collections import defaultdict
import argparse
from pprint import pformat

"""
Example media structure
~/pykb-media/a/
  a.png            # picture of the letter A
  a.ogg            # sound naming the letter A
  apple.png        # picture of an apple
  apple.ogg        # sound of the word apple
  airplane:1.png   # picture of an airplane
  airplane:2.png   # picture of a different airplane
  airplane:1.ogg   # sound of the word airplane
  airplane:2.ogg   # sound of the word airplane, in another language
  airplane:3.ogg   # sound of an airplane in flight
"""

# where to store/find our images and sounds
mediadir = Path.home() / "pykb-media"

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

# which keys to process
allowed_keys = {k:k for k in string.ascii_lowercase + string.digits}
allowed_keys.update({
    '[':'leftbracket',
    ']':'rightbracket',
    ';':'semicolon',
    ',':'comma',
    '.':'period',
    '/':'forwardslash',
    '`':'backtick',
    '-':'minus',
    '+':'plus',
    '*':'star',
    '=':'equals',
    '\'':'singlequote',
    '\r':'return',
    '\\':'backslash',
    '\x08':'delete',
    ' ':'spacebar'})

# prevent key bounce, spamming
active_key = None
active_keypress_time = 0





parser = argparse.ArgumentParser(description="Keyboard Playground")
parser.add_argument("-C","--cache",action="store_true",default=False,help="Cache media in memory")
parser.add_argument("-f","--font",help=f"Specify font name")
parser.add_argument("-m","--mediadir",help=f"Alternate media directory (instead of {mediadir})")
parser.add_argument("-d","--duration",default=DURATION_MS,help=f"Minimum duration (in milliseconds) to display image")
parser.add_argument("-D","--debug",action="store_true",default=False,help="Debug")
parser.add_argument("-T","--testing",action="store_true",default=False,help="Testing mode")
args = parser.parse_args()

if args.testing:
    args.debug = True

def dprint(*dprint_args,**dprint_kwargs):
    if args.debug:
        print(*dprint_args,**dprint_kwargs)

if not args.testing:
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

    def load_image(pathname):
        exiftags = Image.open(pathname).getexif()
        image = pygame.image.load(pathname)
        if EXIFTAG_ORIENTATION in exiftags:
            if exiftags[EXIFTAG_ORIENTATION] == 3:
                image=pygame.transform.rotate(image, 180)
            elif exiftags[EXIFTAG_ORIENTATION] == 6:
                image=pygame.transform.rotate(image, 270)
            elif exiftags[EXIFTAG_ORIENTATION] == 8:
                image=pygame.transform.rotate(image, 90)
        (img_x, img_y) = image.get_size()
        img_max = max(img_x, img_y)
        img_ratio_x = img_x / img_max
        img_ratio_y = img_y / img_max
        image = pygame.transform.scale(image, (int(IMG_X * img_ratio_x), int(IMG_Y * img_ratio_y)))
        dprint(f"Loaded image {pathname}: {img_x} x {img_y}")
        return image

    for keycap, keycap_filename in allowed_keys.items():

        """
            media_options = {
                "keycap_name1": {
                    "basename1":[["image_filename1"], ["sound_filename1"]], # None if no such file
                    "basename2":[["image_filename2"], ["sound_filename2_1", "sound_filename2_2"]],
                    ...
                }
            }
        """
        media_options[keycap] = defaultdict(lambda: [[], []])

        # by default we create a PNG font image for each keycap
        keycap_repr = keycap.upper()
        keycap_mediadir = mediadir / f"{keycap_filename}"
        keycap_font_imagefile = keycap_mediadir / f"{keycap_filename}.png"
        os.makedirs(keycap_mediadir,exist_ok=True)
        if not os.path.exists(keycap_font_imagefile):
            dprint(f"Creating new keycap image file {keycap_font_imagefile}")
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
                    if args.cache:
                        media_options[keycap][colonparts[0]][MEDIA_IMG].append(load_image(fullpath))
                    else:
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
clock = pygame.time.Clock()


if not args.testing:
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

    keycap_media = [None, None]



###
# Main Event Loop
###

while True:

    events = pygame.event.get()

    for event in events:
        if event.type == QUIT:
            if not args.testing:
                pygame.quit()
            sys.exit()

        if event.type == KEYDOWN:
            dprint(f"KEYDOWN: {event}")
            # ignore if just a modifier key by itself was pressed
            if event.mod and not event.unicode:
                continue
            # pygame processes individual key events before triggering QUIT meta-event
            if event.mod & pygame.KMOD_META and event.unicode == 'q':
                if not args.testing:
                    pygame.quit()
                sys.exit()
            # if caps lock is released, unicode is empty and mod is false
            if event.unicode and event.unicode.lower() in allowed_keys:
                # if this is a second (or greater) keypress then ignore
                if active_key:
                    continue
                if active_keypress_time > 0 and (pygame.time.get_ticks() - active_keypress_time < (args.duration + HYSTERESIS_MS)):
                    continue
                active_key = event.unicode.lower()
                dprint(f"ACCEPTED: {active_key}")
                if not args.testing:
                    active_keypress_time = pygame.time.get_ticks()
                    screen.fill(BG)
                    keycap_random_basename = random.choice(list(media_options[active_key].keys()))
                    keycap_media = media_options[active_key][keycap_random_basename]
                    if len(keycap_media[MEDIA_IMG]):
                        keycap_image = random.choice(keycap_media[MEDIA_IMG])
                        if not args.cache:
                            keycap_image = load_image(keycap_image)
                        screen.blit(keycap_image, (horizontal_margin,vertical_margin))
                    if len(keycap_media[MEDIA_SND]):
                        pygame.mixer.music.load(random.choice(keycap_media[MEDIA_SND]))
                        pygame.mixer.music.play(1)
                    pygame.display.update()
                    pygame.time.wait(args.duration)

        if event.type == KEYUP:
            dprint(f"KEYUP: {event}")
            if event.unicode.lower() != active_key:
                continue
            active_key = None
            if not args.testing:
                screen.fill(BG)
                pygame.display.update()
                if keycap_media[MEDIA_SND]:
                    pygame.mixer.music.stop()

    clock.tick(FPS)
