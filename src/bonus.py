import pygame

class Bonus:
    def __init__(self, game, x, y, type):
        self.game = game
        self.rect = pygame.Rect(x, y, 32, 32)
        self.type = type

    def update(self):
        # Обновление состояния бонуса
        pass

    def draw(self):
        # Отрисовка бонуса
        pass