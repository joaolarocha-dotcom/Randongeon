# randongeon/conftest.py
#
# v3 — Atualizado para compatibilidade com os novos atributos de Inimigo:
#   - hp_max, modificador_fuga, cura_percentual, absorcao_dano,
#     bonus_atk_por_turno, chance_atordoar, tipo_especial
#
# ATENÇÃO: o fixture inimigo_fraco usa Inimigo.__new__() para contornar a
# validação de atk=0. Todos os novos atributos precisam ser definidos
# manualmente para evitar AttributeError nos testes de combate.

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import pytest

from jogo.entidades.jogador import Jogador
from jogo.entidades.inimigo import Inimigo
from jogo.entidades.item    import Item
from jogo.sistemas.gerador  import GeradorSala
from jogo.sistemas.masmorra import Masmorra


# ── FIXTURES — Jogador ────────────────────────────────────────────────────────

@pytest.fixture
def jogador_padrao() -> Jogador:
    """Jogador com atributos base. hp=20, atk=5, xp=0, esq=0.3, moedas=0."""
    return Jogador("Herói", hp=20, atk=5, xp=0)


@pytest.fixture
def jogador_ferido() -> Jogador:
    """Jogador com hp atual=5 (hp_max=20)."""
    j = Jogador("Ferido", hp=20, atk=5)
    j.hp = 5
    return j


@pytest.fixture
def jogador_quase_morto() -> Jogador:
    """Jogador com hp atual=1 (hp_max=20)."""
    j = Jogador("Quase Morto", hp=20, atk=5)
    j.hp = 1
    return j


@pytest.fixture
def jogador_forte() -> Jogador:
    """Jogador com hp=100, atk=100 — garante vitória nos testes de combate."""
    return Jogador("Campeão", hp=100, atk=100)


@pytest.fixture
def jogador_com_esq() -> Jogador:
    """Jogador com esquiva elevada (esq=0.8)."""
    return Jogador("Esquivador", hp=20, atk=5, esq=0.8)


@pytest.fixture
def jogador_com_moedas() -> Jogador:
    """Jogador com saldo inicial de moedas=50 para testes de economia."""
    return Jogador("Rico", hp=20, atk=5, moedas=50)


# ── FIXTURES — Inimigo ────────────────────────────────────────────────────────

def _set_atributos_especiais(inimigo: Inimigo) -> None:
    """
    Define todos os novos atributos especiais (v3) em instâncias criadas
    via __new__ (que não passam pelo __init__ e não recebem os defaults).
    Centraliza a atualização: se novos atributos forem adicionados,
    basta alterar esta função.
    """
    inimigo.hp_max              = inimigo.hp
    inimigo.modificador_fuga    = 0.0
    inimigo.cura_percentual     = 0.0
    inimigo.absorcao_dano       = 0
    inimigo.bonus_atk_por_turno = 0
    inimigo.chance_atordoar     = 0.0
    inimigo.tipo_especial       = None
    inimigo.chance_miss         = 0.10   # v3.1
    inimigo.chance_drop         = 0.10   # v3.1


@pytest.fixture
def inimigo_padrao() -> Inimigo:
    """Inimigo moderado. hp=10, atk=3, dificuldade=1, xp=15, moedas=5."""
    return Inimigo("Goblin", hp=10, atk=3, dificuldade=1, xp=15, moedas=5)


@pytest.fixture
def inimigo_fraco() -> Inimigo:
    """
    Inimigo com hp=1 e atk=0 — morto em um golpe, não causa dano.
    Criado via __new__ porque atk=0 não passa na validação do __init__.
    Todos os atributos especiais (v3) são definidos manualmente via
    _set_atributos_especiais() para evitar AttributeError no combate.
    """
    i             = Inimigo.__new__(Inimigo)
    i.nome        = "Dummy"
    i.hp          = 1
    i.atk         = 0
    i.dificuldade = 1
    i.xp          = 10
    i.moedas      = 2
    _set_atributos_especiais(i)
    return i


@pytest.fixture
def inimigo_forte() -> Inimigo:
    """Inimigo com hp=999, atk=999 — garante derrota do jogador padrão."""
    return Inimigo("Chefão Supremo", hp=999, atk=999, dificuldade=3, xp=100, moedas=50)


# ── FIXTURES — Item ───────────────────────────────────────────────────────────

@pytest.fixture
def item_cura() -> Item:
    """Item de cura com bonus_hp=5."""
    return Item("Elixir Vital", bonus_hp=5)


@pytest.fixture
def item_ataque() -> Item:
    """Item de ataque com bonus_atk=3."""
    return Item("Poção de Força", bonus_atk=3)


@pytest.fixture
def item_misto() -> Item:
    """Item com bonus_atk=2 e bonus_hp=3 simultaneamente."""
    return Item("Tônico do Guerreiro", bonus_atk=2, bonus_hp=3)


@pytest.fixture
def item_esquiva() -> Item:
    """Item de esquiva com bonus_esq=0.1."""
    return Item("Poção do Mestre Gato", bonus_esq=0.1)


# ── FIXTURES — Sistema ───────────────────────────────────────────────────────

@pytest.fixture
def gerador_padrao() -> GeradorSala:
    """GeradorSala com chance_item=20 (padrão v2)."""
    return GeradorSala()


@pytest.fixture
def masmorra_padrao(jogador_padrao) -> Masmorra:
    """Masmorra com jogador padrão, andar=0."""
    return Masmorra(jogador_padrao)


@pytest.fixture
def masmorra_forte(jogador_forte) -> Masmorra:
    """Masmorra com jogador forte — vitória garantida nos combates."""
    return Masmorra(jogador_forte)