import pygame, sys
from pygame.locals import *

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

# font for keycap image display
key_font = pygame.font.SysFont('arial',keycap_height)

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
                key_display = key_font.render(chr(active_key).upper(), True, FG)
                screen.blit(key_display, (horizontal_margin,vertical_margin))
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
