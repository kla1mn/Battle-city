from enum import IntEnum

TILE_SIZE = 16

ENEMIES_BY_LEVEL = (
    (18, 2, 0, 0), (14, 4, 0, 2), (14, 4, 0, 2), (2, 5, 10, 3), (8, 5, 5, 2),
    (9, 2, 7, 2), (7, 4, 6, 3), (7, 4, 7, 2), (6, 4, 7, 3), (12, 2, 4, 2),
    (5, 5, 4, 6), (0, 6, 8, 6), (0, 8, 8, 4), (0, 4, 10, 6), (0, 2, 10, 8),
    (16, 2, 0, 2), (8, 2, 8, 2), (2, 8, 6, 4), (4, 4, 4, 8), (2, 8, 2, 8),
    (6, 2, 8, 4), (6, 8, 2, 4), (0, 10, 4, 6), (10, 4, 4, 2), (0, 8, 2, 10),
    (4, 6, 4, 6), (2, 8, 2, 8), (15, 2, 2, 1), (0, 4, 10, 6), (4, 8, 4, 4),
    (3, 8, 3, 6), (6, 4, 2, 8), (4, 4, 4, 8), (0, 10, 4, 6), (0, 6, 4, 10))

CASTLE_TILES = [(11 * TILE_SIZE, 23 * TILE_SIZE),
                (11 * TILE_SIZE, 24 * TILE_SIZE),
                (11 * TILE_SIZE, 25 * TILE_SIZE),
                (14 * TILE_SIZE, 23 * TILE_SIZE),
                (14 * TILE_SIZE, 24 * TILE_SIZE),
                (14 * TILE_SIZE, 25 * TILE_SIZE),
                (12 * TILE_SIZE, 23 * TILE_SIZE),
                (13 * TILE_SIZE, 23 * TILE_SIZE)]


class Direction(IntEnum):
    Up = 0
    Right = 1
    Down = 2
    Left = 3


class Tile(IntEnum):
    Empty = 0
    Brick = 1
    Steel = 2
    Water = 3
    Grass = 4
    Frozen = 5


class CastleState(IntEnum):
    Standing = 0
    Destroyed = 1
    Exploding = 2


class GameSide(IntEnum):
    Player = 0
    Enemy = 1


class BulletState(IntEnum):
    Removed = 0
    Active = 1
    Exploding = 2


class BulletPower(IntEnum):
    Regular = 0
    Powerful = 1


ALPHABET = {"a": "0071b63c7ff1e3",
            "b": "01fb1e3fd8f1fe",
            "c": "00799e0c18199e",
            "e": "01fb060f98307e",
            "g": "007d860cf8d99f",
            "i": "01f8c183060c7e",
            "l": "0183060c18307e",
            "m": "018fbffffaf1e3",
            "o": "00fb1e3c78f1be",
            "r": "01fb1e3cff3767",
            "t": "01f8c183060c18",
            "v": "018f1e3eef8e08",
            "y": "019b3667860c18"}


class TankState(IntEnum):
    Spawning = 0
    Dead = 1
    Alive = 2
    Exploding = 3


class BonusType(IntEnum):
    Grenade = 0
    Helmet = 1
    Shovel = 2
    Star = 3
    Tank = 4
    Timer = 5


class EnemyType(IntEnum):
    Basic = 0
    Fast = 1
    Powerful = 2
    Armored = 3
