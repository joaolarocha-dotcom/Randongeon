import random

class Inimigo:
    def __init__(self, nome, vida, ataque):
        self.nome = nome
        self.vida = vida
        self.ataque = ataque

    def atacar(self, jogador):
        dano = random.randint(1, self.ataque)
        jogador.vida -= dano
        return dano