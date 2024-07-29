import pygame
import Colors


class PlayerTank(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([40, 40])
        self.image.fill(Colors.WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 5
        self.direction = 'up'

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            self.direction = 'left'
        elif keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            self.direction = 'right'
        elif keys[pygame.K_UP]:
            self.rect.y -= self.speed
            self.direction = 'up'
        elif keys[pygame.K_DOWN]:
            self.rect.y += self.speed
            self.direction = 'down'
