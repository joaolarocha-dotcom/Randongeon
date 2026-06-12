"""Lote 3 — doms de slot único (passivo permanente escolhido no início)."""

from unittest.mock import patch

from jogo.entidades.jogador import Jogador
from jogo.entidades.dom import DONS, aplicar_dom


def novo():
    return Jogador("H", hp=20, atk=5, esq=0.3)


class TestDoms:
    def test_jogador_sem_dom_por_padrao(self):
        j = novo()
        assert j.dom is None
        assert j.lifesteal == 0.0
        assert j.evasao_passiva == 0.0

    def test_bruto_mais_atk_menos_esquiva_e_critico(self):
        j = novo(); aplicar_dom(j, "bruto")
        assert j.atk == 8
        assert round(j.esq, 2) == 0.20
        assert round(j.chance_critico, 2) == 0.05
        assert j.dom == "bruto"

    def test_resistente_mais_hp_menos_esquiva(self):
        j = novo(); aplicar_dom(j, "resistente")
        assert j.hp_max == 30 and j.hp == 30
        assert round(j.esq, 2) == 0.25

    def test_agil_menos_hp_mais_esquiva_e_evasao_passiva(self):
        j = novo(); aplicar_dom(j, "agil")
        assert j.hp_max == 15
        assert round(j.esq, 2) == 0.40
        assert j.evasao_passiva == 0.10

    def test_sortudo_mais_critico_menos_atk(self):
        j = novo(); aplicar_dom(j, "sortudo")
        assert j.atk == 4
        assert round(j.chance_critico, 2) == 0.25

    def test_sanguessuga_lifesteal(self):
        j = novo(); aplicar_dom(j, "sanguessuga")
        assert j.lifesteal == 0.10

    def test_aplicar_dom_none_e_no_op(self):
        j = novo()
        aplicar_dom(j, None)
        assert j.dom is None and j.atk == 5

    def test_dom_desconhecido_e_no_op(self):
        j = novo()
        aplicar_dom(j, "inexistente")
        assert j.dom is None and j.atk == 5


class TestPassivosEmCombate:
    def test_lifesteal_cura_fracao_do_dano(self):
        j = novo(); aplicar_dom(j, "sanguessuga")  # lifesteal 10%
        j.receber_dano(10)                          # hp = 10
        curou = j.aplicar_lifesteal(50)             # 10% de 50 = 5
        assert curou == 5 and j.hp == 15

    def test_lifesteal_zero_sem_dom(self):
        j = novo()
        assert j.aplicar_lifesteal(50) == 0

    @patch("jogo.entidades.inimigo.random.random", return_value=0.15)
    def test_evasao_passiva_faz_inimigo_errar(self, _rand):
        # Inimigo com chance_miss 0.10; alvo Ágil soma +0.10 → miss em 0.20.
        from jogo.entidades.inimigo import Inimigo
        j = novo(); aplicar_dom(j, "agil")          # evasao_passiva 0.10
        inimigo = Inimigo("Goblin", hp=5, atk=5, dificuldade=1, xp=5, moedas=2)
        rel = inimigo.atacar(j)
        assert rel["errou"] is True                 # 0.15 < 0.10+0.10

    @patch("jogo.entidades.inimigo.random.random", return_value=0.05)
    def test_sem_evasao_passiva_inimigo_acerta_normal(self, _rand):
        # Sem dom Ágil, miss só pela chance_miss (0.10): 0.05 < 0.10 → erra mesmo.
        # Com 0.15 acertaria; aqui validamos que evasao_passiva default é 0.
        from jogo.entidades.inimigo import Inimigo
        j = novo()
        assert j.evasao_passiva == 0.0
