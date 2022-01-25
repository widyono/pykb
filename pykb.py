import pygame, sys
from pygame.locals import *
import os, string, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from collections import defaultdict

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

# font to use for default keycap images
font = ImageFont.truetype('Monaco.ttf', size=IMG_Y)

# wait this long after any acceptable keypress before continuing with event loop
#  to avoid bounces and spamming
DELAY_MS = 500
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
    media_options[keycap] = defaultdict(lambda: [None, None])

    # by default we create a PNG font image for each keycap
    keycap_repr = keycap.upper()
    keycap_mediadir = mediadir / f"{keycap}"
    keycap_font_imagefile = keycap_mediadir / f"{keycap}.png"
    os.makedirs(keycap_mediadir,exist_ok=True)
    if not os.path.exists(keycap_font_imagefile):
        image = Image.new('RGB', (IMG_X, IMG_Y))
        dl = ImageDraw.Draw(image)
        (width,height)=font.getsize(keycap_repr)
        xoff=int((IMG_X-width)/2)
        yoff=int((IMG_Y-height)/2)-50
        dl.text((xoff,yoff), keycap_repr, font=font, fill=FG)
        image.save(str(keycap_font_imagefile),"PNG")

    for (dirpath, dirnames, filenames) in os.walk(keycap_mediadir):
        for filename in filenames:
            extension=Path(filename).suffix
            basename=Path(filename).stem
            fullpath=str(keycap_mediadir / f"{filename}")
            if extension in EXT_IMG:
                media_index=MEDIA_IMG
            elif extension in EXT_SND:
                media_index=MEDIA_SND
            else:
                print(f"Unrecognized filename extension: {fullpath}")
            media_options[keycap][basename][media_index]=fullpath

    # if we have an image without an associated sound (basename is same), then
    #  assign the keycap's default / self-named sound file (ideally the keycap's label voiced aloud)
    if media_options[keycap][keycap][MEDIA_SND]:
        for basename in media_options[keycap]:
            if basename == keycap:
                continue
            if not media_options[keycap][basename][MEDIA_SND]:
                media_options[keycap][basename][MEDIA_SND] = media_options[keycap][keycap][MEDIA_SND]

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
                if active_keypress_time > 0 and (pygame.time.get_ticks() - active_keypress_time < (DELAY_MS + HYSTERESIS_MS)):
                    continue
                if event.key in numpad_keys:
                    event.key = numpad_to_number[event.key]
                active_key = event.key
                active_keypress_time = pygame.time.get_ticks()
                screen.fill(BG)
                keycap_random_basename = random.choice(list(media_options[chr(active_key)].keys()))
                keycap_media = media_options[chr(active_key)][keycap_random_basename]
                if keycap_media[MEDIA_IMG]:
                    screen.blit(pygame.image.load(keycap_media[MEDIA_IMG]), (horizontal_margin,vertical_margin))
                if keycap_media[MEDIA_SND]:
                    pygame.mixer.music.load(keycap_media[MEDIA_SND])
                    pygame.mixer.music.play(1)
                pygame.display.update()
                pygame.time.wait(DELAY_MS)

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
