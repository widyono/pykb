import pygame, sys
from pygame.locals import *
import os, string, random
from PIL import Image, ImageDraw, ImageFont

image_options = {}

font = ImageFont.truetype('Monaco.ttf', size=500)
all_chars = string.ascii_lowercase + "0123456789"
for ch in all_chars:
    char = ch.upper()
    imagedir = f"images/{ch}/"
    imagefile = imagedir + f"{ch}.png"
    os.makedirs(imagedir,exist_ok=True)
    image = Image.new('RGB', (500, 500))
    dl = ImageDraw.Draw(image)
    (width,height)=font.getsize(char)
    xoff=int((500-width)/2)
    yoff=int((500-height)/2)
    dl.text((xoff,yoff-50), char, font=font, fill=(255,255,255))
    image.save(imagefile,"PNG")
    image_options[ch] = []
    for (dirpath, dirnames, filenames) in os.walk(imagedir):
        for filename in filenames:
            image_options[ch].append(f"images/{ch}/{filename}")

pygame.init()

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

# define colours
BG = (0,0,0)
FG = (255,255,255)

# wait this long after any acceptable keypress before continuing with event loop
# to avoid bounces and spamming
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

while True:

    events = pygame.event.get()

    for event in events:
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == KEYDOWN:
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
                key_image = pygame.image.load(random.choice(image_options[chr(active_key)]))
                screen.blit(key_image, (horizontal_margin,vertical_margin))
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

    clock.tick(FPS)
