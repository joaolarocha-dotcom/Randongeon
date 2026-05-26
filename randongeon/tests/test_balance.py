"""
Testes da nova fórmula de balanceamento de bosses e do modo infinite.

Fórmula atual: hp = 18 + (fator * 7), atk = 4 + fator,
onde fator = andar // intervalo_boss.
"""

import pytest

from jogo.entidades.jogador import Jogador
from jogo.sistemas.masmorra import (
    Masmorra,
    BOSS_A_CADA_ANDARES,
    BOSS_A_CADA_ANDARES_INFINITO,
)


@pytest.fixture
def masmorra_story(jogador_padrao) -> Masmorra:
    return Masmorra(jogador_padrao, modo="story")


@pytest.fixture
def masmorra_infinite(jogador_padrao) -> Masmorra:
    return Masmorra(jogador_padrao, modo="infinite")


class TestModoValidacao:
    def test_modo_invalido_levanta_value_error(self, jogador_padrao):
        with pytest.raises(ValueError):
            Masmorra(jogador_padrao, modo="hardcore")

    def test_modo_default_e_story(self, jogador_padrao):
        m = Masmorra(jogador_padrao)
        assert m.modo == "story"


class TestEscalonamentoBoss:
    @pytest.mark.parametrize("andar,hp_esperado,atk_esperado", [
        (5, 25, 5),    # fator 1
        (10, 32, 6),   # fator 2
        (15, 39, 7),   # fator 3
        (20, 46, 8),   # fator 4
    ])
    def test_formula_boss_story(self, masmorra_story, andar, hp_esperado, atk_esperado):
        masmorra_story.andar = andar
        boss = masmorra_story.gerar_boss()
        assert boss.hp == hp_esperado
        assert boss.atk == atk_esperado

    def test_boss_andar_5_n_mata_em_um_golpe_player_padrao(self, masmorra_story):
        masmorra_story.andar = 5
        boss = masmorra_story.gerar_boss()
        # Player padrão (hp=20, atk=5) precisa de ceil(25/5)=5 ataques
        # e sofre 4 * boss.atk(5) = 20 de dano — sem itens, é derrota apertada,
        # mas viável com 1-2 itens iniciais ou cura.
        ataques_para_matar_boss = (boss.hp + masmorra_story.jogador.atk - 1) // masmorra_story.jogador.atk
        dano_total_sofrido = (ataques_para_matar_boss - 1) * boss.atk
        # Sem itens: derrota perto da linha. Com 2 itens iniciais (HP+3, ATK+1), vencível.
        assert ataques_para_matar_boss == 5
        assert dano_total_sofrido == 20


class TestModoInfinite:
    def test_boss_a_cada_3_andares_no_infinite(self, masmorra_infinite):
        for andar in (3, 6, 9, 12):
            masmorra_infinite.andar = andar
            assert masmorra_infinite.e_andar_de_boss() is True

    def test_andares_intermediarios_nao_sao_boss_no_infinite(self, masmorra_infinite):
        for andar in (1, 2, 4, 5, 7, 8, 10, 11):
            masmorra_infinite.andar = andar
            assert masmorra_infinite.e_andar_de_boss() is False

    def test_constante_infinite_e_3(self):
        assert BOSS_A_CADA_ANDARES_INFINITO == 3

    def test_constante_story_continua_5(self):
        assert BOSS_A_CADA_ANDARES == 5
