import random
from typing import Optional

NOMES_DIFICULDADE_1 = ["Goblin", "Rato Gigante", "Bando de Goblins"]
NOMES_DIFICULDADE_2 = ["Esqueleto Guerreiro", "Orc", "Troll das Cavernas"]

class Inimigo:
    def __init__(
        self,
        nome: str,
        hp: int,
        atk: int,
        dificuldade: int,
        xp: int,
        moedas: int,
        modificador_fuga: float = 0.0,
        cura_percentual: float = 0.0,
        absorcao_dano: int = 0,
        bonus_atk_por_turno: int = 0,
        chance_atordoar: float = 0.0,
        tipo_especial: Optional[str] = None,
        chance_miss: float = 0.10,
        chance_drop: float = 0.10
    ) -> None:
        if not nome or not isinstance(nome, str) or not nome.strip():
            raise ValueError()
        if hp <= 0:
            raise ValueError()
        if atk <= 0:
            raise ValueError()
        if dificuldade < 1:
            raise ValueError()
        if xp < 0:
            raise ValueError()
        if moedas < 0:
            raise ValueError()
        if not (0.0 <= cura_percentual <= 1.0):
            raise ValueError()
        if absorcao_dano < 0:
            raise ValueError()
        if bonus_atk_por_turno < 0:
            raise ValueError()
        if not (0.0 <= chance_atordoar <= 1.0):
            raise ValueError()

        self.nome = nome
        self.hp = hp
        self.hp_max = hp
        self.atk = atk
        self.dificuldade = dificuldade
        self.xp = xp
        self.moedas = moedas
        self.modificador_fuga = modificador_fuga
        self.cura_percentual = cura_percentual
        self.absorcao_dano = absorcao_dano
        self.bonus_atk_por_turno = bonus_atk_por_turno
        self.chance_atordoar = chance_atordoar
        self.tipo_especial = tipo_especial
        self.chance_miss = chance_miss
        self.chance_drop = chance_drop

    def esta_vivo(self) -> bool:
        return self.hp > 0

    def receber_dano(self, dano: int) -> int:
        if dano < 0:
            raise ValueError()
        dano_apos_absorcao = max(0, dano - self.absorcao_dano)
        dano_efetivo = min(dano_apos_absorcao, self.hp)
        self.hp -= dano_efetivo
        return dano_efetivo

    def curar(self, quantidade: int) -> int:
        if quantidade < 0:
            raise ValueError()
        hp_antes = self.hp
        self.hp = min(self.hp_max, self.hp + quantidade)
        return self.hp - hp_antes

    @staticmethod
    def gerar(andar: int = 1) -> "Inimigo":
        if andar < 1:
            raise ValueError()

        if random.random() < 0.10:
            return HordaDeGoblins()

        if andar >= 5 and random.random() < 0.25:
            pool_especiais = []
            if andar >= 8:
                pool_especiais.append(GolemDePedra)
            if andar >= 15:
                pool_especiais.append(Nosferatu)
            if andar >= 17:
                pool_especiais.append(Banshee)

            if pool_especiais and random.random() < 0.40:
                classe_escolhida = random.choice(pool_especiais)
                return classe_escolhida()

            nome = random.choice(NOMES_DIFICULDADE_2)
            hp = random.randint(8, 15)
            atk = random.randint(3, 5)
            xp = random.randint(25, 50)
            moedas = random.randint(5, 10)
            return Inimigo(nome, hp, atk, 2, xp, moedas)

        nome = random.choice(NOMES_DIFICULDADE_1)
        hp = random.randint(3, 8)
        atk = random.randint(1, 3)
        xp = random.randint(10, 20)
        moedas = random.randint(0, 4)
        return Inimigo(nome, hp, atk, 1, xp, moedas)

    def __repr__(self) -> str:
        return (
            f"Inimigo(nome={self.nome!r}, hp={self.hp}/{self.hp_max}, "
            f"atk={self.atk}, dificuldade={self.dificuldade}, xp={self.xp})"
        )

class Nosferatu(Inimigo):
    # Antigo "Vampiro das Sombras" (renomeado no Lote B). Mantém a mecânica de
    # regeneração ao causar dano. Herda de Inimigo e especializa o construtor.
    def __init__(self) -> None:
        super().__init__(
            nome="Nosferatu",
            hp=random.randint(12, 18),
            atk=random.randint(4, 6),
            dificuldade=2,
            xp=45,
            moedas=random.randint(10, 15),
            modificador_fuga=-0.10,
            cura_percentual=0.20,
            tipo_especial="nosferatu",
            chance_miss=0.05,
            chance_drop=0.22
        )

class GolemDePedra(Inimigo):
    def __init__(self) -> None:
        super().__init__(
            nome="Golem de Pedra",
            hp=random.randint(15, 22),
            atk=random.randint(3, 5),
            dificuldade=2,
            xp=50,
            moedas=random.randint(10, 15),
            modificador_fuga=0.40,
            absorcao_dano=2,
            tipo_especial="golem",
            chance_miss=0.10,
            chance_drop=0.20
        )

class HordaDeGoblins(Inimigo):
    def __init__(self) -> None:
        super().__init__(
            nome="Horda de Goblins",
            hp=random.randint(9, 12),
            atk=random.randint(1, 2),
            dificuldade=1,
            xp=20,
            moedas=random.randint(5, 10),
            modificador_fuga=0.20,
            tipo_especial="horda",
            chance_miss=0.20,
            chance_drop=0.12
        )

class Banshee(Inimigo):
    def __init__(self) -> None:
        super().__init__(
            nome="Banshee",
            hp=random.randint(10, 15),
            atk=random.randint(3, 6),
            dificuldade=2,
            xp=55,
            moedas=random.randint(10, 20),
            modificador_fuga=-0.15,
            chance_atordoar=0.30,
            tipo_especial="banshee",
            chance_miss=0.05,
            chance_drop=0.25
        )