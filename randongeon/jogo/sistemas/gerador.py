import random
from jogo.entidades.inimigo import Inimigo
from jogo.entidades.item import Item

class GeradorSala:
    def gerar_sala(self):
        descricoes = [
            "Uma sala escura com cheiro de mofo.",
            "Uma caverna iluminada por cristais.",
            "Um corredor antigo cheio de ossos.",
        ]

        descricao = random.choice(descricoes)
        print(descricao + "\n")

        # 1/5 chance de item
        if random.randint(1, 5) == 1:
            return self.gerar_item()
        else:
            return self.gerar_inimigo()

    def gerar_item(self):
        itens = [
            Item("Poção de Força", bonus_atk=1),
            Item("Grande Poção de Força", bonus_atk=2),
            Item("Elixir Vital", bonus_hp=3),
        ]

        item = random.choice(itens)
        return ("item", item)

    def gerar_inimigo(self):
        inimigo = Inimigo.gerar()
        return ("inimigo", inimigo)