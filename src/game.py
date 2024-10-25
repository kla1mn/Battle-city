import pygame
import os
import sys
import random

from src.castle import Castle
from src.level import Level
from src.player import Player
from src.enemy import Enemy
from src.label import Label
from src.timer import Timer


class Game:
    (DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)

    TILE_SIZE = 16

    def __init__(self):
        pygame.init()

        self.sprites = None
        self.screen = None
        self.players = []
        self.enemies = []
        self.bullets = []
        self.bonuses = []
        self.labels = []
        self.castle = None
        self.level = None

        self.play_sounds = True
        self.sounds = {}

        self.gtimer = Timer()

        # Game state variables
        self.game_over = False
        self.running = True
        self.active = True
        self.timefreeze = False

        # Stage and score variables
        self.stage = 1
        self.nr_of_players = 1

        self.initialize_game()

    def initialize_game(self):
        os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'

        if self.play_sounds:
            pygame.mixer.pre_init(44100, -16, 1, 512)

        pygame.display.set_caption("Battle City")

        size = 480, 416

        if "-f" in sys.argv[1:]:
            self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(size)

        self.clock = pygame.time.Clock()
        self.sprites = pygame.transform.scale(pygame.image.load("../sprites/sprites.gif"), [192, 224])
        pygame.display.set_icon(self.sprites.subsurface(0, 0, 13 * 2, 13 * 2))
        # Load sounds
        if self.play_sounds:
            pygame.mixer.init(44100, -16, 1, 512)
            self.loadSounds()

        # Initialize castle
        self.castle = Castle(self)

        # Load images
        self.enemy_life_image = self.sprites.subsurface(81 * 2, 57 * 2, 7 * 2, 7 * 2)
        self.player_life_image = self.sprites.subsurface(89 * 2, 56 * 2, 7 * 2, 8 * 2)
        self.flag_image = self.sprites.subsurface(64 * 2, 49 * 2, 16 * 2, 15 * 2)
        self.player_image = pygame.transform.rotate(self.sprites.subsurface(0, 0, 13 * 2, 13 * 2), 270)

        # Load font
        self.font = pygame.font.Font("../fonts/font.ttf", 16)

        # Pre-render game over text
        self.im_game_over = pygame.Surface((64, 40))
        self.im_game_over.set_colorkey((0, 0, 0))
        self.im_game_over.blit(self.font.render("GAME", False, (127, 64, 64)), [0, 0])
        self.im_game_over.blit(self.font.render("OVER", False, (127, 64, 64)), [0, 20])
        self.game_over_y = 416 + 40

    def loadSounds(self):
        sound_names = ["gamestart", "gameover", "score", "background", "fire", "bonus", "explosion", "brick", "steel"]
        for name in sound_names:
            self.sounds[name] = pygame.mixer.Sound(f"../sounds/{name}.ogg")

    def showMenu(self):
        self.animateIntroScreen()

        main_loop = True
        while main_loop:
            self.clock.tick(50)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        quit()
                    elif event.key == pygame.K_UP:
                        if self.nr_of_players == 2:
                            self.nr_of_players = 1
                            self.drawIntroScreen()
                    elif event.key == pygame.K_DOWN:
                        if self.nr_of_players == 1:
                            self.nr_of_players = 2
                            self.drawIntroScreen()
                    elif event.key == pygame.K_RETURN:
                        main_loop = False

        self.players.clear()
        self.nextLevel()

    def nextLevel(self):
        del self.bullets[:]
        del self.enemies[:]
        del self.bonuses[:]
        self.castle.rebuild()
        del self.gtimer.timers[:]

        # load level
        self.stage += 1
        self.level = Level(self, self.stage)
        self.timefreeze = False

        # set number of enemies by types (basic, fast, power, armor) according to level
        levels_enemies = (
            (18, 2, 0, 0), (14, 4, 0, 2), (14, 4, 0, 2), (2, 5, 10, 3), (8, 5, 5, 2),
            (9, 2, 7, 2), (7, 4, 6, 3), (7, 4, 7, 2), (6, 4, 7, 3), (12, 2, 4, 2),
            (5, 5, 4, 6), (0, 6, 8, 6), (0, 8, 8, 4), (0, 4, 10, 6), (0, 2, 10, 8),
            (16, 2, 0, 2), (8, 2, 8, 2), (2, 8, 6, 4), (4, 4, 4, 8), (2, 8, 2, 8),
            (6, 2, 8, 4), (6, 8, 2, 4), (0, 10, 4, 6), (10, 4, 4, 2), (0, 8, 2, 10),
            (4, 6, 4, 6), (2, 8, 2, 8), (15, 2, 2, 1), (0, 4, 10, 6), (4, 8, 4, 4),
            (3, 8, 3, 6), (6, 4, 2, 8), (4, 4, 4, 8), (0, 10, 4, 6), (0, 6, 4, 10)
        )

        if self.stage <= 35:
            enemies_l = levels_enemies[self.stage - 1]
        else:
            enemies_l = levels_enemies[34]

        self.level.enemies_left = [0] * enemies_l[0] + [1] * enemies_l[1] + [2] * enemies_l[2] + [3] * enemies_l[3]
        random.shuffle(self.level.enemies_left)

        if self.play_sounds:
            self.sounds["gamestart"].play()
            self.gtimer.add(4330, lambda: self.sounds["background"].play(-1), 1)

        self.reloadPlayers()

        self.gtimer.add(3000, lambda: self.spawnEnemy())

        self.game_over = False
        self.running = True
        self.active = True

        self.draw()

        while self.running:
            time_passed = self.clock.tick(50)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                elif event.type == pygame.KEYDOWN and not self.game_over and self.active:
                    self.handleKeyDown(event)
                elif event.type == pygame.KEYUP and not self.game_over and self.active:
                    self.handleKeyUp(event)

            for player in self.players:
                if player.state == player.STATE_ALIVE and not self.game_over and self.active:
                    self.handlePlayerMovement(player)
                player.update(time_passed)

            for enemy in self.enemies[:]:
                if enemy.state == enemy.STATE_DEAD and not self.game_over and self.active:
                    self.enemies.remove(enemy)
                    if len(self.level.enemies_left) == 0 and len(self.enemies) == 0:
                        self.finishLevel()
                else:
                    enemy.update(time_passed)

            if not self.game_over and self.active:
                for player in self.players:
                    if player.state == player.STATE_ALIVE:
                        if player.bonus is not None and player.side == player.SIDE_PLAYER:
                            self.triggerBonus(player.bonus, player)
                            player.bonus = None
                    elif player.state == player.STATE_DEAD:
                        self.superpowers = 0
                        player.lives -= 1
                        if player.lives > 0:
                            self.respawnPlayer(player)
                        else:
                            self.gameOver()

            for bullet in self.bullets[:]:
                if bullet.state == bullet.STATE_REMOVED:
                    self.bullets.remove(bullet)
                else:
                    bullet.update()

            for bonus in self.bonuses[:]:
                if not bonus.active:
                    self.bonuses.remove(bonus)

            for label in self.labels[:]:
                if not label.active:
                    self.labels.remove(label)

            if not self.game_over:
                if not self.castle.active:
                    self.gameOver()

            self.gtimer.update(time_passed)
            self.draw()

    def handleKeyDown(self, event):
        if event.key == pygame.K_q:
            quit()
        elif event.key == pygame.K_m:
            self.toggleSound()

        for player in self.players:
            if player.state == player.STATE_ALIVE:
                try:
                    index = player.controls.index(event.key)
                except ValueError:
                    pass
                else:
                    if index == 0:
                        if player.fire() and self.play_sounds:
                            self.sounds["fire"].play()
                    elif 1 <= index <= 4:
                        player.pressed[index - 1] = True

    def handleKeyUp(self, event):
        for player in self.players:
            if player.state == player.STATE_ALIVE:
                try:
                    index = player.controls.index(event.key)
                except ValueError:
                    pass
                else:
                    if 1 <= index <= 4:
                        player.pressed[index - 1] = False

    def handlePlayerMovement(self, player):
        if player.pressed[0]:
            player.move(self.DIR_UP)
        elif player.pressed[1]:
            player.move(self.DIR_RIGHT)
        elif player.pressed[2]:
            player.move(self.DIR_DOWN)
        elif player.pressed[3]:
            player.move(self.DIR_LEFT)

    def toggleSound(self):
        self.play_sounds = not self.play_sounds
        if not self.play_sounds:
            pygame.mixer.stop()
        else:
            self.sounds["background"].play(-1)

    def triggerBonus(self, bonus, player):
        if self.play_sounds:
            self.sounds["bonus"].play()

        player.trophies["bonus"] += 1
        player.score += 500

        if bonus.bonus == bonus.BONUS_GRENADE:
            for enemy in self.enemies:
                enemy.explode()
        elif bonus.bonus == bonus.BONUS_HELMET:
            self.shieldPlayer(player, True, 10000)
        elif bonus.bonus == bonus.BONUS_SHOVEL:
            self.level.buildFortress(self.level.TILE_STEEL)
            self.gtimer.add(10000, lambda: self.level.buildFortress(self.level.TILE_BRICK), 1)
        elif bonus.bonus == bonus.BONUS_STAR:
            player.superpowers += 1
            if player.superpowers == 2:
                player.max_active_bullets = 2
        elif bonus.bonus == bonus.BONUS_TANK:
            player.lives += 1
        elif bonus.bonus == bonus.BONUS_TIMER:
            self.toggleEnemyFreeze(True)
            self.gtimer.add(10000, lambda: self.toggleEnemyFreeze(False), 1)
        self.bonuses.remove(bonus)

        self.labels.append(Label(self, bonus.rect.topleft, "500", 500))

    def shieldPlayer(self, player, shield=True, duration=None):
        player.shielded = shield
        if shield:
            player.timer_uuid_shield = self.gtimer.add(100, lambda: player.toggleShieldImage())
        else:
            self.gtimer.destroy(player.timer_uuid_shield)

        if shield and duration is not None:
            self.gtimer.add(duration, lambda: self.shieldPlayer(player, False), 1)

    def spawnEnemy(self):
        if len(self.enemies) >= self.level.max_active_enemies:
            return
        if len(self.level.enemies_left) < 1 or self.timefreeze:
            return
        enemy = Enemy(self, self.level, 1)
        self.enemies.append(enemy)

    def reloadPlayers(self):
        if len(self.players) == 0:
            # first player
            x = 8 * self.TILE_SIZE + (self.TILE_SIZE * 2 - 26) / 2
            y = 24 * self.TILE_SIZE + (self.TILE_SIZE * 2 - 26) / 2

            player = Player(
                self, self.level, 0, [x, y], self.DIR_UP, (0, 0, 13 * 2, 13 * 2)
            )
            self.players.append(player)

            # second player
            if self.nr_of_players == 2:
                x = 16 * self.TILE_SIZE + (self.TILE_SIZE * 2 - 26) / 2
                y = 24 * self.TILE_SIZE + (self.TILE_SIZE * 2 - 26) / 2
                player = Player(self, self.level, 0, [x, y], self.DIR_UP, (16 * 2, 0, 13 * 2, 13 * 2))
                player.controls = [102, 119, 100, 115, 97]
                self.players.append(player)

        for player in self.players:
            player.level = self.level
            self.respawnPlayer(player, True)

    def respawnPlayer(self, player, clear_scores=False):
        player.reset()

        if clear_scores:
            player.trophies = {"bonus": 0, "enemy0": 0, "enemy1": 0, "enemy2": 0, "enemy3": 0}

        self.shieldPlayer(player, True, 4000)

    def gameOver(self):
        if self.play_sounds:
            for sound in self.sounds.values():
                sound.stop()
            self.sounds["gameover"].play()

        self.game_over_y = 416 + 40

        self.game_over = True
        self.stage = 1
        self.gtimer.add(3000, lambda: self.showScores(), 1)

    def finishLevel(self):
        if self.play_sounds:
            self.sounds["background"].stop()

        self.active = False
        self.gtimer.add(3000, lambda: self.showScores(), 1)

        print(f"Stage {self.stage - 1} completed")

    def drawSidebar(self):
        x = 416
        y = 0
        self.screen.fill([100, 100, 100], pygame.Rect([416, 0], [64, 416]))

        xpos = x + 16
        ypos = y + 16

        # draw enemy lives
        for n in range(len(self.level.enemies_left) + len(self.enemies)):
            self.screen.blit(self.enemy_life_image, [xpos, ypos])
            if n % 2 == 1:
                xpos = x + 16
                ypos += 17
            else:
                xpos += 17

        # players' lives
        if pygame.font.get_init():
            text_color = pygame.Color('black')
            for n in range(len(self.players)):
                if n == 0:
                    self.screen.blit(self.font.render(str(n + 1) + "P", False, text_color), [x + 16, y + 200])
                    self.screen.blit(self.font.render(str(self.players[n].lives), False, text_color), [x + 31, y + 215])
                    self.screen.blit(self.player_life_image, [x + 17, y + 215])
                else:
                    self.screen.blit(self.font.render(str(n + 1) + "P", False, text_color), [x + 16, y + 240])
                    self.screen.blit(self.font.render(str(self.players[n].lives), False, text_color), [x + 31, y + 255])
                    self.screen.blit(self.player_life_image, [x + 17, y + 255])

            self.screen.blit(self.flag_image, [x + 17, y + 280])
            self.screen.blit(self.font.render(str(self.stage), False, text_color), [x + 17, y + 312])

    def draw(self):
        self.screen.fill([0, 0, 0])

        self.level.draw([self.level.TILE_EMPTY, self.level.TILE_BRICK, self.level.TILE_STEEL, self.level.TILE_FROZE,
                         self.level.TILE_WATER])

        self.castle.draw()

        for enemy in self.enemies:
            enemy.draw()

        # for label in self.labels:
        # label.draw()

        for player in self.players:
            player.draw()

        for bullet in self.bullets:
            bullet.draw()

        for bonus in self.bonuses:
            bonus.draw()

        self.level.draw([self.level.TILE_GRASS])

        if self.game_over:
            if self.game_over_y > 188:
                self.game_over_y -= 4
            self.screen.blit(self.im_game_over, [176, self.game_over_y])  # 176=(416-64)/2

        self.drawSidebar()

        pygame.display.flip()

    def toggleEnemyFreeze(self, freeze=True):
        for enemy in self.enemies:
            enemy.paused = freeze
        self.timefreeze = freeze

    def loadHiscore(self):
        filename = ".hiscore"
        if not os.path.isfile(filename):
            return 0

        with open(filename, "r") as f:
            hiscore = int(f.read())

        if hiscore < 1000000:
            return hiscore
        else:
            print("cheater =[")
            return 20000

    def save_hiscore(self, hiscore) -> bool:
        try:
            with open(".hiscore", "w") as f:
                f.write(str(hiscore))
        except FileExistsError or FileNotFoundError:
            print("Can't save hi-score")
            return False
        return True

    def showScores(self):
        """ Show level scores """

        # stop game main loop (if any)
        self.running = False

        # clear all timers
        del self.gtimer.timers[:]

        if self.play_sounds:
            for sound in self.sounds:
                self.sounds[sound].stop()

        hiscore = self.loadHiscore()

        # update hiscore if needed
        if self.players[0].score > hiscore:
            hiscore = self.players[0].score
            self.save_hiscore(hiscore)
        if self.nr_of_players == 2 and self.players[1].score > hiscore:
            hiscore = self.players[1].score
            self.save_hiscore(hiscore)

        img_tanks = [
            self.sprites.subsurface(32 * 2, 0, 13 * 2, 15 * 2),
            self.sprites.subsurface(48 * 2, 0, 13 * 2, 15 * 2),
            self.sprites.subsurface(64 * 2, 0, 13 * 2, 15 * 2),
            self.sprites.subsurface(80 * 2, 0, 13 * 2, 15 * 2)
        ]

        img_arrows = [
            self.sprites.subsurface(81 * 2, 48 * 2, 7 * 2, 7 * 2),
            self.sprites.subsurface(88 * 2, 48 * 2, 7 * 2, 7 * 2)
        ]

        self.screen.fill([0, 0, 0])

        # colors
        black = pygame.Color("black")
        white = pygame.Color("white")
        purple = pygame.Color(127, 64, 64)
        pink = pygame.Color(191, 160, 128)

        self.screen.blit(self.font.render("HI-SCORE", False, purple), [105, 35])
        self.screen.blit(self.font.render(str(hiscore), False, pink), [295, 35])

        self.screen.blit(self.font.render("STAGE" + str(self.stage).rjust(3), False, white), [170, 65])

        self.screen.blit(self.font.render("I-PLAYER", False, purple), [25, 95])

        # player 1 global score
        self.screen.blit(self.font.render(str(self.players[0].score).rjust(8), False, pink), [25, 125])

        if self.nr_of_players == 2:
            self.screen.blit(self.font.render("II-PLAYER", False, purple), [310, 95])

            # player 2 global score
            self.screen.blit(self.font.render(str(self.players[1].score).rjust(8), False, pink), [325, 125])

        # tanks and arrows
        for i in range(4):
            self.screen.blit(img_tanks[i], [226, 160 + (i * 45)])
            self.screen.blit(img_arrows[0], [206, 168 + (i * 45)])
            if self.nr_of_players == 2:
                self.screen.blit(img_arrows[1], [258, 168 + (i * 45)])

        self.screen.blit(self.font.render("TOTAL", False, white), [70, 335])

        # total underline
        pygame.draw.line(self.screen, white, [170, 330], [307, 330], 4)

        pygame.display.flip()

        self.clock.tick(2)

        interval = 5

        # points and kills
        for i in range(4):

            # total specific tanks
            tanks = self.players[0].trophies["enemy" + str(i)]

            for n in range(tanks + 1):
                if n > 0 and self.play_sounds:
                    self.sounds["score"].play()

                # erase previous text
                self.screen.blit(self.font.render(str(n - 1).rjust(2), False, black), [170, 168 + (i * 45)])
                # print new number of enemies
                self.screen.blit(self.font.render(str(n).rjust(2), False, white), [170, 168 + (i * 45)])
                # erase previous text
                self.screen.blit(self.font.render(str((n - 1) * (i + 1) * 100).rjust(4) + " PTS", False, black),
                                 [25, 168 + (i * 45)])
                # print new total points per enemy
                self.screen.blit(self.font.render(str(n * (i + 1) * 100).rjust(4) + " PTS", False, white),
                                 [25, 168 + (i * 45)])
                pygame.display.flip()
                self.clock.tick(interval)

            if self.nr_of_players == 2:
                tanks = self.players[1].trophies["enemy" + str(i)]

                for n in range(tanks + 1):

                    if n > 0 and self.play_sounds:
                        self.sounds["score"].play()

                    self.screen.blit(self.font.render(str(n - 1).rjust(2), False, black), [277, 168 + (i * 45)])
                    self.screen.blit(self.font.render(str(n).rjust(2), False, white), [277, 168 + (i * 45)])

                    self.screen.blit(self.font.render(str((n - 1) * (i + 1) * 100).rjust(4) + " PTS", False, black),
                                     [325, 168 + (i * 45)])
                    self.screen.blit(self.font.render(str(n * (i + 1) * 100).rjust(4) + " PTS", False, white),
                                     [325, 168 + (i * 45)])

                    pygame.display.flip()
                    self.clock.tick(interval)

            self.clock.tick(interval)

        # total tanks
        tanks = sum([i for i in self.players[0].trophies.values()]) - self.players[0].trophies["bonus"]
        self.screen.blit(self.font.render(str(tanks).rjust(2), False, white), [170, 335])
        if self.nr_of_players == 2:
            tanks = sum([i for i in self.players[1].trophies.values()]) - self.players[1].trophies["bonus"]
            self.screen.blit(self.font.render(str(tanks).rjust(2), False, white), [277, 335])

        pygame.display.flip()

        # do nothing for 2 seconds
        self.clock.tick(1)
        self.clock.tick(1)

        if self.game_over:
            self.gameOverScreen()
        else:
            self.nextLevel()

    def gameOverScreen(self):
        """ Show game over screen """

        # stop game main loop (if any)
        self.running = False

        self.screen.fill([0, 0, 0])

        self.writeInBricks("game", [125, 140])
        self.writeInBricks("over", [125, 220])
        pygame.display.flip()

        while 1:
            time_passed = self.clock.tick(50)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.showMenu()
                        return

    def animateIntroScreen(self):

        self.drawIntroScreen(False)
        screen_cp = self.screen.copy()

        self.screen.fill([0, 0, 0])

        y = 416
        while y > 0:
            time_passed = self.clock.tick(50)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        y = 0
                        break

            self.screen.blit(screen_cp, [0, y])
            pygame.display.flip()
            y -= 5

        self.screen.blit(screen_cp, [0, 0])
        pygame.display.flip()

    def drawIntroScreen(self, put_on_surface=True):
        """ Draw intro (menu) screen
        @param put_on_surface If True, flip display after drawing
        @return None
        """
        self.screen.fill([0, 0, 0])

        if pygame.font.get_init():
            hiscore = self.loadHiscore()

            self.screen.blit(self.font.render("HI- " + str(hiscore), True, pygame.Color('white')), [170, 35])

            self.screen.blit(self.font.render("1 PLAYER", True, pygame.Color('white')), [165, 250])
            self.screen.blit(self.font.render("2 PLAYERS", True, pygame.Color('white')), [165, 275])

            self.screen.blit(self.font.render("(c) 1980 1985 NAMCO LTD.", True, pygame.Color('white')), [50, 350])
            self.screen.blit(self.font.render("ALL RIGHTS RESERVED", True, pygame.Color('white')), [85, 380])

        if self.nr_of_players == 1:
            self.screen.blit(self.player_image, [125, 245])
        elif self.nr_of_players == 2:
            self.screen.blit(self.player_image, [125, 270])

        self.writeInBricks("battle", [65, 80])
        self.writeInBricks("city", [129, 160])

        if put_on_surface:
            pygame.display.flip()

    def chunks(self, l, n):
        return [l[i:i + n] for i in range(0, len(l), n)]

    def writeInBricks(self, text, pos):
        """ Write specified text in "brick font"
        Only those letters are available that form words "Battle City" and "Game Over"
        Both lowercase and uppercase are valid input, but output is always uppercase
        Each letter consists of 7x7 bricks which is converted into 49 character long string
        of 1's and 0's which in turn is then converted into hex to save some bytes
        @return None
        """
        bricks = self.sprites.subsurface(56 * 2, 64 * 2, 8 * 2, 8 * 2)
        brick1 = bricks.subsurface((0, 0, 8, 8))
        brick2 = bricks.subsurface((8, 0, 8, 8))
        brick3 = bricks.subsurface((8, 8, 8, 8))
        brick4 = bricks.subsurface((0, 8, 8, 8))

        alphabet = {
            "a": "0071b63c7ff1e3",
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
            "y": "019b3667860c18"
        }

        abs_x, abs_y = pos

        for letter in text.lower():

            binstr = ""
            for h in self.chunks(alphabet[letter], 2):
                binstr += str(bin(int(h, 16)))[2:].rjust(8, "0")
            binstr = binstr[7:]

            x, y = 0, 0
            letter_w = 0
            surf_letter = pygame.Surface((56, 56))
            for j, row in enumerate(self.chunks(binstr, 7)):
                for i, bit in enumerate(row):
                    if bit == "1":
                        if i % 2 == 0 and j % 2 == 0:
                            surf_letter.blit(brick1, [x, y])
                        elif i % 2 == 1 and j % 2 == 0:
                            surf_letter.blit(brick2, [x, y])
                        elif i % 2 == 1 and j % 2 == 1:
                            surf_letter.blit(brick3, [x, y])
                        elif i % 2 == 0 and j % 2 == 1:
                            surf_letter.blit(brick4, [x, y])
                        if x > letter_w:
                            letter_w = x
                    x += 8
                x = 0
                y += 8
            self.screen.blit(surf_letter, [abs_x, abs_y])
            abs_x += letter_w + 16
