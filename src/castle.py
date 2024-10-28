import pygame

from src.explosion import Explosion

from src.constants import CastleState


class Castle:
    def __init__(self, game):
        self.game = game
        self.explosion = None
        self.active = None
        self.image = None
        self.state = None
        self.img_undamaged = self.game.sprites.subsurface(0, 15 * 2, 16 * 2, 16 * 2)
        self.img_destroyed = self.game.sprites.subsurface(16 * 2, 15 * 2, 16 * 2, 16 * 2)
        self.rect = pygame.Rect(12 * 16, 24 * 16, 32, 32)
        self.rebuild()

    def draw(self):
        self.game.screen.blit(self.image, self.rect.topleft)
        if self.state == CastleState.Exploding:
            if not self.explosion.active:
                self.state = CastleState.Destroyed
                del self.explosion
            else:
                self.explosion.draw()

    def rebuild(self):
        self.state = CastleState.Standing
        self.image = self.img_undamaged
        self.active = True

    def destroy(self):
        self.state = CastleState.Exploding
        self.explosion = Explosion(self.game, self.rect.topleft)
        self.image = self.img_destroyed
        self.active = False
