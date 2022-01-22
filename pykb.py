import pygame, sys
from pygame.locals import *

# TODO:
# enable numpad
# add more characters
# speak the characters
# add minimum display time

pygame.init()
display_info = pygame.display.Info()
#print(display_info)
display_width=display_info.current_w
display_height=display_info.current_h
vertical_margin=100
char_height=int(display_height-(vertical_margin*2))
horizontal_margin=int((display_width-char_height)/2)
screen = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption("pykb")
clock = pygame.time.Clock()
key_font = pygame.font.SysFont('arial',char_height)
BG = (0,0,0)
FG = (255,255,255)
allowed_keys = list(range(ord('a'),ord('z'))) + list(range(ord('0'),ord('9')))
num_pressed_keys = 0
while True:
    event = pygame.event.wait()
    if event.type == QUIT:
        pygame.quit()
        sys.exit()
    if event.type == KEYDOWN:
        #print(event)
        if event.key in allowed_keys:
            num_pressed_keys += 1
            if num_pressed_keys != 1:
                continue
            screen.fill(BG)
            key_display = key_font.render(chr(event.key).upper(), True, FG)
            screen.blit(key_display, (horizontal_margin,vertical_margin))
            pygame.display.update()
    if event.type == KEYUP:
        #print(event)
        if event.key in allowed_keys:
            num_pressed_keys -= 1
            if num_pressed_keys > 0:
                continue
            screen.fill(BG)
            pygame.display.update()
    clock.tick(60)
