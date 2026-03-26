class Item:
    def __init__(self, nome, bonus_atk=0, bonus_hp=0):
        self.nome = nome
        self.bonus_atk = bonus_atk
        self.bonus_hp = bonus_hp

    def usar(self, jogador):
        print(f"Você encontrou: {self.nome}!\n")

        if self.bonus_atk > 0:
            jogador.atk += self.bonus_atk
            print(f"ATK +{self.bonus_atk}")

        if self.bonus_hp > 0:
            jogador.hp += self.bonus_hp
            print(f"HP +{self.bonus_hp}")

        print()