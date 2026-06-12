"""
randongeon/tests/test_masmorra.py

Lote 1 — correções:
  - dummy_inimigo(): adicionados todos os atributos especiais v3
    (absorcao_dano, chance_miss, chance_drop, etc.) — corrige 12 AttributeError.
  - TestGerarBoss.test_nome_boss_contem_nome_tematico: assertiva corrigida
    para "Arauto das Sombras" (boss do andar 5 no v3).
  - Fórmulas boss: XP = 80 + fator*40, moedas = 25 + fator*8.
  - self.andar inicia em 0 (não 1).
  - resolver_combate() retorna str ('vitoria'/'derrota'), não dict.
  - GeradorSala importado de jogo.sistemas.gerador.
  - NOMES_BOSS importado de jogo.sistemas.masmorra (agora constante de módulo).
"""

import pytest

from jogo.entidades.inimigo import Inimigo
from jogo.entidades.item    import Item
from jogo.entidades.jogador import Jogador
from jogo.sistemas.gerador  import GeradorSala
from jogo.sistemas.masmorra import (
    BOSS_A_CADA_ANDARES,
    CHANCE_MISS_JOGADOR,
    NOMES_BOSS,
    POOL_LOOT,
    Masmorra,
)


# ══════════════════════════════════════════════════════════════════════════════
# HELPER LOCAL
# ══════════════════════════════════════════════════════════════════════════════

def dummy_inimigo(
    hp: int = 1,
    atk: int = 0,
    xp: int = 10,
    moedas: int = 5,
    dificuldade: int = 1,
) -> Inimigo:
    """
    Cria Inimigo mínimo via __new__ para uso nos testes deste módulo.
    FIX Lote 1: todos os atributos especiais v3 inicializados para evitar
    AttributeError em resolver_combate, _rolar_loot, tentar_fuga, etc.
    """
    i             = Inimigo.__new__(Inimigo)
    i.nome        = "Dummy"
    i.hp          = hp
    i.atk         = atk
    i.dificuldade = dificuldade
    i.xp          = xp
    i.moedas      = moedas
    # ── v3: atributos obrigatórios ───────────────────────────────────────────
    i.hp_max              = hp
    i.modificador_fuga    = 0.0
    i.cura_percentual     = 0.0
    i.absorcao_dano       = 0
    i.bonus_atk_por_turno = 0
    i.chance_atordoar     = 0.0
    i.tipo_especial       = None
    i.chance_miss            = 0.10
    i.chance_drop            = 0.10
    i.chance_veneno          = 0.0
    i.chance_fraqueza        = 0.0
    i.chance_esquiva_debuff  = 0.0
    i.esquiva                = 0.0
    return i


# ══════════════════════════════════════════════════════════════════════════════
# TestMasmorra — atributos iniciais
# ══════════════════════════════════════════════════════════════════════════════

class TestMasmorra:

    def test_inicia_no_andar_0(self, masmorra_padrao):
        assert masmorra_padrao.andar == 0

    def test_tem_jogador(self, masmorra_padrao, jogador_padrao):
        assert masmorra_padrao.jogador is jogador_padrao

    def test_andar_max_padrao_none(self, masmorra_padrao):
        assert masmorra_padrao.andar_max is None

    def test_campanha_define_andar_max(self, jogador_padrao):
        m = Masmorra(jogador_padrao, andar_max=20)
        assert m.andar_max == 20

    def test_andar_max_qualquer_valor(self, jogador_padrao):
        m = Masmorra(jogador_padrao, andar_max=10)
        assert m.andar_max == 10

    def test_andar_max_preservado_apos_incremento(self, jogador_padrao):
        m = Masmorra(jogador_padrao, andar_max=20)
        m.andar += 1
        assert m.andar_max == 20

    def test_desistiu_inicia_false(self, masmorra_padrao):
        assert masmorra_padrao.desistiu is False

    def test_gerador_inicializado(self, masmorra_padrao):
        assert masmorra_padrao.gerador is not None
        assert isinstance(masmorra_padrao.gerador, GeradorSala)

    def test_gerador_customizado(self, jogador_padrao):
        gerador = GeradorSala()
        m = Masmorra(jogador_padrao, gerador=gerador)
        assert m.gerador is gerador


# ══════════════════════════════════════════════════════════════════════════════
# TestEAndarDeBoss
# ══════════════════════════════════════════════════════════════════════════════

class TestEAndarDeBoss:

    def test_andar_0_nao_e_boss(self, masmorra_padrao):
        assert masmorra_padrao.e_andar_de_boss() is False

    def test_andar_1_nao_e_boss(self, masmorra_padrao):
        masmorra_padrao.andar = 1
        assert masmorra_padrao.e_andar_de_boss() is False

    def test_andar_3_nao_e_boss(self, masmorra_padrao):
        masmorra_padrao.andar = 3
        assert masmorra_padrao.e_andar_de_boss() is False

    def test_andar_5_e_boss(self, masmorra_padrao):
        masmorra_padrao.andar = 5
        assert masmorra_padrao.e_andar_de_boss() is True

    def test_andar_10_e_boss(self, masmorra_padrao):
        masmorra_padrao.andar = 10
        assert masmorra_padrao.e_andar_de_boss() is True

    def test_andar_15_e_boss(self, masmorra_padrao):
        masmorra_padrao.andar = 15
        assert masmorra_padrao.e_andar_de_boss() is True

    def test_andar_20_e_boss(self, masmorra_padrao):
        masmorra_padrao.andar = 20
        assert masmorra_padrao.e_andar_de_boss() is True

    @pytest.mark.parametrize("andar", [5, 10, 15, 20, 25, 30])
    def test_multiplos_de_5_sao_boss(self, masmorra_padrao, andar):
        masmorra_padrao.andar = andar
        assert masmorra_padrao.e_andar_de_boss() is True

    @pytest.mark.parametrize("andar", [1, 2, 3, 4, 6, 7, 8, 9, 11])
    def test_nao_multiplos_de_5_nao_sao_boss(self, masmorra_padrao, andar):
        masmorra_padrao.andar = andar
        assert masmorra_padrao.e_andar_de_boss() is False


# ══════════════════════════════════════════════════════════════════════════════
# TestGerarBoss — balance patch v3
# ══════════════════════════════════════════════════════════════════════════════

class TestGerarBoss:
    """
    Fórmulas v3.2 / config I (fator = andar // 5):
      HP     = 20 + fator * 20   →  5/10/15/20: 40/60/80/100
      ATK    =  5 + fator *  3   →  5/10/15/20: 8/11/14/17
      XP     = 80 + fator * 40   →  5/10/15/20: 120/160/200/240  (inalterado)
      moedas = 25 + fator *  8   →  5/10/15/20: 33/41/49/57      (inalterado)
    """

    def test_retorna_inimigo(self, masmorra_padrao):
        masmorra_padrao.andar = 5
        assert isinstance(masmorra_padrao.gerar_boss(), Inimigo)

    def test_dificuldade_sempre_3(self, masmorra_padrao):
        for andar in [5, 10, 15, 20]:
            masmorra_padrao.andar = andar
            assert masmorra_padrao.gerar_boss().dificuldade == 3

    # ── Andar 5 (fator=1) ─────────────────────────────────────────────────

    def test_boss_andar5_hp(self, masmorra_padrao):
        masmorra_padrao.andar = 5
        assert masmorra_padrao.gerar_boss().hp == 40

    def test_boss_andar5_atk(self, masmorra_padrao):
        masmorra_padrao.andar = 5
        assert masmorra_padrao.gerar_boss().atk == 6   # recalibração C: era 8

    def test_boss_andar5_xp(self, masmorra_padrao):
        masmorra_padrao.andar = 5
        assert masmorra_padrao.gerar_boss().xp == 120   # 80 + 1*40

    def test_boss_andar5_moedas(self, masmorra_padrao):
        masmorra_padrao.andar = 5
        assert masmorra_padrao.gerar_boss().moedas == 33  # 25 + 1*8

    def test_nome_boss_contem_nome_tematico(self, masmorra_padrao):
        """
        FIX Lote 1: o boss do andar 5 tem nome temático "Arauto das Sombras",
        não uma string contendo o dígito '5'.
        """
        masmorra_padrao.andar = 5
        assert masmorra_padrao.gerar_boss().nome == "Arauto das Sombras"

    # ── Andar 10 (fator=2) ────────────────────────────────────────────────

    def test_boss_andar10_hp(self, masmorra_padrao):
        masmorra_padrao.andar = 10
        assert masmorra_padrao.gerar_boss().hp == 60

    def test_boss_andar10_atk(self, masmorra_padrao):
        masmorra_padrao.andar = 10
        assert masmorra_padrao.gerar_boss().atk == 10   # recalibração C: era 11

    def test_boss_andar10_xp(self, masmorra_padrao):
        masmorra_padrao.andar = 10
        assert masmorra_padrao.gerar_boss().xp == 160   # 80 + 2*40

    def test_boss_andar10_moedas(self, masmorra_padrao):
        masmorra_padrao.andar = 10
        assert masmorra_padrao.gerar_boss().moedas == 41  # 25 + 2*8

    def test_boss_andar10_nome(self, masmorra_padrao):
        masmorra_padrao.andar = 10
        assert masmorra_padrao.gerar_boss().nome == "Senhor dos Corredores"

    # ── Andar 15 (fator=3) ────────────────────────────────────────────────

    def test_boss_andar15_hp(self, masmorra_padrao):
        masmorra_padrao.andar = 15
        assert masmorra_padrao.gerar_boss().hp == 80

    def test_boss_andar15_atk(self, masmorra_padrao):
        masmorra_padrao.andar = 15
        assert masmorra_padrao.gerar_boss().atk == 13   # recalibração C: era 14

    def test_boss_andar15_xp(self, masmorra_padrao):
        masmorra_padrao.andar = 15
        assert masmorra_padrao.gerar_boss().xp == 200   # 80 + 3*40

    def test_boss_andar15_moedas(self, masmorra_padrao):
        masmorra_padrao.andar = 15
        assert masmorra_padrao.gerar_boss().moedas == 49  # 25 + 3*8

    def test_boss_andar15_nome(self, masmorra_padrao):
        masmorra_padrao.andar = 15
        assert masmorra_padrao.gerar_boss().nome == "Ceifador Eterno"

    # ── Andar 20 (fator=4) ────────────────────────────────────────────────

    def test_boss_andar20_hp(self, masmorra_padrao):
        masmorra_padrao.andar = 20
        assert masmorra_padrao.gerar_boss().hp == 100

    def test_boss_andar20_atk(self, masmorra_padrao):
        masmorra_padrao.andar = 20
        assert masmorra_padrao.gerar_boss().atk == 17

    def test_boss_andar20_xp(self, masmorra_padrao):
        masmorra_padrao.andar = 20
        assert masmorra_padrao.gerar_boss().xp == 240   # 80 + 4*40

    def test_boss_andar20_moedas(self, masmorra_padrao):
        masmorra_padrao.andar = 20
        assert masmorra_padrao.gerar_boss().moedas == 57  # 25 + 4*8

    def test_boss_andar20_nome(self, masmorra_padrao):
        masmorra_padrao.andar = 20
        assert masmorra_padrao.gerar_boss().nome == "Coração da Masmorra"

    # ── Fallback ──────────────────────────────────────────────────────────

    def test_boss_andar_sem_nome_tematico_usa_fallback(self, masmorra_padrao):
        masmorra_padrao.andar = 25
        nome = masmorra_padrao.gerar_boss().nome
        assert isinstance(nome, str) and len(nome) > 0
        assert "25" in nome  # fallback: "Guardião do Andar 25"

    def test_boss_mesmo_andar_nome_consistente(self, masmorra_padrao):
        masmorra_padrao.andar = 5
        nomes = {masmorra_padrao.gerar_boss().nome for _ in range(10)}
        assert nomes == {"Arauto das Sombras"}


# ══════════════════════════════════════════════════════════════════════════════
# TestGerarMimico
# ══════════════════════════════════════════════════════════════════════════════

class TestGerarMimico:

    def test_hp_14(self, masmorra_padrao):
        assert masmorra_padrao.gerar_mimico().hp == 14

    def test_atk_4(self, masmorra_padrao):
        assert masmorra_padrao.gerar_mimico().atk == 4

    def test_dificuldade_2(self, masmorra_padrao):
        assert masmorra_padrao.gerar_mimico().dificuldade == 2

    def test_retorna_inimigo(self, masmorra_padrao):
        assert isinstance(masmorra_padrao.gerar_mimico(), Inimigo)

    def test_xp_positivo(self, masmorra_padrao):
        assert masmorra_padrao.gerar_mimico().xp > 0

    def test_nome_mimico(self, masmorra_padrao):
        assert masmorra_padrao.gerar_mimico().nome == "Mímico"


# ══════════════════════════════════════════════════════════════════════════════
# TestTentarFuga
# ══════════════════════════════════════════════════════════════════════════════

class TestTentarFuga:

    def test_retorna_bool(self, masmorra_padrao):
        assert isinstance(masmorra_padrao.tentar_fuga(), bool)

    def test_retorna_bool_com_inimigo(self, masmorra_padrao):
        assert isinstance(masmorra_padrao.tentar_fuga(dummy_inimigo()), bool)

    def test_fuga_falha_random_alto(self, masmorra_padrao, monkeypatch):
        monkeypatch.setattr("random.random", lambda: 0.99)
        assert masmorra_padrao.tentar_fuga(dummy_inimigo()) is False

    def test_fuga_sucesso_random_baixo(self, masmorra_padrao, monkeypatch):
        monkeypatch.setattr("random.random", lambda: 0.01)
        assert masmorra_padrao.tentar_fuga(dummy_inimigo()) is True

    def test_sem_inimigo_usa_chance_base(self, masmorra_padrao, monkeypatch):
        monkeypatch.setattr("random.random", lambda: 0.49)
        assert masmorra_padrao.tentar_fuga() is True

    def test_sem_inimigo_falha_acima_de_50(self, masmorra_padrao, monkeypatch):
        monkeypatch.setattr("random.random", lambda: 0.51)
        assert masmorra_padrao.tentar_fuga() is False

    def test_modificador_positivo_aumenta_chance(self, masmorra_padrao, monkeypatch):
        monkeypatch.setattr("random.random", lambda: 0.69)
        i = dummy_inimigo()
        i.modificador_fuga = 0.20   # chance = 0.70
        assert masmorra_padrao.tentar_fuga(i) is True

    def test_modificador_negativo_reduz_chance(self, masmorra_padrao, monkeypatch):
        monkeypatch.setattr("random.random", lambda: 0.36)
        i = dummy_inimigo()
        i.modificador_fuga = -0.15   # chance = 0.35
        assert masmorra_padrao.tentar_fuga(i) is False

    def test_clamp_minimo_5_porcento(self, masmorra_padrao):
        i = dummy_inimigo()
        i.modificador_fuga = -99.0
        resultados = [masmorra_padrao.tentar_fuga(i) for _ in range(1000)]
        assert any(resultados)   # mínimo 5% → pelo menos algum sucesso

    def test_clamp_maximo_90_porcento(self, masmorra_padrao, monkeypatch):
        monkeypatch.setattr("random.random", lambda: 0.89)
        i = dummy_inimigo()
        i.modificador_fuga = 99.0   # clampado em 0.90
        assert masmorra_padrao.tentar_fuga(i) is True


# ══════════════════════════════════════════════════════════════════════════════
# TestRolarLoot
# ══════════════════════════════════════════════════════════════════════════════

class TestRolarLoot:

    def test_boss_dropa_abaixo_50(self, masmorra_padrao, monkeypatch):
        monkeypatch.setattr("random.random", lambda: 0.49)
        boss = dummy_inimigo(dificuldade=3)
        assert masmorra_padrao._rolar_loot(boss) is not None

    def test_boss_nao_dropa_acima_50(self, masmorra_padrao, monkeypatch):
        monkeypatch.setattr("random.random", lambda: 0.51)
        boss = dummy_inimigo(dificuldade=3)
        assert masmorra_padrao._rolar_loot(boss) is None

    def test_comum_usa_chance_drop_do_inimigo(self, masmorra_padrao, monkeypatch):
        """chance_drop=0.10 do dummy_inimigo: drop se random < 0.10."""
        monkeypatch.setattr("random.random", lambda: 0.09)
        i = dummy_inimigo()   # chance_drop=0.10
        assert masmorra_padrao._rolar_loot(i) is not None

    def test_comum_nao_dropa_acima_chance_drop(self, masmorra_padrao, monkeypatch):
        monkeypatch.setattr("random.random", lambda: 0.11)
        i = dummy_inimigo()   # chance_drop=0.10
        assert masmorra_padrao._rolar_loot(i) is None

    def test_loot_pertence_ao_pool(self, masmorra_padrao, monkeypatch):
        monkeypatch.setattr("random.random", lambda: 0.0)
        boss = dummy_inimigo(dificuldade=3)
        loot = masmorra_padrao._rolar_loot(boss)
        assert loot in POOL_LOOT

    def test_retorna_none_ou_item(self, masmorra_padrao):
        for _ in range(50):
            resultado = masmorra_padrao._rolar_loot(dummy_inimigo())
            assert resultado is None or isinstance(resultado, Item)


# ══════════════════════════════════════════════════════════════════════════════
# TestAplicarItem
# ══════════════════════════════════════════════════════════════════════════════

class TestAplicarItem:

    def test_aplica_bonus_hp(self, masmorra_padrao):
        hp_antes = masmorra_padrao.jogador.hp
        masmorra_padrao.aplicar_item(Item("Cura", bonus_hp=5))
        assert masmorra_padrao.jogador.hp >= hp_antes

    def test_aplica_bonus_atk(self, masmorra_padrao):
        atk_antes = masmorra_padrao.jogador.atk
        masmorra_padrao.aplicar_item(Item("Espada", bonus_atk=2))
        assert masmorra_padrao.jogador.atk == atk_antes + 2

    def test_aplica_bonus_esq(self, masmorra_padrao):
        esq_antes = masmorra_padrao.jogador.esq
        masmorra_padrao.aplicar_item(Item("Escudo", bonus_esq=0.05))
        assert masmorra_padrao.jogador.esq > esq_antes

    def test_levanta_value_error_para_none(self, masmorra_padrao):
        with pytest.raises(ValueError):
            masmorra_padrao.aplicar_item(None)

    def test_retorna_dict(self, masmorra_padrao):
        resultado = masmorra_padrao.aplicar_item(Item("Item", bonus_hp=1))
        assert isinstance(resultado, dict)


# ══════════════════════════════════════════════════════════════════════════════
# TestResolverCombate — modo terminal (retorna str, não dict)
# ══════════════════════════════════════════════════════════════════════════════

class TestResolverCombate:

    def test_levanta_value_error_para_none(self, masmorra_padrao):
        with pytest.raises(ValueError):
            masmorra_padrao.resolver_combate(None)

    def test_vitoria_quando_inimigo_morre(self, masmorra_forte):
        """Jogador forte (atk=100) derrota inimigo fraco em 1 turno."""
        inimigo = dummy_inimigo(hp=1, atk=0)
        assert masmorra_forte.resolver_combate(inimigo) == "vitoria"

    def test_derrota_quando_jogador_morre(self, masmorra_padrao):
        """Jogador padrão (hp=20, atk=5) perde para inimigo muito forte."""
        masmorra_padrao.jogador.hp = 1
        inimigo = dummy_inimigo(hp=9999, atk=999)
        inimigo.chance_miss = 0.0   # inimigo nunca erra
        assert masmorra_padrao.resolver_combate(inimigo) == "derrota"

    def test_retorna_string(self, masmorra_forte):
        resultado = masmorra_forte.resolver_combate(dummy_inimigo(hp=1, atk=0))
        assert isinstance(resultado, str)

    def test_resultado_e_vitoria_ou_derrota(self, masmorra_forte):
        resultado = masmorra_forte.resolver_combate(dummy_inimigo(hp=1, atk=0))
        assert resultado in ("vitoria", "derrota")

    def test_vitoria_concede_xp(self, masmorra_forte):
        xp_antes = masmorra_forte.jogador.xp
        masmorra_forte.resolver_combate(dummy_inimigo(hp=1, atk=0, xp=25))
        assert masmorra_forte.jogador.xp > xp_antes

    def test_vitoria_concede_moedas(self, masmorra_forte):
        moedas_antes = masmorra_forte.jogador.moedas
        masmorra_forte.resolver_combate(dummy_inimigo(hp=1, atk=0, moedas=10))
        assert masmorra_forte.jogador.moedas > moedas_antes

    def test_derrota_nao_concede_xp(self, masmorra_padrao):
        masmorra_padrao.jogador.hp = 1
        xp_antes = masmorra_padrao.jogador.xp
        inimigo = dummy_inimigo(hp=9999, atk=999)
        inimigo.chance_miss = 0.0
        masmorra_padrao.resolver_combate(inimigo)
        assert masmorra_padrao.jogador.xp == xp_antes


# ══════════════════════════════════════════════════════════════════════════════
# TestConstantes
# ══════════════════════════════════════════════════════════════════════════════

class TestConstantes:

    def test_pool_loot_tem_5_itens(self):
        assert len(POOL_LOOT) == 5

    def test_pool_loot_sao_items(self):
        for item in POOL_LOOT:
            assert isinstance(item, Item)

    def test_chance_miss_jogador(self):
        assert CHANCE_MISS_JOGADOR == 0.10

    def test_boss_a_cada_5_andares(self):
        assert BOSS_A_CADA_ANDARES == 5

    def test_nomes_boss_tem_4_entradas(self):
        assert len(NOMES_BOSS) == 4

    def test_nomes_boss_andar5(self):
        assert NOMES_BOSS[5] == "Arauto das Sombras"

    def test_nomes_boss_andar10(self):
        assert NOMES_BOSS[10] == "Senhor dos Corredores"

    def test_nomes_boss_andar15(self):
        assert NOMES_BOSS[15] == "Ceifador Eterno"

    def test_nomes_boss_andar20(self):
        assert NOMES_BOSS[20] == "Coração da Masmorra"

    def test_pool_loot_tem_item_com_bonus_hp(self):
        assert any(getattr(i, 'bonus_hp', 0) > 0 for i in POOL_LOOT)

    def test_pool_loot_tem_item_com_bonus_atk(self):
        assert any(getattr(i, 'bonus_atk', 0) > 0 for i in POOL_LOOT)


# ══════════════════════════════════════════════════════════════════════════════
# TestModoCampanha — atributo andar_max
# ══════════════════════════════════════════════════════════════════════════════

class TestModoCampanha:

    def test_modo_infinito_andar_max_none(self, masmorra_padrao):
        assert masmorra_padrao.andar_max is None

    def test_modo_campanha_andar_max_20(self, jogador_padrao):
        m = Masmorra(jogador_padrao, andar_max=20)
        assert m.andar_max == 20

    def test_andar_max_nao_afeta_andar_inicial(self, jogador_padrao):
        m = Masmorra(jogador_padrao, andar_max=20)
        assert m.andar == 0

    def test_andar_max_nao_afeta_gerador(self, jogador_padrao):
        m = Masmorra(jogador_padrao, andar_max=20)
        assert isinstance(m.gerador, GeradorSala)

class TestCalcularScore:
    """Lote H: score da run = jogador.pontuacao + andar * 100."""

    def test_score_inicial_e_zero(self, jogador_padrao):
        m = Masmorra(jogador_padrao)              # andar 0, pontuacao 0
        assert m.calcular_score() == 0

    def test_score_combina_pontuacao_e_andar(self, jogador_padrao):
        m = Masmorra(jogador_padrao)
        m.andar = 7
        jogador_padrao.ganhar_moedas(30)
        assert m.calcular_score() == jogador_padrao.pontuacao + 700

    def test_andar_mais_fundo_da_score_maior(self, jogador_padrao):
        m = Masmorra(jogador_padrao)
        m.andar = 3
        score_raso = m.calcular_score()
        m.andar = 12
        assert m.calcular_score() > score_raso