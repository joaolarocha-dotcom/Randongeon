# randongeon/tests/test_levelup_feedback.py
#
# Lote feedback de level-up: a cura ao subir de nível era silenciosa. Agora
# ganhar_xp() devolve quantos níveis subiu, há um texto comemorativo, e
# progresso_nivel() alimenta a barra de XP com a curva REAL (não mais xp/50).

import pytest

from jogo.entidades.jogador import Jogador, mensagem_level_up


class TestGanharXpRetornaNiveis:
    def test_sem_subir_retorna_zero(self):
        j = Jogador("H", hp=20, atk=5)
        assert j.ganhar_xp(5) == 0          # precisa 20 para o nível 2

    def test_sobe_um_nivel(self):
        j = Jogador("H", hp=20, atk=5)
        assert j.ganhar_xp(20) == 1
        assert j.nivel == 2

    def test_sobe_varios_niveis_de_uma_vez(self):
        j = Jogador("H", hp=20, atk=5)
        niveis = j.ganhar_xp(100000)
        assert niveis >= 3
        assert j.nivel == 1 + niveis


class TestProgressoNivel:
    def test_nivel_1_inicio(self):
        j = Jogador("H", hp=20, atk=5)
        assert j.progresso_nivel() == (0, 20)    # 0/20 para o nível 2

    def test_nivel_1_parcial(self):
        j = Jogador("H", hp=20, atk=5)
        j.ganhar_xp(10)
        assert j.progresso_nivel() == (10, 20)

    def test_apos_subir_reinicia_no_novo_nivel(self):
        j = Jogador("H", hp=20, atk=5)
        j.ganhar_xp(20)                          # nível 2 (xp 20)
        atual, total = j.progresso_nivel()
        assert atual == 0                        # 20 - 20 (base do nível 2)
        assert total == 40                       # 60 - 20

    def test_barra_nunca_passa_de_100(self):
        j = Jogador("H", hp=20, atk=5)
        j.ganhar_xp(19)                          # quase no nível 2
        atual, total = j.progresso_nivel()
        assert 0 <= atual <= total


class TestMensagemLevelUp:
    def test_um_nivel_menciona_nivel_e_cura(self):
        msg = mensagem_level_up("Neivinha", 2, 1)
        assert "PARABÉNS" in msg
        assert "nível 2" in msg
        assert "Vida recuperada" in msg

    def test_multiplos_niveis(self):
        msg = mensagem_level_up("Neivinha", 4, 3)
        assert "3 níveis" in msg
        assert "nível 4" in msg
