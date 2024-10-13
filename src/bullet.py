import pygame


class Bullet:
    def __init__(self, game, x, y, direction):
        self.game = game
        self.rect = pygame.Rect(x, y, 4, 4)
        self.direction = direction
        self.speed = 5

    def update(self):
        # Обновление положения пули
        pass

    def draw(self):
        # Отрисовка пули
        pass
