import random
from typing import Optional

from jogo.entidades.item import Item

NOMES_DIFICULDADE_1 = ["Goblin", "Rato Gigante", "Bando de Goblins"]
NOMES_DIFICULDADE_2 = ["Esqueleto Guerreiro", "Orc", "Troll das Cavernas"]

# ── Pools de loot (Lote C) ────────────────────────────────────────────────────
# Cada tipo de inimigo tem um pool temático. O pool padrão (LOOT_PADRAO) é usado
# por inimigos comuns e bosses. As subclasses sobrescrevem tabela_loot() para
# devolver o seu pool — é polimorfismo: quem rola o loot chama inimigo.tabela_loot()
# sem precisar saber o tipo concreto.
LOOT_PADRAO = [
    Item("Poção Menor de Cura",  bonus_hp=3),
    Item("Erva Medicinal",       bonus_hp=2),
    Item("Fragmento de Cristal", bonus_atk=1),
    Item("Pó de Velocidade",     bonus_esq=0.03),
    Item("Poção de Cura",        bonus_hp=5),
]
LOOT_GOLEM = [
    Item("Fragmento de Pedra", bonus_hp=4),
    Item("Núcleo de Pedra",    bonus_atk=2),
]
LOOT_NOSFERATU = [
    Item("Sangue Vital",     bonus_hp=6),
    Item("Essência Sombria", bonus_atk=2),
]
LOOT_BANSHEE = [
    Item("Eco da Banshee",      bonus_esq=0.08),
    Item("Grito Cristalizado",  bonus_atk=1),
]
LOOT_HORDA = [
    Item("Bolsa de Moedas Goblin", bonus_hp=2),
    Item("Adaga Enferrujada",      bonus_atk=1),
]

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

    def tabela_loot(self) -> list:
        """
        Pool de itens que este inimigo pode dropar.

        Polimorfismo (slide "Polimorfismo"): a base devolve o pool padrão; cada
        subclasse especial SOBRESCREVE este método com o seu pool temático.
        Quem rola o loot chama inimigo.tabela_loot() sem saber o tipo concreto.
        """
        return LOOT_PADRAO

    @staticmethod
    def gerar(andar: int = 1) -> "Inimigo":
        if andar < 1:
            raise ValueError()

        if random.random() < 0.10:
            return HordaDeGoblins()

        if andar >= 5 and random.random() < 0.25:
            # Thresholds antecipados (Lote C): os especiais aparecem mais cedo,
            # quando o herói ainda é vulnerável — validado por simulação, pois só
            # assim as mecânicas (defesa/cura/atordoar) fazem diferença real.
            pool_especiais = []
            if andar >= 5:
                pool_especiais.append(GolemDePedra)
            if andar >= 8:
                pool_especiais.append(Nosferatu)
            if andar >= 10:
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

    def tabela_loot(self) -> list:   # Polimorfismo: sobrescreve o pool padrão
        return LOOT_NOSFERATU

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
            absorcao_dano=3,          # Lote C: defesa maior (era 2)
            tipo_especial="golem",
            chance_miss=0.10,
            chance_drop=0.20
        )

    def tabela_loot(self) -> list:
        return LOOT_GOLEM

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

    def tabela_loot(self) -> list:
        return LOOT_HORDA

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

    def tabela_loot(self) -> list:
        return LOOT_BANSHEE


# ── Bando de Goblins: combate sequencial (Lote E) ─────────────────────────────

class Goblin(Inimigo):
    """
    Um goblin individual de um Bando.

    Herança (slide "Herança"): É UM Inimigo — herda combate, dano, cura etc.,
    e usa super().__init__ para reaproveitar a construção.
    Polimorfismo: sobrescreve tabela_loot() para dropar o pool da horda.
    """
    def __init__(self, nome: str, hp: int, atk: int, xp: int, moedas: int) -> None:
        super().__init__(
            nome=nome,
            hp=hp,
            atk=atk,
            dificuldade=1,
            xp=xp,
            moedas=moedas,
            modificador_fuga=0.20,
            tipo_especial="horda",
            chance_miss=0.15,
            chance_drop=0.12,
        )

    def tabela_loot(self) -> list:
        return LOOT_HORDA


class BandoDeGoblins:
    """
    Um bando enfrentado em sequência (3 goblins IDÊNTICOS, um de cada vez).

    Composição (slide "Composição vs Herança"): um Bando NÃO é um Inimigo —
    ele TEM vários Goblins (relação "tem um"). O combate continua consumindo
    UM Inimigo por vez; a fila de goblins é estado da sessão.

    Os 3 goblins são iguais entre si (mesmo nome, mesmas stats) — no frontend
    usam um único sprite "Goblin". Stats próximas às de um goblin comum.
    """
    TAMANHO = 3

    def __init__(self) -> None:
        # Rola as stats UMA vez e aplica aos 3 → goblins idênticos.
        hp     = random.randint(4, 7)
        atk    = random.randint(1, 2)
        xp     = random.randint(8, 12)
        moedas = random.randint(2, 4)
        self.goblins = [
            Goblin("Goblin", hp=hp, atk=atk, xp=xp, moedas=moedas)
            for _ in range(self.TAMANHO)
        ]

    def fila(self) -> list:
        """Devolve a fila de goblins (cópia), na ordem em que serão enfrentados."""
        return list(self.goblins)