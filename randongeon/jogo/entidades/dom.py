# randongeon/jogo/entidades/dom.py

"""
Doms (Lote 3) — bônus passivo PERMANENTE escolhido no início da run.

Cada dom dá uma vantagem com um trade-off (lado fraco), para criar "builds" sem
acúmulo e sem depender de sorte/itens: o jogador escolhe UM no começo e ele vale
a run inteira.

POO: cada dom é um objeto `Dom` (value object) que sabe se APLICAR a um Jogador.
Quem cria a run só chama `dom.aplicar(jogador)` — não precisa saber os detalhes.
"""


class Dom:
    """Um dom: ajustes de stat na criação + passivos de combate, com trade-off."""

    def __init__(
        self,
        id: str,
        nome: str,
        descricao: str,
        atk: int = 0,
        hp: int = 0,
        esq: float = 0.0,
        crit: float = 0.0,
        lifesteal: float = 0.0,
        evasao_passiva: float = 0.0,
    ) -> None:
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.atk = atk
        self.hp = hp
        self.esq = esq
        self.crit = crit
        self.lifesteal = lifesteal
        self.evasao_passiva = evasao_passiva

    def aplicar(self, jogador) -> None:
        """Aplica os modificadores do dom a um Jogador recém-criado."""
        if self.atk:
            jogador.atk = max(1, jogador.atk + self.atk)
        if self.hp:
            jogador.hp_max = max(1, jogador.hp_max + self.hp)
            jogador.hp = jogador.hp_max
        if self.esq:
            jogador.esq = min(jogador.esq_max, max(0.0, jogador.esq + self.esq))
        if self.crit:
            jogador.chance_critico = max(0.0, jogador.chance_critico + self.crit)
        jogador.lifesteal = self.lifesteal
        jogador.evasao_passiva = self.evasao_passiva
        jogador.dom = self.id


# Registro dos doms disponíveis (números tunáveis — base atk5/hp20/esq0.30/crit0.10).
DONS = {
    "bruto": Dom(
        "bruto", "Bruto",
        "+3 ATK, mas menos esquiva e menos crítico.",
        atk=+3, esq=-0.10, crit=-0.05,
    ),
    "resistente": Dom(
        "resistente", "Resistente",
        "+10 HP máximo, mas um pouco menos de esquiva.",
        hp=+10, esq=-0.05,
    ),
    "agil": Dom(
        "agil", "Ágil",
        "+esquiva e inimigos erram mais, mas menos HP.",
        hp=-5, esq=+0.10, evasao_passiva=0.10,
    ),
    "sortudo": Dom(
        "sortudo", "Sortudo",
        "Muito mais chance de crítico, mas menos dano base.",
        atk=-1, crit=+0.15,
    ),
    "sanguessuga": Dom(
        "sanguessuga", "Sanguessuga",
        "Cura 10% do dano que você causa.",
        lifesteal=0.10,
    ),
}


def aplicar_dom(jogador, dom_id) -> None:
    """Aplica o dom de id `dom_id` ao jogador (no-op se None/desconhecido)."""
    dom = DONS.get(dom_id) if dom_id else None
    if dom is not None:
        dom.aplicar(jogador)
