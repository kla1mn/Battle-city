import pygame

TILE_SIZE = 16

class Castle:
    def __init__(self, game):
        self.game = game
        self.rect = pygame.Rect(12 * TILE_SIZE, 24 * TILE_SIZE, 32, 32)
        self.active = True

    def draw(self):
        # Отрисовка замка
        pass