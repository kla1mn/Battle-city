import pygame

from src.tank import Tank

from src.constants import Direction, TankState


class Player(Tank):
    def __init__(self, game, level, type, position=None, direction=None, filename=None):
        Tank.__init__(self, game, level, type, position=None, direction=None)
        if filename is None:
            filename = (0, 0, 16 * 2, 16 * 2)
        self.start_position = position
        self.start_direction = direction
        self.lives = 3
        self.score = 0
        self.trophies = {
            "bonus": 0,
            "enemy0": 0,
            "enemy1": 0,
            "enemy2": 0,
            "enemy3": 0
        }
        self.image = self.game.sprites.subsurface(filename)
        self.image_up = self.image
        self.image_left = pygame.transform.rotate(self.image, 90)
        self.image_down = pygame.transform.rotate(self.image, 180)
        self.image_right = pygame.transform.rotate(self.image, 270)

        if direction is None:
            self.rotate(Direction.Up, False)
        else:
            self.rotate(direction, False)

    def move(self, direction):
        if self.state == TankState.Exploding:
            if not self.explosion.active:
                self.state = TankState.Dead
                del self.explosion

        if self.state != TankState.Alive:
            return

        if self.direction != direction:
            self.rotate(direction)

        if self.paralised:
            return

        new_position = [0, 0]
        if direction == Direction.Up:
            new_position = [self.rect.left, self.rect.top - self.speed]
            if new_position[1] < 0:
                return
        elif direction == Direction.Right:
            new_position = [self.rect.left + self.speed, self.rect.top]
            if new_position[0] > (416 - 26):
                return
        elif direction == Direction.Down:
            new_position = [self.rect.left, self.rect.top + self.speed]
            if new_position[1] > (416 - 26):
                return
        elif direction == Direction.Left:
            new_position = [self.rect.left - self.speed, self.rect.top]
            if new_position[0] < 0:
                return

        player_rect = pygame.Rect(new_position, [26, 26])

        if player_rect.collidelist(self.level.obstacle_rects) != -1:
            return

        for player in self.game.players:
            if player != self and player.state == TankState.Alive and player_rect.colliderect(player.rect) is True:
                return

        for enemy in self.game.enemies:
            if player_rect.colliderect(enemy.rect) is True:
                return

        for bonus in self.game.bonuses:
            if player_rect.colliderect(bonus.rect) is True:
                self.bonus = bonus

        self.rect.topleft = (new_position[0], new_position[1])

    def reset(self):
        self.rotate(self.start_direction, False)
        self.rect.topleft = self.start_position
        self.superpowers = 0
        self.max_active_bullets = 1
        self.health = 100
        self.paralised = False
        self.paused = False
        self.pressed = [False] * 4
        self.state = TankState.Alive
