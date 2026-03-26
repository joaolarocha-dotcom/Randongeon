import random

class Inimigo:
    def __init__(self, nome, hp, atk, dificuldade, xp):
        self.nome = nome
        self.hp = hp
        self.atk = atk
        self.dificuldade = dificuldade
        self.xp = xp

    @staticmethod
    def gerar():
        nomes = ["Goblin", "Esqueleto", "Orc"]

        # inimigo mais forte (mais raro)
        if random.random() < 0.3:
            dificuldade = 2
            hp = random.randint(5, 8)
            atk = random.randint(3, 4)
            xp = random.randint(20, 40)
        else:
            dificuldade = 1
            hp = random.randint(1, 4)
            atk = random.randint(1, 2)
            xp = random.randint(10, 20)

        nome = random.choice(nomes)

        return Inimigo(nome, hp, atk, dificuldade, xp)