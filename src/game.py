import pygame
import os
import random

from src.castle import Castle
from src.level import Level
from src.player import Player
from src.enemy import Enemy
from src.label import Label
from src.timer import Timer

from src.constants import Direction, Tile, GameSide, TankState


class Game:
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
        self.clock = None

        self.game_over = False
        self.running = True
        self.active = True
        self.time_freeze = False

        self.stage = 0
        self.players_number = 1

        self._initialize_game()

    def _initialize_game(self):
        os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'

        if self.play_sounds:
            pygame.mixer.pre_init(44100, -16, 1, 512)

        pygame.display.set_caption("Battle City")

        size = 480, 416

        self.screen = pygame.display.set_mode(size)

        self.clock = pygame.time.Clock()
        self.sprites = pygame.transform.scale(pygame.image.load("../sprites/sprites.gif"), [192, 224])
        pygame.display.set_icon(self.sprites.subsurface(0, 0, 13 * 2, 13 * 2))
        if self.play_sounds:
            pygame.mixer.init(44100, -16, 1, 512)
            self._load_sounds()

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

    def _load_sounds(self):
        sound_names = ["gamestart", "gameover", "score", "background", "fire", "bonus", "explosion", "brick", "steel"]
        for name in sound_names:
            self.sounds[name] = pygame.mixer.Sound(f"../sounds/{name}.ogg")

    def load_menu(self):
        self.load_intro_screen()

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
                        if self.players_number == 2:
                            self.players_number = 1
                            self.draw_intro_screen()
                    elif event.key == pygame.K_DOWN:
                        if self.players_number == 1:
                            self.players_number = 2
                            self.draw_intro_screen()
                    elif event.key == pygame.K_RETURN:
                        main_loop = False

        self.players.clear()
        self._load_next_level()

    def _load_next_level(self):
        from src.constants import BulletState
        self._clear_game_objects_for_next_level()
        self.stage += 1
        self.level = Level(self, self.stage)
        self.time_freeze = False

        enemies_count_on_level = self._get_enemies_count_by_level()

        self.level.enemies_left = ([0] * enemies_count_on_level[0] +
                                   [1] * enemies_count_on_level[1] +
                                   [2] * enemies_count_on_level[2] +
                                   [3] * enemies_count_on_level[3])
        random.shuffle(self.level.enemies_left)

        if self.play_sounds:
            self.sounds["gamestart"].play()
            self.gtimer.add(4330, lambda: self.sounds["background"].play(-1), 1)

        self._reload_players()

        self.gtimer.add(3000, lambda: self._spawn_enemy())

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
                    self._handle_key_down(event)
                elif event.type == pygame.KEYUP and not self.game_over and self.active:
                    self._handle_key_up(event)

            for player in self.players:
                if player.state == TankState.Alive and not self.game_over and self.active:
                    self._handle_player_movement(player)
                player.update(time_passed)

            for enemy in self.enemies:
                if enemy.state == TankState.Dead and not self.game_over and self.active:
                    self.enemies.remove(enemy)
                    if len(self.level.enemies_left) == 0 and len(self.enemies) == 0:
                        self._finish_level()
                else:
                    enemy.update(time_passed)

            if not self.game_over and self.active:
                for player in self.players:
                    if player.state == TankState.Alive:
                        if player.bonus is not None and player.side == GameSide.Player:
                            self._trigger_bonus(player.bonus, player)
                            player.bonus = None
                    elif player.state == TankState.Dead:
                        self.superpowers = 0
                        player.lives -= 1
                        if player.lives > 0:
                            self._respawn_player(player)
                        else:
                            self._game_over()

            for bullet in self.bullets[:]:
                if bullet.state == BulletState.Removed:
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
                    self._game_over()

            self.gtimer.update(time_passed)
            self.draw()

    def _get_enemies_count_by_level(self):
        from src.constants import ENEMIES_BY_LEVEL

        if self.stage <= 35:
            enemies = ENEMIES_BY_LEVEL[self.stage - 1]
        else:
            enemies = ENEMIES_BY_LEVEL[34]
        return enemies

    def _clear_game_objects_for_next_level(self):
        del self.bullets[:]
        del self.enemies[:]
        del self.bonuses[:]
        self.castle.rebuild()
        del self.gtimer.timers[:]

    def _handle_key_down(self, event):
        if event.key == pygame.K_q:
            quit()
        elif event.key == pygame.K_m:
            self._toggle_sound()

        for player in self.players:
            if player.state == TankState.Alive:
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

    def _handle_key_up(self, event):
        for player in self.players:
            if player.state == TankState.Alive:
                try:
                    index = player.controls.index(event.key)
                except ValueError:
                    pass
                else:
                    if 1 <= index <= 4:
                        player.pressed[index - 1] = False

    def _handle_player_movement(self, player):
        if player.pressed[0]:
            player.move(Direction.Up)
        elif player.pressed[1]:
            player.move(Direction.Right)
        elif player.pressed[2]:
            player.move(Direction.Down)
        elif player.pressed[3]:
            player.move(Direction.Left)

    def _toggle_sound(self):
        self.play_sounds = not self.play_sounds
        if not self.play_sounds:
            pygame.mixer.stop()
        else:
            self.sounds["background"].play(-1)

    def _trigger_bonus(self, bonus, player):
        if self.play_sounds:
            self.sounds["bonus"].play()

        player.trophies["bonus"] += 1
        player.score += 500

        if bonus.bonus == bonus.BONUS_GRENADE:
            for enemy in self.enemies:
                enemy.explode()
        elif bonus.bonus == bonus.BONUS_HELMET:
            self._cover_player_with_shield(player, True, 10000)
        elif bonus.bonus == bonus.BONUS_SHOVEL:
            self.level.build_castle(Tile.Steel)
            self.gtimer.add(10000, lambda: self.level.build_castle(Tile.Brick), 1)
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

    def _cover_player_with_shield(self, player, shield=True, duration=None):
        player.shielded = shield
        if shield:
            player.timer_uuid_shield = self.gtimer.add(100, lambda: player.toggleShieldImage())
        else:
            self.gtimer.destroy(player.timer_uuid_shield)

        if shield and duration is not None:
            self.gtimer.add(duration, lambda: self._cover_player_with_shield(player, False), 1)

    def _spawn_enemy(self):
        if len(self.enemies) >= self.level.max_active_enemies:
            return
        if len(self.level.enemies_left) < 1 or self.time_freeze:
            return
        enemy = Enemy(self, self.level, 1)
        self.enemies.append(enemy)

    def _reload_players(self):
        from src.constants import TILE_SIZE
        if len(self.players) == 0:
            # first player
            x = 8 * TILE_SIZE + (TILE_SIZE * 2 - 26) / 2
            y = 24 * TILE_SIZE + (TILE_SIZE * 2 - 26) / 2

            player = Player(self, self.level, 0, [x, y], Direction.Up, (0, 0, 13 * 2, 13 * 2))
            self.players.append(player)

            # second player
            if self.players_number == 2:
                x = 16 * TILE_SIZE + (TILE_SIZE * 2 - 26) / 2
                y = 24 * TILE_SIZE + (TILE_SIZE * 2 - 26) / 2
                player = Player(self, self.level, 0, [x, y], Direction.Up, (16 * 2, 0, 13 * 2, 13 * 2))
                player.controls = [pygame.K_f, pygame.K_w, pygame.K_d, pygame.K_s, pygame.K_a]
                self.players.append(player)

        for player in self.players:
            player.level = self.level
            self._respawn_player(player, True)

    def _respawn_player(self, player, clear_scores=False):
        player.reset()

        if clear_scores:
            player.trophies = {"bonus": 0, "enemy0": 0, "enemy1": 0, "enemy2": 0, "enemy3": 0}

        self._cover_player_with_shield(player, True, 4000)

    def _game_over(self):
        if self.play_sounds:
            for sound in self.sounds.values():
                sound.stop()
            self.sounds["gameover"].play()

        self.game_over_y = 416 + 40

        self.game_over = True
        self.gtimer.add(3000, lambda: self.showScores(), 1)

    def _finish_level(self):
        if self.play_sounds:
            self.sounds["background"].stop()

        self.active = False
        self.gtimer.add(3000, lambda: self.showScores(), 1)

        print(f"Stage {self.stage} completed")

    def _draw_sidebar(self):
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

        self.level.draw([Tile.Empty, Tile.Brick, Tile.Steel, Tile.Frozen, Tile.Water])

        self.castle.draw()

        for enemy in self.enemies:
            enemy.draw()

        for player in self.players:
            player.draw()

        for label in self.labels:
            label.draw()

        for bullet in self.bullets:
            bullet.draw()

        for bonus in self.bonuses:
            bonus.draw()

        self.level.draw([Tile.Grass])

        if self.game_over:
            if self.game_over_y > 188:
                self.game_over_y -= 4
            self.screen.blit(self.im_game_over, [176, self.game_over_y])  # 176=(416-64)/2

        self._draw_sidebar()

        pygame.display.flip()

    def toggleEnemyFreeze(self, freeze=True):
        for enemy in self.enemies:
            enemy.paused = freeze
        self.time_freeze = freeze

    def load_hiscore(self):
        filename = ".hiscore"
        if not os.path.isfile(filename):
            return 0

        with open(filename, "r") as f:
            hiscore = int(f.read())

        if hiscore < 1000000:
            return hiscore
        else:
            print("u r cheater =[")
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
        self.running = False
        del self.gtimer.timers[:]

        if self.play_sounds:
            for sound in self.sounds:
                self.sounds[sound].stop()

        hiscore = self.load_hiscore()

        # update hiscore if needed
        if self.players[0].score > hiscore:
            hiscore = self.players[0].score
            self.save_hiscore(hiscore)
        if self.players_number == 2 and self.players[1].score > hiscore:
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

        if self.players_number == 2:
            self.screen.blit(self.font.render("II-PLAYER", False, purple), [310, 95])

            # player 2 global score
            self.screen.blit(self.font.render(str(self.players[1].score).rjust(8), False, pink), [325, 125])

        # tanks and arrows
        for i in range(4):
            self.screen.blit(img_tanks[i], [226, 160 + (i * 45)])
            self.screen.blit(img_arrows[0], [206, 168 + (i * 45)])
            if self.players_number == 2:
                self.screen.blit(img_arrows[1], [258, 168 + (i * 45)])

        self.screen.blit(self.font.render("TOTAL", False, white), [70, 335])

        # total underline
        pygame.draw.line(self.screen, white, [170, 330], [307, 330], 4)

        pygame.display.flip()

        self.clock.tick(1)
        self.clock.tick(1)

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

            if self.players_number == 2:
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
        if self.players_number == 2:
            tanks = sum([i for i in self.players[1].trophies.values()]) - self.players[1].trophies["bonus"]
            self.screen.blit(self.font.render(str(tanks).rjust(2), False, white), [277, 335])

        pygame.display.flip()

        self.clock.tick(1)
        self.clock.tick(1)

        if self.game_over:
            self.stage = 0
            self.load_game_over_screen()
        else:
            self._load_next_level()

    def load_game_over_screen(self):
        self.running = False
        self.screen.fill([0, 0, 0])
        self.write_text_in_bricks("game", [125, 140])
        self.write_text_in_bricks("over", [125, 220])
        pygame.display.flip()

        while True:
            self.clock.tick(50)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    quit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.load_menu()
                    return

    def load_intro_screen(self):
        self.draw_intro_screen(False)
        screen_cp = self.screen.copy()
        self.screen.fill([0, 0, 0])
        y = 416
        while y > 0:
            self.clock.tick(50)
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

    def draw_intro_screen(self, put_on_surface=True):
        self.screen.fill([0, 0, 0])

        if pygame.font.get_init():
            hiscore = self.load_hiscore()

            self.screen.blit(self.font.render("HI-" + str(hiscore), True, pygame.Color('white')), [170, 35])

            self.screen.blit(self.font.render("1 PLAYER", True, pygame.Color('white')), [165, 250])
            self.screen.blit(self.font.render("2 PLAYERS", True, pygame.Color('white')), [165, 275])

            self.screen.blit(self.font.render("(c) 1980 1985 NAMCO LTD.", True, pygame.Color('white')), [50, 350])
            self.screen.blit(self.font.render("ALL RIGHTS RESERVED", True, pygame.Color('white')), [85, 380])

        if self.players_number == 1:
            self.screen.blit(self.player_image, [125, 245])
        elif self.players_number == 2:
            self.screen.blit(self.player_image, [125, 270])

        self.write_text_in_bricks("battle", [65, 80])
        self.write_text_in_bricks("city", [129, 160])

        if put_on_surface:
            pygame.display.flip()

    def write_text_in_bricks(self, text, pos):
        from src.constants import ALPHABET
        bricks = self.sprites.subsurface(56 * 2, 64 * 2, 8 * 2, 8 * 2)
        brick1 = bricks.subsurface((0, 0, 8, 8))
        brick2 = bricks.subsurface((8, 0, 8, 8))
        brick3 = bricks.subsurface((8, 8, 8, 8))
        brick4 = bricks.subsurface((0, 8, 8, 8))

        abs_x, abs_y = pos

        for letter in text.lower():
            binstr = ""
            for h in self._get_chunks(ALPHABET[letter], 2):
                binstr += str(bin(int(h, 16)))[2:].rjust(8, "0")
            binstr = binstr[7:]

            x, y = 0, 0
            letter_w = 0
            surf_letter = pygame.Surface((56, 56))
            for j, row in enumerate(self._get_chunks(binstr, 7)):
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

    @staticmethod
    def _get_chunks(l, n):
        return [l[i:i + n] for i in range(0, len(l), n)]
