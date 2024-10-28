import os
import pygame

from src.my_rectangle import MyRect

from src.constants import TILE_SIZE, Tile


class Level:
    def __init__(self, game, level_nr=None):
        """ There are total 35 different levels. If level_nr is larger than 35, loop over
        to next according level so, for example, if level_nr ir 37, then load level 2 """
        self.mapr = []
        self.game = game

        # max number of enemies simultaneously  being on map
        self.max_active_enemies = 4

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

        level_nr = 1 if level_nr is None else level_nr % 35
        if level_nr == 0:
            level_nr = 35

        self.loadLevel(level_nr)

        # tiles' rects on map, tanks cannot move over
        self.obstacle_rects = []

        # update these tiles
        self.updateObstacleRects()

        self.game.gtimer.add(10000, lambda: self.toggleWaves())

    def hitTile(self, pos, power=1, sound=False):
        """
            Hit the tile
            @param pos Tile's x, y in px
            @return True if bullet was stopped, False otherwise
        """

        for tile in self.mapr:
            if tile.topleft == pos:
                if tile.type == Tile.Brick:
                    if self.game.play_sounds and sound:
                        self.game.sounds["brick"].play()
                    self.mapr.remove(tile)
                    self.updateObstacleRects()
                    return True
                elif tile.type == Tile.Steel:
                    if self.game.play_sounds and sound:
                        self.game.sounds["steel"].play()
                    if power == 2:
                        self.mapr.remove(tile)
                        self.updateObstacleRects()
                    return True
                else:
                    return False

    def toggleWaves(self):
        """ Toggle water image """
        if self.tile_water == self.tile_water1:
            self.tile_water = self.tile_water2
        else:
            self.tile_water = self.tile_water1

    def loadLevel(self, level_nr=1):
        """ Load specified level
        @return boolean Whether level was loaded
        """
        filename = "../levels/" + str(level_nr)
        if not os.path.isfile(filename):
            return False
        level = []
        f = open(filename, "r")
        data = f.read().split("\n")
        self.mapr = []
        x, y = 0, 0
        for row in data:
            for ch in row:
                if ch == "#":
                    self.mapr.append(MyRect(x, y, TILE_SIZE, TILE_SIZE, Tile.Brick))
                elif ch == "@":
                    self.mapr.append(MyRect(x, y, TILE_SIZE, TILE_SIZE, Tile.Steel))
                elif ch == "~":
                    self.mapr.append(MyRect(x, y, TILE_SIZE, TILE_SIZE, Tile.Water))
                elif ch == "%":
                    self.mapr.append(MyRect(x, y, TILE_SIZE, TILE_SIZE, Tile.Grass))
                elif ch == "-":
                    self.mapr.append(MyRect(x, y, TILE_SIZE, TILE_SIZE, Tile.Frozen))
                x += TILE_SIZE
            x = 0
            y += TILE_SIZE
        return True

    def draw(self, tiles=None):
        """ Draw specified map on top of existing surface """

        if tiles is None:
            tiles = [Tile.Brick, Tile.Steel, Tile.Water, Tile.Grass, Tile.Frozen]

        for tile in self.mapr:
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

    def updateObstacleRects(self):
        """ Set self.obstacle_rects to all tiles' rects that players can destroy
        with bullets """

        self.obstacle_rects = [self.game.castle.rect]

        for tile in self.mapr:
            if tile.type in (Tile.Brick, Tile.Steel, Tile.Water):
                self.obstacle_rects.append(tile)

    def build_castle(self, tile):
        from src.constants import CASTLE_TILES
        obsolete = []
        for i, rect in enumerate(self.mapr):
            if rect.topleft in CASTLE_TILES:
                obsolete.append(rect)
        for rect in obsolete:
            self.mapr.remove(rect)

        for pos in CASTLE_TILES:
            self.mapr.append(MyRect(pos[0], pos[1], TILE_SIZE, TILE_SIZE, tile))

        self.updateObstacleRects()
