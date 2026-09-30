import pygame
from pygame import mixer
import os
import random
import csv

mixer.init()
pygame.init()

#PANEL SETTINGS
PANEL_SPAN = 800
PANEL_TALLNESS = int(PANEL_SPAN * 0.8)
panel = pygame.display.set_mode((PANEL_SPAN, PANEL_TALLNESS))
pygame.display.set_caption('Pixel Shooter')

#REFRESH RATE
clock = pygame.time.Clock()
FPS = 60

# BACKGROUNDS
BACK_IMG = pygame.image.load('BACKGROUND/P1 PIC.png').convert_alpha()
BACK = pygame.transform.scale(BACK_IMG, (800, 640))

#HERO VARIABLES
gravity = 0.75
D_Left = False
D_Right = False

# COLOURS
CANVAS_COLOUR = (144, 201, 120)
RED = (200, 8, 21)
WHITE = (255, 255, 255)
GREEN = (0,110,51)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
PINKISH = (229, 37, 84)
DBLUE = (42, 46, 55)
GREY = (128, 128, 128)

def Draw_background():
    panel.fill(CANVAS_COLOUR)
    panel.blit(BACK, (0, 0))


class Trooper(pygame.sprite.Sprite):
    def __init__(self, character_variation: str, x: int, y: int, scale: float, velocity: int):
        pygame.sprite.Sprite.__init__(self)
        self.character_variation = character_variation
        self.dx_velocity = velocity
        self.course = 1
        self.dy_velocity = 0
        self.jump = False
        self.airborne = True
        self.turn = False 
        pic = pygame.image.load(f'P2 {character_variation}.png')
        self.image = pygame.transform.scale(pic, (int(pic.get_width() * scale), int(pic.get_height() * scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def move(self, D_Left, D_Right):
        #RESET MOVE VARIABLES
        change_x = 0
        change_y = 0

        #ASSIGN MOVEMENT VARIABLES
        if D_Left :
            change_x = -self.dx_velocity
            self.turn = True
            self.course = -1
        if D_Right : 
            change_x = self.dx_velocity
            self.turn = False
            self.course = 1

        #JUMP
        if self.jump == True and self.airborne == False:
            self.dy_velocity = -12
            self.jump = False
            self.airborne = True

        #APPLY GRAVITY
        self.dy_velocity += gravity
        if self.dy_velocity > 10:
            self.dy_velocity
        change_y += self.dy_velocity

        #SCREEN BOTTOM TEMP
        if self.rect.bottom + change_y > 500:
            change_y = 500 - self.rect.bottom
            self.airborne = False


        #Refresh RECTANGLE POSITION
        self.rect.x += change_x
        self.rect.y += change_y


    def draw(self):
        panel.blit(pygame.transform.flip(self.image, self.turn, False), self.rect)


HERO = Trooper('player', 200, 200, 0.25, 5)
OPPS = Trooper('enemy', 400, 200, 0.25, 5)


run = True

while run:
    
    clock.tick(FPS)

    Draw_background()

    HERO.draw()
    OPPS.draw()

    HERO.move(D_Left, D_Right)

    for event in  pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        #KEYBOARD PRESSES
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                D_Left = True
            if event.key == pygame.K_d:
                D_Right = True
            if event.key == pygame.K_w:
                HERO.jump = True
            if event.key == pygame.K_ESCAPE:
                run = False

        #KEYBOARD BUTTON RELEASED
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                D_Left = False
            if event.key == pygame.K_d:
                D_Right = False
            if event.key == pygame.K_w:
                HERO.jump = False

    pygame.display.update()

pygame.quit()