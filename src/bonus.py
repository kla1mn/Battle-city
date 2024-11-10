import random

import pygame

from src.constants import BonusType


class Bonus:
    """
    grenade	- explodes all enemies
    helmet - temporary shield from bullets
    shovel - stone walls around fortress
    star - level up
    tank - extra life
    timer - freeze time
    """
    def __init__(self, game, level):
        self.game = game
        self.level = level
        self.active = True
        self.visible = True
        self.rect = pygame.Rect(random.randint(0, 416 - 32), random.randint(0, 416 - 32), 32, 32)
        self.bonus = random.choice([
            BonusType.Grenade,
            BonusType.Helmet,
            BonusType.Shovel,
            BonusType.Star,
            BonusType.Tank,
            BonusType.Timer
        ])
        self.image = self.game.sprites.subsurface(16 * 2 * self.bonus, 32 * 2, 16 * 2, 15 * 2)

    def draw(self):
        if self.visible:
            self.game.screen.blit(self.image, self.rect.topleft)

    def toggle_visibility(self):
        self.visible = not self.visible
