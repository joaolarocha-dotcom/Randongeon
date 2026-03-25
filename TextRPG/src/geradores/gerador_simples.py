import random

from jogo.inimigo import Inimigo
from geradores.gerador_base import GeradorBase

class GeradorSimples(GeradorBase):
    def gerar_sala(self):
        descricoes = [
            "Uma sala escura com cheiro de mofo.",
            "Uma caverna iluminada por cristais.",
            "Um corredor antigo cheio de ossos.",
        ]
        return random.choice(descricoes)

    def gerar_inimigo(self):
        nomes = ["Goblin", "Esqueleto", "Orc"]
        nome = random.choice(nomes)
        vida = random.randint(5, 15)
        ataque = random.randint(2, 6)

        return Inimigo(nome, vida, ataque)