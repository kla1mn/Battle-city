from tank import Tank

class Player(Tank):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.lives = 3
        self.score = 0

    # Дополнительные методы для игрока