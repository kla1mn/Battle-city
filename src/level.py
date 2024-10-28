import os
import pygame

from src.my_rectangle import RectangleWithType

from src.constants import TILE_SIZE, Tile


class Level:
    def __init__(self, game, level_number=None):
        self.game = game
        self.max_active_enemies = 4
        self.map = []

        tile_images = [
            pygame.Surface((8 * 2, 8 * 2)),
            self.game.sprites.subsurface(48 * 2, 64 * 2, 8 * 2, 8 * 2),
            self.game.sprites.subsurface(48 * 2, 72 * 2, 8 * 2, 8 * 2),
            self.game.sprites.subsurface(56 * 2, 72 * 2, 8 * 2, 8 * 2),
            self.game.sprites.subsurface(64 * 2, 64 * 2, 8 * 2, 8 * 2),
            self.game.sprites.subsurface(64 * 2, 64 * 2, 8 * 2, 8 * 2),
            self.game.sprites.subsurface(72 * 2, 64 * 2, 8 * 2, 8 * 2),
            self.game.sprites.subsurface(64 * 2, 72 * 2, 8 * 2, 8 * 2)
        ]
        self.tile_empty = tile_images[0]
        self.tile_brick = tile_images[1]
        self.tile_steel = tile_images[2]
        self.tile_grass = tile_images[3]
        self.tile_water = tile_images[4]
        self.tile_water1 = tile_images[4]
        self.tile_water2 = tile_images[5]
        self.tile_froze = tile_images[6]

        self.obstacle_rects = []

        level_number = 1 if level_number is None or level_number == 0 else level_number % 36

        self.load_level(level_number)
        self.obstacle_rects = []
        self.update_obstacle_rects()
        self.game.gtimer.add(500, lambda: self.toggle_waves())

    def hit_tile(self, pos, power=1, sound=False):
        for tile in self.map:
            if tile.topleft == pos:
                if tile.type == Tile.Brick:
                    if self.game.play_sounds and sound:
                        self.game.sounds["brick"].play()
                    self.map.remove(tile)
                    self.update_obstacle_rects()
                    return True
                elif tile.type == Tile.Steel:
                    if self.game.play_sounds and sound:
                        self.game.sounds["steel"].play()
                    if power == 2:
                        self.map.remove(tile)
                        self.update_obstacle_rects()
                    return True
                else:
                    return False

    def toggle_waves(self):
        if self.tile_water == self.tile_water1:
            self.tile_water = self.tile_water2
        else:
            self.tile_water = self.tile_water1

    def load_level(self, level_number=1):
        filename = f"../levels/{level_number}"
        if not os.path.isfile(filename):
            return False
        with open(filename, "r") as f:
            data = f.read().split("\n")
            self.map = []
            x, y = 0, 0
            for row in data:
                for ch in row:
                    if ch == "#":
                        self.map.append(RectangleWithType(x, y, TILE_SIZE, TILE_SIZE, Tile.Brick))
                    elif ch == "@":
                        self.map.append(RectangleWithType(x, y, TILE_SIZE, TILE_SIZE, Tile.Steel))
                    elif ch == "~":
                        self.map.append(RectangleWithType(x, y, TILE_SIZE, TILE_SIZE, Tile.Water))
                    elif ch == "%":
                        self.map.append(RectangleWithType(x, y, TILE_SIZE, TILE_SIZE, Tile.Grass))
                    elif ch == "-":
                        self.map.append(RectangleWithType(x, y, TILE_SIZE, TILE_SIZE, Tile.Frozen))
                    x += TILE_SIZE
                x = 0
                y += TILE_SIZE
        return True

    def draw(self, tiles=None):
        if tiles is None:
            tiles = [Tile.Brick, Tile.Steel, Tile.Water, Tile.Grass, Tile.Frozen]

        for tile in self.map:
            if tile.type in tiles:
                if tile.type == Tile.Brick:
                    self.game.screen.blit(self.tile_brick, tile.topleft)
                elif tile.type == Tile.Steel:
                    self.game.screen.blit(self.tile_steel, tile.topleft)
                elif tile.type == Tile.Water:
                    self.game.screen.blit(self.tile_water, tile.topleft)
                elif tile.type == Tile.Frozen:
                    self.game.screen.blit(self.tile_froze, tile.topleft)
                elif tile.type == Tile.Grass:
                    self.game.screen.blit(self.tile_grass, tile.topleft)

    def update_obstacle_rects(self):
        self.obstacle_rects = [self.game.castle.rect]
        for tile in self.map:
            if tile.type in (Tile.Brick, Tile.Steel, Tile.Water):
                self.obstacle_rects.append(tile)

    def build_castle(self, tile):
        from src.constants import CASTLE_TILES
        obsolete = []
        for i, rect in enumerate(self.map):
            if rect.topleft in CASTLE_TILES:
                obsolete.append(rect)
        for rect in obsolete:
            self.map.remove(rect)

        for pos in CASTLE_TILES:
            self.map.append(RectangleWithType(pos[0], pos[1], TILE_SIZE, TILE_SIZE, tile))

        self.update_obstacle_rects()
