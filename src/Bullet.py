import pygame

from src import Colors


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface([5, 5])
        self.image.fill(Colors.WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 10
        self.direction = direction

    def update(self):
        if self.direction == 'up':
            self.rect.y -= self.speed
        elif self.direction == 'down':
            self.rect.y += self.speed
        elif self.direction == 'left':
            self.rect.x -= self.speed
        elif self.direction == 'right':
            self.rect.x += self.speed

        if (self.rect.y < 0 or self.rect.y > Sizes.SCREEN_HEIGHT
                or self.rect.x < 0 or self.rect.x > Sizes.SCREEN_WIDTH):
            self.kill()