import pygame
import random
import Colors
import Sizes


class EnemyTank(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([40, 40])
        self.image.fill(Colors.WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.y > Sizes.SCREEN_HEIGHT:
            self.rect.y = -40
            self.rect.x = random.randint(0, Sizes.SCREEN_WIDTH - 40)