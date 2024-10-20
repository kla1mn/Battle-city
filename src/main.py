from src.castle import Castle
from src.game import Game
from src.timer import Timer

if __name__ == "__main__":
    gtimer = Timer()

    sprites = None
    screen = None
    players = []
    enemies = []
    bullets = []
    bonuses = []
    labels = []

    play_sounds = True
    sounds = {}

    game = Game()
    castle = Castle()
    game.showMenu()
