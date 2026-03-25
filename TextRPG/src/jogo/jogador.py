import random

class Jogador:
    def __init__(self, vida=20, ataque=5):
        self.vida = vida
        self.ataque = ataque

    def atacar(self, inimigo):
        dano = random.randint(1, self.ataque)
        inimigo.vida -= dano
        return dano