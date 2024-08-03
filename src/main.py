import pygame
import src.Tank

"""pygame.init()

pygame.display.set_caption("Battle City")
size = width, height = 480, 416
screen = pygame.display.set_mode(size)"""


pygame.init()
pygame.display.set_caption('hello')

background = pygame.image.load('img/background.png')
person = pygame.image.load('img/person.png')

display_w = 500
display_h = 500

loc_x = 100
loc_y = 100

game_exit = False

clock = pygame.time.Clock()

game_display = pygame.display.set_mode((display_w, display_h))
game_display.blit(background, (0, 0))
game_display.blit(person, (loc_x, loc_y))

class Inventory:
    key = False

def game_loop(update_time):
    global game_exit
    while not game_exit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_exit = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    loc_y += 25
                if event.key == pygame.K_s:
                    loc_y -= 25
                if event.key == pygame.K_a:
                    loc_x -= 25
                if event.key == pygame.K_d:
                    loc_x += 25
    game_display.blit(background, (0, 0))
    game_display.blit(person, (loc_x, loc_y))

game_loop(30)
pygame.quit()