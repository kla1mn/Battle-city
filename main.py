import pygame
import random
import PlayerTank
import EnemyTank
import Colors
import Sizes

pygame.init()


screen = pygame.display.set_mode((Sizes.SCREEN_WIDTH, Sizes.SCREEN_HEIGHT))
pygame.display.set_caption("Battle City")
# TODO pygame.display.set_icon()


clock = pygame.time.Clock()
FPS = 60


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


def main():
    player = PlayerTank.PlayerTank(Sizes.SCREEN_WIDTH // 2, Sizes.SCREEN_HEIGHT - 50)
    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()

    all_sprites.add(player)

    for _ in range(5):
        enemy = EnemyTank.EnemyTank(random.randint(0, Sizes.SCREEN_WIDTH - 40), random.randint(-300, -40))
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

        screen.fill(Colors.BLACK)
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
