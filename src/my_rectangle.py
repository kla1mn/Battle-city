import pygame


class MyRect(pygame.Rect):
    def __init__(self, left, top, width, height, type):
        pygame.Rect.__init__(self, left, top, width, height)
        self.type = type
