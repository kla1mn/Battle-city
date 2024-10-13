from tank import Tank

class Enemy(Tank):
    def __init__(self, game, x, y, type):
        super().__init__(game, x, y)
        self.type = type

    # Дополнительные методы для врага