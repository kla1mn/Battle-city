import pygame
import random

# Инициализация Pygame
pygame.init()

# Настройки экрана
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Battle City")

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Частота кадров
clock = pygame.time.Clock()
FPS = 60


class PlayerTank(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([40, 40])
        self.image.fill(WHITE)
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
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            self.direction = 'right'
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
            self.direction = 'up'
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed
            self.direction = 'down'


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface([5, 5])
        self.image.fill(WHITE)
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

        if self.rect.y < 0 or self.rect.y > screen_height or self.rect.x < 0 or self.rect.x > screen_width:
            self.kill()


class EnemyTank(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([40, 40])
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.y > screen_height:
            self.rect.y = -40
            self.rect.x = random.randint(0, screen_width - 40)


def main():
    player = PlayerTank(screen_width // 2, screen_height - 50)
    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()

    all_sprites.add(player)

    for _ in range(5):
        enemy = EnemyTank(random.randint(0, screen_width - 40), random.randint(-300, -40))
        all_sprites.add(enemy)
        enemies.add(enemy)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullet = Bullet(player.rect.centerx, player.rect.centery, player.direction)
                    all_sprites.add(bullet)
                    bullets.add(bullet)

        all_sprites.update()

        for bullet in bullets:
            enemy_hit_list = pygame.sprite.spritecollide(bullet, enemies, True)
            for enemy in enemy_hit_list:
                bullets.remove(bullet)
                all_sprites.remove(bullet)

        screen.fill(BLACK)
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
