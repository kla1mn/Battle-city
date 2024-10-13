import os
import pygame
from level import Level
from castle import Castle
from player import Player
from enemy import Enemy
from bullet import Bullet
from bonus import Bonus
from timer import Timer

SCREEN_WIDTH = 480
SCREEN_HEIGHT = 416


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Battle City")
        self.clock = pygame.time.Clock()
        self.sprites = self.load_sprites()
        self.sounds = self.load_sounds()
        self.timer = Timer()
        self.level = Level(self)
        self.castle = Castle(self)
        self.players = []
        self.enemies = []
        self.bullets = []
        self.bonuses = []
        self.labels = []
        self.stage = 1
        self.game_over = False
        self.active = True

    def load_sprites(self):
        src_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(src_dir)
        sprites_path = os.path.join(project_root, 'sprites', 'sprites.gif')
        return pygame.transform.scale(pygame.image.load(sprites_path), [192, 224])

    def load_sounds(self):
        src_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(src_dir)
        sounds_dir = os.path.join(project_root, 'sounds')

        sounds = {}
        sound_files = ["gamestart", "gameover", "score", "background", "fire", "bonus", "explosion", "brick", "steel"]

        for sound in sound_files:
            sound_path = os.path.join(sounds_dir, f"{sound}.ogg")
            if os.path.exists(sound_path):
                sounds[sound] = pygame.mixer.Sound(sound_path)

        return sounds

    def start(self):
        self.show_menu()
        self.main_loop()

    def show_menu(self):
        # Реализация меню
        pass

    def main_loop(self):
        while self.active:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(50)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.active = False
            # Обработка других событий

    def update(self):
        self.timer.update()
        for player in self.players:
            player.update()
        for enemy in self.enemies:
            enemy.update()
        for bullet in self.bullets:
            bullet.update()
        for bonus in self.bonuses:
            bonus.update()
        self.level.update()

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.level.draw()
        self.castle.draw()
        for player in self.players:
            player.draw()
        for enemy in self.enemies:
            enemy.draw()
        for bullet in self.bullets:
            bullet.draw()
        for bonus in self.bonuses:
            bonus.draw()
        pygame.display.flip()