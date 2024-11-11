import random

import pygame

from src.bullet import Bullet
from src.explosion import Explosion
from src.label import Label

from src.constants import BulletState, Direction, GameSide, TankState


class Tank:
    def __init__(self, game, level, side, position=None, direction=None):
        self.game = game
        self.health = 100
        self.paralyzed = False
        self.paused = False
        self.shielded = False
        self.speed = 2
        self.max_active_bullets = 1
        self.side = side
        self.flash = 0
        # 0 - no superpowers
        # 1 - faster bullets
        # 2 - can fire 2 bullets
        # 3 - can destroy steel
        self.superpowers = 0
        self.bonus = None
        self.controls = [pygame.K_SPACE, pygame.K_UP, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_LEFT]
        self.pressed = [False] * 4

        self.image = None
        self.image_up = None
        self.image_right = None
        self.image_down = None
        self.image_left = None

        self.shield_images = [
            self.game.sprites.subsurface(0, 48 * 2, 16 * 2, 16 * 2),
            self.game.sprites.subsurface(16 * 2, 48 * 2, 16 * 2, 16 * 2)
        ]
        self.shield_image = self.shield_images[0]
        self.shield_index = 0

        self.spawn_images = [
            self.game.sprites.subsurface(32 * 2, 48 * 2, 16 * 2, 16 * 2),
            self.game.sprites.subsurface(48 * 2, 48 * 2, 16 * 2, 16 * 2)
        ]
        self.spawn_image = self.spawn_images[0]
        self.spawn_index = 0

        self.level = level

        if position is not None:
            self.rect = pygame.Rect(position, (26, 26))
        else:
            self.rect = pygame.Rect(0, 0, 26, 26)

        if direction is None:
            self.direction = random.choice([Direction.Right, Direction.Down, Direction.Left])
        else:
            self.direction = direction

        self.state = TankState.Spawning

        self.timer_uuid_spawn = self.game.gtimer.add(100, lambda: self.toggle_spawn_image())
        self.timer_uuid_spawn_end = self.game.gtimer.add(1000, lambda: self.end_spawning())

    def end_spawning(self):
        self.state = TankState.Alive
        self.game.gtimer.destroy(self.timer_uuid_spawn_end)

    def toggle_spawn_image(self):
        if self.state != TankState.Spawning:
            self.game.gtimer.destroy(self.timer_uuid_spawn)
            return
        self.spawn_index += 1
        if self.spawn_index >= len(self.spawn_images):
            self.spawn_index = 0
        self.spawn_image = self.spawn_images[self.spawn_index]

    def toggle_shield_image(self):
        if self.state != TankState.Alive:
            self.game.gtimer.destroy(self.timer_uuid_shield)
            return
        if self.shielded:
            self.shield_index += 1
            if self.shield_index >= len(self.shield_images):
                self.shield_index = 0
            self.shield_image = self.shield_images[self.shield_index]

    def draw(self):
        if self.state == TankState.Alive:
            self.game.screen.blit(self.image, self.rect.topleft)
            if self.shielded:
                self.game.screen.blit(self.shield_image, [self.rect.left - 3, self.rect.top - 3])
        elif self.state == TankState.Exploding:
            self.explosion.draw()
        elif self.state == TankState.Spawning:
            self.game.screen.blit(self.spawn_image, self.rect.topleft)

    def explode(self):
        if self.state != TankState.Dead:
            self.state = TankState.Exploding
            self.explosion = Explosion(self.game, self.rect.topleft)

            if self.bonus:
                self.spawn_bonus()

    def fire(self, forced=False):
        if self.state != TankState.Alive:
            self.game.gtimer.destroy(self.timer_uuid_fire)
            return False

        if self.paused:
            return False

        if not forced:
            active_bullets = 0
            for bullet in self.game.bullets:
                if bullet.owner_class == self and bullet.state == BulletState.Active:
                    active_bullets += 1
            if active_bullets >= self.max_active_bullets:
                return False

        bullet = Bullet(self.game, self.level, self.rect.topleft, self.direction)

        # if superpower level is at least 1
        if self.superpowers > 0:
            bullet.speed = 8

        # if superpower level is at least 3
        if self.superpowers > 2:
            bullet.power = 2

        if self.side == GameSide.Player:
            bullet.owner = GameSide.Player
        else:
            bullet.owner = GameSide.Enemy
            self.bullet_queued = False

        bullet.owner_class = self
        self.game.bullets.append(bullet)
        return True

    def rotate(self, direction, fix_position=True):
        self.direction = direction

        if direction == Direction.Up:
            self.image = self.image_up
        elif direction == Direction.Right:
            self.image = self.image_right
        elif direction == Direction.Down:
            self.image = self.image_down
        elif direction == Direction.Left:
            self.image = self.image_left

        if fix_position:
            new_x = self.get_nearest(self.rect.left, 8) + 3
            new_y = self.get_nearest(self.rect.top, 8) + 3
            if abs(self.rect.left - new_x) < 5:
                self.rect.left = new_x
            if abs(self.rect.top - new_y) < 5:
                self.rect.top = new_y

    def turn_around(self):
        if self.direction in (Direction.Up, Direction.Right):
            self.rotate(self.direction + 2, False)
        else:
            self.rotate(self.direction - 2, False)

    def update(self, time_passed):
        if self.state == TankState.Exploding:
            if not self.explosion.active:
                self.state = TankState.Dead
                del self.explosion

    def get_nearest(self, num, base):
        return int(round(num / (base * 1.0)) * base)

    def calculate_bullet_impact(self, friendly_fire=False, damage=100, tank=None):
        if self.shielded:
            return True

        if not friendly_fire:
            self.health -= damage
            if self.health < 1:
                if self.side == GameSide.Enemy:
                    tank.trophies["enemy" + str(self.type)] += 1
                    points = (self.type + 1) * 100
                    tank.score += points
                    if self.game.play_sounds:
                        self.game.sounds["explosion"].play()

                    self.game.labels.append(Label(self.game, self.rect.topleft, str(points), 500))

                self.explode()
            return True

        if self.side == GameSide.Enemy:
            return False
        elif self.side == GameSide.Player:
            if not self.paralyzed:
                self.set_paralyzed(True)
                self.timer_uuid_paralise = self.game.gtimer.add(10000, lambda: self.set_paralyzed(False), 1)
            return True

    def set_paralyzed(self, paralyzed=True):
        if self.state != TankState.Alive:
            self.game.gtimer.destroy(self.timer_uuid_paralise)
            return
        self.paralyzed = paralyzed
