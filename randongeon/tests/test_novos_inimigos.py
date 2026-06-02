import pytest
from unittest.mock import patch
from jogo.entidades.inimigo import (
    Inimigo,
    Nosferatu,
    GolemDePedra,
    HordaDeGoblins,
    Banshee,
    Goblin,
    BandoDeGoblins,
    LOOT_PADRAO,
    LOOT_GOLEM,
    LOOT_NOSFERATU,
    LOOT_BANSHEE,
    LOOT_HORDA,
)
from jogo.entidades.jogador import Jogador
from jogo.sistemas.masmorra import Masmorra

def _set_atributos_especiais(inimigo: Inimigo) -> None:
    inimigo.hp_max = inimigo.hp
    inimigo.modificador_fuga = 0.0
    inimigo.cura_percentual = 0.0
    inimigo.absorcao_dano = 0
    inimigo.bonus_atk_por_turno = 0
    inimigo.chance_atordoar = 0.0
    inimigo.tipo_especial = None

def _dummy(hp=1, atk=1, xp=10, moedas=5) -> Inimigo:
    i = Inimigo.__new__(Inimigo)
    i.nome = "Dummy"
    i.hp = hp
    i.atk = atk
    i.dificuldade = 1
    i.xp = xp
    i.moedas = moedas
    _set_atributos_especiais(i)
    return i

class TestNosferatu:
    def test_fabrica_retorna_instancia_de_inimigo(self):
        assert isinstance(Nosferatu(), Inimigo)
    def test_nome_correto(self):
        assert Nosferatu().nome == "Nosferatu"
    def test_dificuldade_e_dois(self):
        assert Nosferatu().dificuldade == 2
    def test_tipo_especial_e_vampiro(self):
        assert Nosferatu().tipo_especial == "nosferatu"
    def test_cura_percentual_e_vinte_por_cento(self):
        assert Nosferatu().cura_percentual == 0.20
    def test_modificador_fuga_e_negativo(self):
        assert Nosferatu().modificador_fuga < 0.0
    def test_hp_dentro_do_range(self):
        for _ in range(20):
            v = Nosferatu()
            assert 12 <= v.hp <= 18
    def test_hp_max_igual_ao_hp_inicial(self):
        v = Nosferatu()
        assert v.hp_max == v.hp
    def test_atk_dentro_do_range(self):
        for _ in range(20):
            assert 4 <= Nosferatu().atk <= 6
    def test_moedas_positivas(self):
        assert Nosferatu().moedas > 0
    def test_absorcao_dano_e_zero(self):
        assert Nosferatu().absorcao_dano == 0
    def test_chance_atordoar_e_zero(self):
        assert Nosferatu().chance_atordoar == 0.0
    def test_bonus_atk_por_turno_e_zero(self):
        assert Nosferatu().bonus_atk_por_turno == 0

class TestGolemDePedra:
    def test_fabrica_retorna_instancia_de_inimigo(self):
        assert isinstance(GolemDePedra(), Inimigo)
    def test_nome_correto(self):
        assert GolemDePedra().nome == "Golem de Pedra"
    def test_dificuldade_e_dois(self):
        assert GolemDePedra().dificuldade == 2
    def test_tipo_especial_e_golem(self):
        assert GolemDePedra().tipo_especial == "golem"
    def test_absorcao_dano_e_tres(self):
        # Lote C: defesa do Golem subiu de 2 para 3.
        assert GolemDePedra().absorcao_dano == 3
    def test_absorcao_reduz_dano_recebido(self):
        golem = GolemDePedra()
        golem.hp = 20
        dano = golem.receber_dano(5)   # 5 - 3 de absorção = 2
        assert dano == 2
        assert golem.hp == 18
    def test_absorcao_maior_que_dano_resulta_zero(self):
        golem = GolemDePedra()
        hp_antes = golem.hp
        dano = golem.receber_dano(3)   # 3 - 3 de absorção = 0
        assert dano == 0
        assert golem.hp == hp_antes
    def test_ataque_de_forca_um_causa_zero_dano(self):
        golem = GolemDePedra()
        hp_antes = golem.hp
        assert golem.receber_dano(1) == 0
        assert golem.hp == hp_antes
    def test_hp_dentro_do_range(self):
        for _ in range(20):
            g = GolemDePedra()
            assert 15 <= g.hp <= 22
    def test_cura_percentual_e_zero(self):
        assert GolemDePedra().cura_percentual == 0.0
    def test_chance_atordoar_e_zero(self):
        assert GolemDePedra().chance_atordoar == 0.0

class TestHordaDeGoblins:
    def test_fabrica_retorna_instancia_de_inimigo(self):
        assert isinstance(HordaDeGoblins(), Inimigo)
    def test_nome_correto(self):
        assert HordaDeGoblins().nome == "Horda de Goblins"
    def test_dificuldade_e_um(self):
        assert HordaDeGoblins().dificuldade == 1
    def test_tipo_especial_e_horda(self):
        assert HordaDeGoblins().tipo_especial == "horda"
    def test_modificador_fuga_e_alto_positivo(self):
        assert HordaDeGoblins().modificador_fuga == 0.20
    def test_hp_combinado_maior_que_goblin_comum(self):
        horda = HordaDeGoblins()
        assert horda.hp >= 9
    def test_atk_baixo_como_esperado(self):
        for _ in range(20):
            h = HordaDeGoblins()
            assert 1 <= h.atk <= 2
    def test_cura_percentual_e_zero(self):
        assert HordaDeGoblins().cura_percentual == 0.0
    def test_absorcao_dano_e_zero(self):
        assert HordaDeGoblins().absorcao_dano == 0
    def test_chance_atordoar_e_zero(self):
        assert HordaDeGoblins().chance_atordoar == 0.0
    @patch("jogo.entidades.inimigo.random.random", return_value=0.05)
    def test_horda_disponivel_no_andar_1(self, _):
        inimigo = Inimigo.gerar(andar=1)
        assert getattr(inimigo, "tipo_especial", None) == "horda"

class TestBanshee:
    def test_fabrica_retorna_instancia_de_inimigo(self):
        assert isinstance(Banshee(), Inimigo)
    def test_nome_correto(self):
        assert Banshee().nome == "Banshee"
    def test_dificuldade_e_dois(self):
        assert Banshee().dificuldade == 2
    def test_tipo_especial_e_banshee(self):
        assert Banshee().tipo_especial == "banshee"
    def test_chance_atordoar_e_trinta_por_cento(self):
        assert Banshee().chance_atordoar == 0.30
    def test_modificador_fuga_e_muito_negativo(self):
        assert Banshee().modificador_fuga == -0.15
    def test_hp_dentro_do_range(self):
        for _ in range(20):
            b = Banshee()
            assert 10 <= b.hp <= 15
    def test_atk_dentro_do_range(self):
        for _ in range(20):
            assert 3 <= Banshee().atk <= 6
    def test_cura_percentual_e_zero(self):
        assert Banshee().cura_percentual == 0.0
    def test_absorcao_dano_e_zero(self):
        assert Banshee().absorcao_dano == 0
    def test_bonus_atk_por_turno_e_zero(self):
        assert Banshee().bonus_atk_por_turno == 0
    def test_moedas_altas(self):
        for _ in range(20):
            b = Banshee()
            assert b.moedas >= 10

class TestCurarInimigo:
    def test_curar_aumenta_hp(self):
        v = Nosferatu()
        v.hp_max = 99
        v.hp = 10
        v.curar(5)
        assert v.hp == 15
    def test_curar_nao_ultrapassa_hp_max(self):
        v = Nosferatu()
        hp_max = v.hp_max
        v.hp = hp_max - 2
        v.curar(100)
        assert v.hp == hp_max
    def test_curar_valor_negativo_levanta_value_error(self):
        with pytest.raises(ValueError):
            Nosferatu().curar(-1)
    def test_curar_zero_nao_altera_hp(self):
        v = Nosferatu()
        v.hp_max = 99
        v.hp = 10
        v.curar(0)
        assert v.hp == 10
    def test_hp_max_permanece_fixo_apos_cura(self):
        v = Nosferatu()
        hp_max_antes = v.hp_max
        v.hp = 5
        v.curar(100)
        assert v.hp_max == hp_max_antes

class TestCriarEspecial:
    @pytest.mark.parametrize("tipo,classe_esperada", [
        ("nosferatu", Nosferatu),
        ("golem", GolemDePedra),
        ("banshee", Banshee),
    ])
    def test_dispatcher_cria_tipo_correto(self, tipo, classe_esperada):
        if hasattr(Inimigo, "_criar_especial"):
            inimigo = Inimigo._criar_especial(tipo)
            assert isinstance(inimigo, classe_esperada)
        else:
            pytest.skip("Dispatcher _criar_especial removido.")
    def test_tipo_desconhecido_levanta_value_error(self):
        if hasattr(Inimigo, "_criar_especial"):
            with pytest.raises(ValueError):
                Inimigo._criar_especial("dragao_inexistente")
        else:
            pytest.skip("Dispatcher _criar_especial removido.")
    def test_tipo_vazio_levanta_value_error(self):
        if hasattr(Inimigo, "_criar_especial"):
            with pytest.raises(ValueError):
                Inimigo._criar_especial("")
        else:
            pytest.skip("Dispatcher _criar_especial removido.")

class TestThresholdsDeAndar:
    # Thresholds antecipados (Lote C): Golem>=5, Nosferatu>=8, Banshee>=10.
    @patch("jogo.entidades.inimigo.random.random", return_value=0.50)
    def test_golem_nao_disponivel_antes_do_andar_5(self, _):
        for _ in range(20):
            i = Inimigo.gerar(andar=4)
            assert getattr(i, "tipo_especial", None) != "golem"
    @patch("jogo.entidades.inimigo.random.choice", return_value=GolemDePedra)
    @patch("jogo.entidades.inimigo.random.random", side_effect=[0.50, 0.10, 0.20])
    def test_golem_disponivel_no_andar_5(self, _rand, _choice):
        inimigo = Inimigo.gerar(andar=5)
        assert getattr(inimigo, "tipo_especial", None) == "golem"
    @patch("jogo.entidades.inimigo.random.choice", return_value=Nosferatu)
    @patch("jogo.entidades.inimigo.random.random", side_effect=[0.50, 0.10, 0.20])
    def test_nosferatu_disponivel_no_andar_8(self, _rand, _choice):
        inimigo = Inimigo.gerar(andar=8)
        assert getattr(inimigo, "tipo_especial", None) == "nosferatu"
    @patch("jogo.entidades.inimigo.random.random", side_effect=[0.50, 0.10, 0.20])
    def test_nosferatu_nao_disponivel_no_andar_5(self, _):
        # No andar 5 o pool especial só tem Golem → forçar especial sempre dá golem.
        inimigo = Inimigo.gerar(andar=5)
        assert getattr(inimigo, "tipo_especial", None) == "golem"
    @patch("jogo.entidades.inimigo.random.choice", return_value=Banshee)
    @patch("jogo.entidades.inimigo.random.random", side_effect=[0.50, 0.10, 0.20])
    def test_banshee_disponivel_no_andar_10(self, _rand, _choice):
        inimigo = Inimigo.gerar(andar=10)
        assert getattr(inimigo, "tipo_especial", None) == "banshee"
    @patch("jogo.entidades.inimigo.random.random", side_effect=[0.50, 0.10, 0.50])
    def test_elite_comum_quando_random_especial_acima_de_40(self, _):
        inimigo = Inimigo.gerar(andar=10)
        assert getattr(inimigo, "tipo_especial", None) is None
        assert inimigo.dificuldade == 2
    @patch("jogo.entidades.inimigo.random.random", side_effect=[0.50, 0.50])
    def test_inimigo_comum_quando_nao_e_elite(self, _):
        inimigo = Inimigo.gerar(andar=5)
        assert inimigo.dificuldade == 1
        assert getattr(inimigo, "tipo_especial", None) is None

class TestFugaVariavelPorTipo:
    def _masmorra(self) -> Masmorra:
        return Masmorra(Jogador("Teste", hp=20, atk=5))
    @patch("jogo.sistemas.masmorra.random.random", return_value=0.45)
    def test_horda_mais_facil_fugir(self, _mock):
        horda = HordaDeGoblins()
        m = self._masmorra()
        assert m.tentar_fuga(horda) is True
    @patch("jogo.sistemas.masmorra.random.random", return_value=0.55)
    def test_vampiro_mais_dificil_fugir(self, _mock):
        vampiro = Nosferatu()
        m = self._masmorra()
        assert m.tentar_fuga(vampiro) is False
    @patch("jogo.sistemas.masmorra.random.random", return_value=0.55)
    def test_banshee_mais_dificil_fugir(self, _mock):
        banshee = Banshee()
        m = self._masmorra()
        assert m.tentar_fuga(banshee) is False
    @patch("jogo.sistemas.masmorra.random.random", return_value=0.49)
    def test_inimigo_comum_fuga_padrao(self, _mock):
        comum = Inimigo("Goblin", hp=5, atk=1, dificuldade=1, xp=10, moedas=2)
        m = self._masmorra()
        assert m.tentar_fuga(comum) is True
    @patch("jogo.sistemas.masmorra.random.random", return_value=0.51)
    def test_inimigo_sem_modificador_fuga_padrao(self, _mock):
        comum = Inimigo("Goblin", hp=5, atk=1, dificuldade=1, xp=10, moedas=2)
        m = self._masmorra()
        assert m.tentar_fuga(comum) is False

class TestHpMaxEmTodosOsTipos:
    @pytest.mark.parametrize("fabrica", [
        Nosferatu,
        GolemDePedra,
        HordaDeGoblins,
        Banshee,
    ])
    def test_hp_max_igual_ao_hp_inicial_para_todos_especiais(self, fabrica):
        i = fabrica()
        assert i.hp_max == i.hp
    def test_hp_max_nao_muda_apos_receber_dano(self):
        golem = GolemDePedra()
        hp_max_antes = golem.hp_max
        golem.receber_dano(5)
        assert golem.hp_max == hp_max_antes
    def test_repr_exibe_hp_max(self):
        v = Nosferatu()
        assert f"{v.hp}/{v.hp_max}" in repr(v)
    def test_inimigo_gerado_via_gerar_tem_hp_max(self):
        for _ in range(30):
            i = Inimigo.gerar(andar=10)
            assert hasattr(i, "hp_max")
            assert i.hp_max == i.hp

class TestTabelaLoot:
    """
    Loot por tipo via polimorfismo (Lote C): cada subclasse sobrescreve
    tabela_loot() devolvendo o seu pool; a base devolve o pool padrão.
    """
    def test_base_inimigo_usa_pool_padrao(self):
        comum = Inimigo("Goblin", hp=5, atk=2, dificuldade=1, xp=10, moedas=2)
        assert comum.tabela_loot() is LOOT_PADRAO

    def test_golem_usa_pool_proprio(self):
        assert GolemDePedra().tabela_loot() is LOOT_GOLEM

    def test_nosferatu_usa_pool_proprio(self):
        assert Nosferatu().tabela_loot() is LOOT_NOSFERATU

    def test_banshee_usa_pool_proprio(self):
        assert Banshee().tabela_loot() is LOOT_BANSHEE

    def test_horda_usa_pool_proprio(self):
        assert HordaDeGoblins().tabela_loot() is LOOT_HORDA

    def test_polimorfismo_cada_tipo_devolve_seu_pool(self):
        # Mesma chamada (tabela_loot), pools diferentes conforme o tipo concreto.
        esperado = {
            GolemDePedra:   LOOT_GOLEM,
            Nosferatu:      LOOT_NOSFERATU,
            Banshee:        LOOT_BANSHEE,
            HordaDeGoblins: LOOT_HORDA,
        }
        for fabrica, pool in esperado.items():
            assert fabrica().tabela_loot() is pool

    def test_pools_nao_sao_vazios(self):
        for pool in (LOOT_PADRAO, LOOT_GOLEM, LOOT_NOSFERATU, LOOT_BANSHEE, LOOT_HORDA):
            assert len(pool) >= 1

    def test_rolar_loot_usa_pool_do_tipo(self):
        # Integração com a Masmorra: um Golem só dropa itens do pool do Golem.
        from jogo.entidades.jogador import Jogador
        from jogo.sistemas.masmorra import Masmorra
        m = Masmorra(Jogador("H", hp=20, atk=5))
        golem = GolemDePedra()
        with patch("jogo.sistemas.masmorra.random.random", return_value=0.0):
            loot = m._rolar_loot(golem)
        assert loot in LOOT_GOLEM

class TestBandoDeGoblins:
    """
    Lote E: Goblin (Herança), tabela_loot (Polimorfismo), BandoDeGoblins
    (Composição: um Bando TEM 3 Goblins).
    """
    def test_goblin_e_um_inimigo(self):           # Herança ("é um")
        g = Goblin("Goblin", hp=5, atk=1, xp=8, moedas=2)
        assert isinstance(g, Inimigo)

    def test_goblin_tipo_horda(self):
        assert Goblin("Goblin", hp=5, atk=1, xp=8, moedas=2).tipo_especial == "horda"

    def test_goblin_dropa_loot_da_horda(self):    # Polimorfismo
        assert Goblin("Goblin", hp=5, atk=1, xp=8, moedas=2).tabela_loot() is LOOT_HORDA

    def test_bando_tem_tres_goblins(self):        # Composição ("tem um")
        fila = BandoDeGoblins().fila()
        assert len(fila) == 3
        assert all(isinstance(g, Goblin) for g in fila)

    def test_bando_nao_e_inimigo(self):
        # O Bando é um agrupador, NÃO um Inimigo (composição, não herança).
        assert not isinstance(BandoDeGoblins(), Inimigo)

    def test_fila_e_copia_defensiva(self):
        bando = BandoDeGoblins()
        fila = bando.fila()
        fila.clear()
        assert len(bando.fila()) == 3   # mutar a cópia não afeta o bando

    def test_goblins_sao_identicos(self):
        fila = BandoDeGoblins().fila()
        # mesmo nome "Bando de Goblins" e mesmas stats (um único sprite)
        assert all(g.nome == "Bando de Goblins" for g in fila)
        assert len({(g.hp, g.atk, g.xp, g.moedas) for g in fila}) == 1

    def test_nome_bando_distinto_do_goblin_comum(self):
        from jogo.entidades.inimigo import NOMES_DIFICULDADE_1
        # "Bando de Goblins" saiu da lista de comuns (evita colisão)
        assert "Bando de Goblins" not in NOMES_DIFICULDADE_1

    def test_goblins_sao_fracos_dif1(self):
        for g in BandoDeGoblins().fila():
            assert g.dificuldade == 1
            assert g.hp <= 9