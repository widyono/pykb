import pygame, sys
from pygame.locals import *
pygame.init()
display_info = pygame.display.Info()
screen = pygame.display.set_mode((display_info.current_w,display_info.current_h))
pygame.display.set_caption("pykb")
clock = pygame.time.Clock()
key_font = pygame.font.SysFont('arial',800)
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
            screen.blit(key_display, (500,100))
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
