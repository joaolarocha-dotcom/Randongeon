"""
Configuração global do pytest para o projeto randongeon — v2.

Este arquivo é carregado automaticamente pelo pytest antes de qualquer teste.
Ele garante que o diretório raiz do projeto esteja no sys.path, permitindo
que todos os arquivos de teste importem os módulos do jogo corretamente
sem necessidade de instalação do pacote.

Também define fixtures globais reutilizáveis por qualquer arquivo de teste.
"""

import sys
import os

# ── Configuração de path ──────────────────────────────────────────────────────
# Insere a raiz do projeto (onde está este conftest.py) no início do sys.path.
# Isso permite imports como: from jogo.entidades.jogador import Jogador

sys.path.insert(0, os.path.dirname(__file__))


# ── Imports das entidades (disponíveis para todos os testes) ──────────────────

import pytest

from jogo.entidades.jogador import Jogador
from jogo.entidades.inimigo import Inimigo
from jogo.entidades.item    import Item
from jogo.sistemas.gerador  import GeradorSala
from jogo.sistemas.masmorra import Masmorra


# ══════════════════════════════════════════════════════════════════════════════
# FIXTURES GLOBAIS — Jogador
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def jogador_padrao() -> Jogador:
    """
    Jogador com atributos base para uso geral nos testes.

    Retorna:
        Jogador: hp=20, atk=5, xp=0
    """
    return Jogador("Herói", hp=20, atk=5, xp=0)


@pytest.fixture
def jogador_ferido() -> Jogador:
    """
    Jogador com HP reduzido para testar comportamentos de cura e limite de vida.

    Retorna:
        Jogador: hp_max=20, hp atual=5
    """
    j = Jogador("Ferido", hp=20, atk=5)
    j.hp = 5
    return j


@pytest.fixture
def jogador_quase_morto() -> Jogador:
    """
    Jogador com HP = 1 para testar bordas de morte e sobrevivência.

    Retorna:
        Jogador: hp_max=20, hp atual=1
    """
    j = Jogador("Quase Morto", hp=20, atk=5)
    j.hp = 1
    return j


@pytest.fixture
def jogador_forte() -> Jogador:
    """
    Jogador com atributos elevados para garantir vitória nos testes de combate.

    Retorna:
        Jogador: hp=100, atk=100
    """
    return Jogador("Campeão", hp=100, atk=100)


# ══════════════════════════════════════════════════════════════════════════════
# FIXTURES GLOBAIS — Inimigo
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def inimigo_padrao() -> Inimigo:
    """
    Inimigo com atributos moderados para testes gerais.

    Retorna:
        Inimigo: hp=10, atk=3, dificuldade=1, xp=15
    """
    return Inimigo("Goblin", hp=10, atk=3, dificuldade=1, xp=15)


@pytest.fixture
def inimigo_fraco() -> Inimigo:
    """
    Inimigo com HP=1 e ATK=0 — morto em um golpe, não causa dano.
    Usado para garantir vitória determinística em testes de combate.

    Retorna:
        Inimigo: hp=1, atk=0 (dificuldade 1, xp=10)
    """
    # ATK=0 não passa na validação normal; criamos manualmente
    i = Inimigo.__new__(Inimigo)
    i.nome        = "Dummy"
    i.hp          = 1
    i.atk         = 0
    i.dificuldade = 1
    i.xp          = 10
    return i


@pytest.fixture
def inimigo_forte() -> Inimigo:
    """
    Inimigo com HP e ATK altíssimos — mata jogador padrão em um golpe.
    Usado para garantir derrota determinística em testes de combate.

    Retorna:
        Inimigo: hp=999, atk=999, dificuldade=3, xp=100
    """
    return Inimigo("Chefão Supremo", hp=999, atk=999, dificuldade=3, xp=100)


# ══════════════════════════════════════════════════════════════════════════════
# FIXTURES GLOBAIS — Item
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def item_cura() -> Item:
    """
    Item de cura simples com bonus_hp=5.

    Retorna:
        Item: bonus_hp=5
    """
    return Item("Elixir Vital", bonus_hp=5)


@pytest.fixture
def item_ataque() -> Item:
    """
    Item de equipamento com bonus_atk=3.

    Retorna:
        Item: bonus_atk=3
    """
    return Item("Poção de Força", bonus_atk=3)


@pytest.fixture
def item_misto() -> Item:
    """
    Item com bonus_atk=2 e bonus_hp=3 simultaneamente.

    Retorna:
        Item: bonus_atk=2, bonus_hp=3
    """
    return Item("Tônico do Guerreiro", bonus_atk=2, bonus_hp=3)


# ══════════════════════════════════════════════════════════════════════════════
# FIXTURES GLOBAIS — Sistema
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def gerador_padrao() -> GeradorSala:
    """
    GeradorSala com configuração padrão.

    Retorna:
        GeradorSala: chance_item=5
    """
    return GeradorSala()


@pytest.fixture
def masmorra_padrao(jogador_padrao) -> Masmorra:
    """
    Masmorra inicializada com jogador padrão e gerador padrão.

    Retorna:
        Masmorra: andar=0, jogador padrão
    """
    return Masmorra(jogador_padrao)


@pytest.fixture
def masmorra_forte(jogador_forte) -> Masmorra:
    """
    Masmorra com jogador forte — para testes onde vitória é garantida.

    Retorna:
        Masmorra: jogador com hp=100, atk=100
    """
    return Masmorra(jogador_forte)