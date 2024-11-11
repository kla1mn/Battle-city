import random

import pygame

from src.bonus import Bonus
from src.constants import TILE_SIZE, Direction, TankState, EnemyType
from src.tank import Tank


class Enemy(Tank):
    def __init__(self, game, level, type, position=None):
        Tank.__init__(self, game, level, type, position=None, direction=None)
        self.game = game
        self.bullet_queued = False
        if len(level.enemies_left) > 0:
            self.type = level.enemies_left.pop()
        else:
            self.state = TankState.Dead
            return

        if self.type == EnemyType.Basic:
            self.speed = 1
        elif self.type == EnemyType.Fast:
            self.speed = 3
        elif self.type == EnemyType.Powerful:
            self.superpowers = 1
        elif self.type == EnemyType.Armored:
            self.health = 400

        if random.randint(1, 5) == 1:
            self.bonus = True
            for enemy in self.game.enemies:
                if enemy.bonus:
                    self.bonus = False
                    break

        images = [
            self.game.sprites.subsurface(32 * 2, 0, 13 * 2, 15 * 2),
            self.game.sprites.subsurface(48 * 2, 0, 13 * 2, 15 * 2),
            self.game.sprites.subsurface(64 * 2, 0, 13 * 2, 15 * 2),
            self.game.sprites.subsurface(80 * 2, 0, 13 * 2, 15 * 2),
            self.game.sprites.subsurface(32 * 2, 16 * 2, 13 * 2, 15 * 2),
            self.game.sprites.subsurface(48 * 2, 16 * 2, 13 * 2, 15 * 2),
            self.game.sprites.subsurface(64 * 2, 16 * 2, 13 * 2, 15 * 2),
            self.game.sprites.subsurface(80 * 2, 16 * 2, 13 * 2, 15 * 2)
        ]

        self.image = images[self.type + 0]

        self.image_up = self.image
        self.image_left = pygame.transform.rotate(self.image, 90)
        self.image_down = pygame.transform.rotate(self.image, 180)
        self.image_right = pygame.transform.rotate(self.image, 270)

        if self.bonus:
            self.image1_up = self.image_up
            self.image1_left = self.image_left
            self.image1_down = self.image_down
            self.image1_right = self.image_right

            self.image2 = images[self.type + 4]
            self.image2_up = self.image2
            self.image2_left = pygame.transform.rotate(self.image2, 90)
            self.image2_down = pygame.transform.rotate(self.image2, 180)
            self.image2_right = pygame.transform.rotate(self.image2, 270)

        self.rotate(self.direction, False)

        if position is None:
            self.rect.topleft = self.get_free_spawning_position()
            if not self.rect.topleft:
                self.state = TankState.Dead
                return

        self.path = self.generate_path(self.direction)
        self.timer_uuid_fire = self.game.gtimer.add(1000, lambda: self.fire())

        if self.bonus:
            self.timer_uuid_flash = self.game.gtimer.add(200, lambda: self.toggle_flash())

    def toggle_flash(self):
        if self.state not in (TankState.Alive, TankState.Spawning):
            self.game.gtimer.destroy(self.timer_uuid_flash)
            return
        self.flash = not self.flash
        if self.flash:
            self.image_up = self.image2_up
            self.image_right = self.image2_right
            self.image_down = self.image2_down
            self.image_left = self.image2_left
        else:
            self.image_up = self.image1_up
            self.image_right = self.image1_right
            self.image_down = self.image1_down
            self.image_left = self.image1_left
        self.rotate(self.direction, False)

    def spawn_bonus(self):
        if len(self.game.bonuses) > 0:
            return
        bonus = Bonus(self.game, self.level)
        self.game.bonuses.append(bonus)
        self.game.gtimer.add(500, lambda: bonus.toggle_visibility())
        self.game.gtimer.add(10000, lambda: self.game.bonuses.remove(bonus), 1)

    def get_free_spawning_position(self):
        available_positions = [
            [(TILE_SIZE * 2 - self.rect.width) / 2, (TILE_SIZE * 2 - self.rect.height) / 2],
            [12 * TILE_SIZE + (TILE_SIZE * 2 - self.rect.width) / 2, (TILE_SIZE * 2 - self.rect.height) / 2],
            [24 * TILE_SIZE + (TILE_SIZE * 2 - self.rect.width) / 2, (TILE_SIZE * 2 - self.rect.height) / 2]
        ]

        random.shuffle(available_positions)

        for pos in available_positions:
            enemy_rect = pygame.Rect(pos, [26, 26])
            collision = False
            for enemy in self.game.enemies:
                if enemy_rect.colliderect(enemy.rect):
                    collision = True
                    continue

            if collision:
                continue

            collision = False
            for player in self.game.players:
                if enemy_rect.colliderect(player.rect):
                    collision = True
                    continue

            if collision:
                continue

            return pos
        return False

    def move(self):
        if self.state != TankState.Alive or self.paused or self.paralyzed:
            return

        if not self.path:
            self.path = self.generate_path(None, True)

        new_position = self.path.pop(0)

        # move enemy
        if self.direction == Direction.Up:
            if new_position[1] < 0:
                self.path = self.generate_path(self.direction, True)
                return
        elif self.direction == Direction.Right:
            if new_position[0] > (416 - 26):
                self.path = self.generate_path(self.direction, True)
                return
        elif self.direction == Direction.Down:
            if new_position[1] > (416 - 26):
                self.path = self.generate_path(self.direction, True)
                return
        elif self.direction == Direction.Left:
            if new_position[0] < 0:
                self.path = self.generate_path(self.direction, True)
                return

        new_rect = pygame.Rect(new_position, [26, 26])

        if new_rect.collidelist(self.level.obstacle_rects) != -1:
            self.path = self.generate_path(self.direction, True)
            return

        for enemy in self.game.enemies:
            if enemy != self and new_rect.colliderect(enemy.rect):
                self.turn_around()
                self.path = self.generate_path(self.direction)
                return

        for player in self.game.players:
            if new_rect.colliderect(player.rect):
                self.turn_around()
                self.path = self.generate_path(self.direction)
                return

        for bonus in self.game.bonuses:
            if new_rect.colliderect(bonus.rect):
                self.game.bonuses.remove(bonus)

        self.rect.topleft = new_rect.topleft

    def update(self, time_passed):
        Tank.update(self, time_passed)
        if self.state == TankState.Alive and not self.paused:
            self.move()

    def generate_path(self, direction=None, fix_direction=False):
        all_directions = [Direction.Up, Direction.Right, Direction.Down, Direction.Left]

        if direction is None:
            if self.direction in [Direction.Up, Direction.Right]:
                opposite_direction = self.direction + 2
            else:
                opposite_direction = self.direction - 2
            directions = all_directions
            random.shuffle(directions)
            directions.remove(opposite_direction)
            directions.append(opposite_direction)
        else:
            if direction in [Direction.Up, Direction.Right]:
                opposite_direction = direction + 2
            else:
                opposite_direction = direction - 2

            if direction in [Direction.Up, Direction.Right]:
                opposite_direction = direction + 2
            else:
                opposite_direction = direction - 2
            directions = all_directions
            random.shuffle(directions)
            directions.remove(opposite_direction)
            directions.remove(direction)
            directions.insert(0, direction)
            directions.append(opposite_direction)

        x = int(round(self.rect.left / 16))
        y = int(round(self.rect.top / 16))

        new_direction = None

        for direction in directions:
            if direction == Direction.Up and y > 1:
                new_pos_rect = self.rect.move(0, -8)
                if new_pos_rect.collidelist(self.level.obstacle_rects) == -1:
                    new_direction = direction
                    break
            elif direction == Direction.Right and x < 24:
                new_pos_rect = self.rect.move(8, 0)
                if new_pos_rect.collidelist(self.level.obstacle_rects) == -1:
                    new_direction = direction
                    break
            elif direction == Direction.Down and y < 24:
                new_pos_rect = self.rect.move(0, 8)
                if new_pos_rect.collidelist(self.level.obstacle_rects) == -1:
                    new_direction = direction
                    break
            elif direction == Direction.Left and x > 1:
                new_pos_rect = self.rect.move(-8, 0)
                if new_pos_rect.collidelist(self.level.obstacle_rects) == -1:
                    new_direction = direction
                    break

        if new_direction is None:
            new_direction = opposite_direction

        if fix_direction and new_direction == self.direction:
            fix_direction = False

        self.rotate(new_direction, fix_direction)

        positions = []
        x = self.rect.left
        y = self.rect.top

        if new_direction in (Direction.Right, Direction.Left):
            axis_fix = self.get_nearest(y, 16) - y
        else:
            axis_fix = self.get_nearest(x, 16) - x
        axis_fix = 0

        pixels = self.get_nearest(random.randint(1, 12) * 32, 32) + axis_fix + 3

        if new_direction == Direction.Up:
            for px in range(0, pixels, self.speed):
                positions.append([x, y - px])
        elif new_direction == Direction.Right:
            for px in range(0, pixels, self.speed):
                positions.append([x + px, y])
        elif new_direction == Direction.Down:
            for px in range(0, pixels, self.speed):
                positions.append([x, y + px])
        elif new_direction == Direction.Left:
            for px in range(0, pixels, self.speed):
                positions.append([x - px, y])

        return positions
