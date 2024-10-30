import pygame

from src.explosion import Explosion

from src.constants import Direction, GameSide, BulletState, TankState


class Bullet:
    def __init__(self, game, level, position, direction, damage=100, speed=5):
        self.game = game
        self.explosion = None

        self.level = level
        self.direction = direction
        self.damage = damage
        self.owner = None
        self.owner_class = None

        # 1-regular everyday normal bullet
        # 2-can destroy steel
        self.power = 1

        self.image = self.game.sprites.subsurface(75 * 2, 74 * 2, 3 * 2, 4 * 2)

        # position is player's top left corner, so we'll need to
        # recalculate a bit. also rotate image itself.
        if direction == Direction.Up:
            self.rect = pygame.Rect(position[0] + 11, position[1] - 8, 6, 8)
        elif direction == Direction.Right:
            self.image = pygame.transform.rotate(self.image, 270)
            self.rect = pygame.Rect(position[0] + 26, position[1] + 11, 8, 6)
        elif direction == Direction.Down:
            self.image = pygame.transform.rotate(self.image, 180)
            self.rect = pygame.Rect(position[0] + 11, position[1] + 26, 6, 8)
        elif direction == Direction.Left:
            self.image = pygame.transform.rotate(self.image, 90)
            self.rect = pygame.Rect(position[0] - 8, position[1] + 11, 8, 6)

        self.explosion_images = [self.game.sprites.subsurface(0, 80 * 2, 32 * 2, 32 * 2),
                                 self.game.sprites.subsurface(32 * 2, 80 * 2, 32 * 2, 32 * 2)]

        self.speed = speed
        self.state = BulletState.Active

    def draw(self):
        if self.state == BulletState.Active:
            self.game.screen.blit(self.image, self.rect.topleft)
        elif self.state == BulletState.Exploding:
            self.explosion.draw()

    def update(self):
        if self.state == BulletState.Exploding:
            if not self.explosion.active:
                self.destroy()
                del self.explosion

        if self.state != BulletState.Active:
            return

        """ move bullet """
        if self.direction == Direction.Up:
            self.rect.topleft = [self.rect.left, self.rect.top - self.speed]
            if self.rect.top < 0:
                if self.game.play_sounds and self.owner == GameSide.Player:
                    self.game.sounds["steel"].play()
                self.explode()
                return
        elif self.direction == Direction.Right:
            self.rect.topleft = [self.rect.left + self.speed, self.rect.top]
            if self.rect.left > (416 - self.rect.width):
                if self.game.play_sounds and self.owner == GameSide.Player:
                    self.game.sounds["steel"].play()
                self.explode()
                return
        elif self.direction == Direction.Down:
            self.rect.topleft = [self.rect.left, self.rect.top + self.speed]
            if self.rect.top > (416 - self.rect.height):
                if self.game.play_sounds and self.owner == GameSide.Player:
                    self.game.sounds["steel"].play()
                self.explode()
                return
        elif self.direction == Direction.Left:
            self.rect.topleft = [self.rect.left - self.speed, self.rect.top]
            if self.rect.left < 0:
                if self.game.play_sounds and self.owner == GameSide.Player:
                    self.game.sounds["steel"].play()
                self.explode()
                return

        has_collided = False

        # check for collisions with walls. one bullet can destroy several (1 or 2)
        # tiles but explosion remains 1
        rects = self.level.obstacle_rects
        collisions = self.rect.collidelistall(rects)
        if collisions:
            for i in collisions:
                if self.level.hit_tile(rects[i].topleft, self.power, self.owner == GameSide.Player):
                    has_collided = True
        if has_collided:
            self.explode()
            return

        # check for collisions with other bullets
        for bullet in self.game.bullets:
            if self.state == BulletState.Active and bullet.owner != self.owner and bullet != self and self.rect.colliderect(
                    bullet.rect):
                self.destroy()
                self.explode()
                return

        # check for collisions with players
        for player in self.game.players:
            if player.state == TankState.Alive and self.rect.colliderect(player.rect):
                if player.bulletImpact(self.owner == GameSide.Player, self.damage, self.owner_class):
                    self.destroy()
                    return

        # check for collisions with enemies
        for enemy in self.game.enemies:
            if enemy.state == TankState.Alive and self.rect.colliderect(enemy.rect):
                if enemy.bulletImpact(self.owner == GameSide.Enemy, self.damage, self.owner_class):
                    self.destroy()
                    return

        # check for collision with castle
        if self.game.castle.active and self.rect.colliderect(self.game.castle.rect):
            self.game.castle.destroy()
            self.destroy()
            return

    def explode(self):
        if self.state != BulletState.Removed:
            self.state = BulletState.Exploding
            self.explosion = Explosion(self.game, [self.rect.left - 13, self.rect.top - 13],
                                       100, self.explosion_images)

    def destroy(self):
        self.state = BulletState.Removed
