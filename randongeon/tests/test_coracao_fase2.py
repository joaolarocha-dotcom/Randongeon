# randongeon/tests/test_coracao_fase2.py
#
# Lote 4 — Boss de 2ª fase: o Coração da Masmorra renasce uma única vez ao morrer
# (cura 50% do HP máx + fúria de ATK). Cobre o modelo (CoracaoDaMasmorra), a
# geração do boss final (gerar_boss) e o caminho CLI (resolver_combate).

import pytest

from jogo.entidades.inimigo import (
    Inimigo,
    CoracaoDaMasmorra,
    CORACAO_CURA_RENASCIMENTO,
    CORACAO_FURIA_ATK_MULT,
)
from jogo.sistemas.masmorra import Masmorra


# ── Hook base (Template Method / Polimorfismo) ────────────────────────────────

class TestHookRenascimentoBase:
    def test_inimigo_comum_nao_renasce(self, inimigo_padrao):
        """A base devolve False — inimigos comuns morrem de vez."""
        inimigo_padrao.hp = 0
        assert inimigo_padrao.tentar_renascer() is False


# ── Geração do boss final ─────────────────────────────────────────────────────

class TestGerarBossFinal:
    def _masmorra_no_andar_final(self) -> Masmorra:
        from jogo.entidades.jogador import Jogador
        m = Masmorra(Jogador("Herói", hp=20, atk=5), modo="story")
        m.andar = 20
        return m

    def test_boss_andar_20_e_coracao(self):
        boss = self._masmorra_no_andar_final().gerar_boss()
        assert isinstance(boss, CoracaoDaMasmorra)
        assert isinstance(boss, Inimigo)          # continua sendo um Inimigo

    def test_boss_final_mantem_stats_travadas(self):
        """A subclasse não pode mudar as stats travadas por teste do andar 20."""
        boss = self._masmorra_no_andar_final().gerar_boss()
        assert boss.nome == "Coração da Masmorra"
        assert boss.hp == 100 and boss.hp_max == 100
        assert boss.atk == 17
        assert boss.dificuldade == 3

    def test_boss_intermediario_nao_renasce(self):
        from jogo.entidades.jogador import Jogador
        m = Masmorra(Jogador("Herói", hp=20, atk=5), modo="story")
        m.andar = 5
        boss = m.gerar_boss()
        assert not isinstance(boss, CoracaoDaMasmorra)
        boss.hp = 0
        assert boss.tentar_renascer() is False


# ── Mecânica de renascimento ──────────────────────────────────────────────────

class TestRenascimento:
    def test_nao_renasce_se_ainda_vivo(self):
        boss = CoracaoDaMasmorra(hp=100, atk=17, xp=240, moedas=57)
        assert boss.tentar_renascer() is False      # vivo → não ressuscita
        assert boss.ja_renasceu is False

    def test_primeira_morte_renasce_a_50_porcento(self):
        boss = CoracaoDaMasmorra(hp=100, atk=17, xp=240, moedas=57)
        boss.hp = 0
        assert boss.tentar_renascer() is True
        assert boss.ja_renasceu is True
        assert boss.hp == round(boss.hp_max * CORACAO_CURA_RENASCIMENTO)   # 50

    def test_renascimento_entra_em_furia(self):
        boss = CoracaoDaMasmorra(hp=100, atk=17, xp=240, moedas=57)
        atk_antes = boss.atk
        boss.hp = 0
        boss.tentar_renascer()
        esperado = max(atk_antes + 1, round(atk_antes * CORACAO_FURIA_ATK_MULT))
        assert boss.atk == esperado
        assert boss.atk > atk_antes

    def test_segunda_morte_nao_renasce(self):
        boss = CoracaoDaMasmorra(hp=100, atk=17, xp=240, moedas=57)
        boss.hp = 0
        assert boss.tentar_renascer() is True       # 1ª morte
        boss.hp = 0
        assert boss.tentar_renascer() is False      # 2ª morte → fim


# ── Caminho CLI (resolver_combate) ────────────────────────────────────────────

class TestResolverCombateCLI:
    def test_vencer_coracao_passa_pela_2a_fase(self, jogador_forte, capsys):
        """O jogador forte vence, mas só depois de o Coração ter renascido 1x."""
        m = Masmorra(jogador_forte, modo="story")
        boss = CoracaoDaMasmorra(hp=10, atk=1, xp=50, moedas=10)
        resultado = m.resolver_combate(boss)
        assert resultado == "vitoria"
        assert boss.ja_renasceu is True             # passou pela 2ª fase
