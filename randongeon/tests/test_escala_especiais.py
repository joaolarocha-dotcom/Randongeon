# randongeon/tests/test_escala_especiais.py
#
# Lote balance "B" — Escala dos elites ESPECIAIS por andar.
# Antes, Golem/Nosferatu/Banshee nasciam com stats FIXAS e não escalavam, então
# no fim da campanha morriam mais fácil que um comum. Agora recebem bônus de
# HP/ATK por andar (params opcionais, default 0) e o Golem ganha rampa de armadura.

from unittest.mock import patch

import pytest

from jogo.entidades.inimigo import (
    Inimigo,
    GolemDePedra,
    Nosferatu,
    Banshee,
    ESCALA_HP_POR_ANDAR,
    ESCALA_ATK_DIVISOR,
    ESPECIAL_HP_MULTIPLICADOR,
    GOLEM_ARMADURA_PASSO,
)


# ── Params opcionais não quebram as stats base (default 0) ────────────────────

class TestBaseInalterada:
    def test_golem_sem_args_mantem_base(self):
        for _ in range(20):
            g = GolemDePedra()
            assert 15 <= g.hp <= 22
            assert g.absorcao_dano == 3        # base intacta

    def test_nosferatu_sem_args_mantem_base(self):
        for _ in range(20):
            assert 12 <= Nosferatu().hp <= 18

    def test_banshee_sem_args_mantem_base(self):
        for _ in range(20):
            assert 10 <= Banshee().hp <= 15


# ── Params de escala somam corretamente ───────────────────────────────────────

class TestParamsDeEscala:
    def test_golem_bonus_hp_e_armadura(self):
        for _ in range(20):
            g = GolemDePedra(bonus_hp=10, bonus_atk=2, bonus_armadura=2)
            assert 25 <= g.hp <= 32          # 15-22 + 10
            assert 5 <= g.atk <= 7           # 3-5 + 2
            assert g.absorcao_dano == 5      # 3 + 2

    def test_nosferatu_bonus(self):
        for _ in range(20):
            n = Nosferatu(bonus_hp=20, bonus_atk=3)
            assert 32 <= n.hp <= 38          # 12-18 + 20
            assert 7 <= n.atk <= 9           # 4-6 + 3

    def test_banshee_bonus(self):
        for _ in range(20):
            b = Banshee(bonus_hp=20)
            assert 30 <= b.hp <= 35          # 10-15 + 20


# ── Escala aplicada via Inimigo.gerar() por andar ─────────────────────────────

class TestEscalaViaGerar:
    def _forcar_especial(self, andar, classe):
        # side_effect: [horda?, gate elite, ratio especial]; choice → a classe.
        with patch("jogo.entidades.inimigo.random.random",
                   side_effect=[0.50, 0.10, 0.20]), \
             patch("jogo.entidades.inimigo.random.choice", return_value=classe):
            return Inimigo.gerar(andar=andar)

    def test_golem_escala_no_andar_16(self):
        andar = 16
        bonus_hp = round(andar * ESCALA_HP_POR_ANDAR)                 # 29
        bonus_hp_especial = round(bonus_hp * ESPECIAL_HP_MULTIPLICADOR)  # 46
        bonus_atk = andar // ESCALA_ATK_DIVISOR                       # 3
        g = self._forcar_especial(andar, GolemDePedra)
        assert g.tipo_especial == "golem"
        assert (15 + bonus_hp_especial) <= g.hp <= (22 + bonus_hp_especial)
        assert (3 + bonus_atk) <= g.atk <= (5 + bonus_atk)
        assert g.absorcao_dano == 3 + andar // GOLEM_ARMADURA_PASSO   # 5

    def test_especial_no_fim_e_mais_tanque_que_a_base(self):
        # Regressão: um especial gerado no fim da campanha tem MUITO mais HP que
        # a sua versão base (o bug era exatamente não escalar).
        g = self._forcar_especial(20, GolemDePedra)
        assert g.hp > 22                      # acima do teto base do Golem
        n = self._forcar_especial(20, Nosferatu)
        assert n.hp > 18                      # acima do teto base do Nosferatu

    def test_armadura_do_golem_sobe_com_andar(self):
        baixo = self._forcar_especial(6, GolemDePedra)
        alto  = self._forcar_especial(18, GolemDePedra)
        assert alto.absorcao_dano > baixo.absorcao_dano
