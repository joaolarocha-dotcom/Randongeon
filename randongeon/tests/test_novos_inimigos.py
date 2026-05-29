import pytest
from unittest.mock import patch
from jogo.entidades.inimigo import (
    Inimigo,
    VampiroDasSombras,
    GolemDePedra,
    CacadorSombrio,
    HordaDeGoblins,
    Banshee
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

class TestVampiroDasSombras:
    def test_fabrica_retorna_instancia_de_inimigo(self):
        assert isinstance(VampiroDasSombras(), Inimigo)
    def test_nome_correto(self):
        assert VampiroDasSombras().nome == "Vampiro das Sombras"
    def test_dificuldade_e_dois(self):
        assert VampiroDasSombras().dificuldade == 2
    def test_tipo_especial_e_vampiro(self):
        assert VampiroDasSombras().tipo_especial == "vampiro"
    def test_cura_percentual_e_vinte_por_cento(self):
        assert VampiroDasSombras().cura_percentual == 0.20
    def test_modificador_fuga_e_negativo(self):
        assert VampiroDasSombras().modificador_fuga < 0.0
    def test_hp_dentro_do_range(self):
        for _ in range(20):
            v = VampiroDasSombras()
            assert 12 <= v.hp <= 18
    def test_hp_max_igual_ao_hp_inicial(self):
        v = VampiroDasSombras()
        assert v.hp_max == v.hp
    def test_atk_dentro_do_range(self):
        for _ in range(20):
            assert 4 <= VampiroDasSombras().atk <= 6
    def test_moedas_positivas(self):
        assert VampiroDasSombras().moedas > 0
    def test_absorcao_dano_e_zero(self):
        assert VampiroDasSombras().absorcao_dano == 0
    def test_chance_atordoar_e_zero(self):
        assert VampiroDasSombras().chance_atordoar == 0.0
    def test_bonus_atk_por_turno_e_zero(self):
        assert VampiroDasSombras().bonus_atk_por_turno == 0

class TestGolemDePedra:
    def test_fabrica_retorna_instancia_de_inimigo(self):
        assert isinstance(GolemDePedra(), Inimigo)
    def test_nome_correto(self):
        assert GolemDePedra().nome == "Golem de Pedra"
    def test_dificuldade_e_dois(self):
        assert GolemDePedra().dificuldade == 2
    def test_tipo_especial_e_golem(self):
        assert GolemDePedra().tipo_especial == "golem"
    def test_absorcao_dano_e_dois(self):
        assert GolemDePedra().absorcao_dano == 2
    def test_absorcao_reduz_dano_recebido(self):
        golem = GolemDePedra()
        golem.hp = 20
        dano = golem.receber_dano(5)
        assert dano == 3
        assert golem.hp == 17
    def test_absorcao_maior_que_dano_resulta_zero(self):
        golem = GolemDePedra()
        hp_antes = golem.hp
        dano = golem.receber_dano(2)
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

class TestCacadorSombrio:
    def test_fabrica_retorna_instancia_de_inimigo(self):
        assert isinstance(CacadorSombrio(), Inimigo)
    def test_nome_correto(self):
        assert CacadorSombrio().nome == "Caçador Sombrio"
    def test_dificuldade_e_dois(self):
        assert CacadorSombrio().dificuldade == 2
    def test_tipo_especial_e_cacador(self):
        assert CacadorSombrio().tipo_especial == "cacador"
    def test_bonus_atk_por_turno_e_um(self):
        assert CacadorSombrio().bonus_atk_por_turno == 1
    def test_hp_baixo_intencional(self):
        for _ in range(20):
            c = CacadorSombrio()
            assert 6 <= c.hp <= 10
    def test_modificador_fuga_e_positivo(self):
        assert CacadorSombrio().modificador_fuga > 0.0
    def test_cura_percentual_e_zero(self):
        assert CacadorSombrio().cura_percentual == 0.0
    def test_absorcao_dano_e_zero(self):
        assert CacadorSombrio().absorcao_dano == 0
    def test_atk_inicial_dentro_do_range(self):
        for _ in range(20):
            assert 3 <= CacadorSombrio().atk <= 5
    def test_moedas_positivas(self):
        assert CacadorSombrio().moedas > 0

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
        v = VampiroDasSombras()
        v.hp_max = 99
        v.hp = 10
        v.curar(5)
        assert v.hp == 15
    def test_curar_nao_ultrapassa_hp_max(self):
        v = VampiroDasSombras()
        hp_max = v.hp_max
        v.hp = hp_max - 2
        v.curar(100)
        assert v.hp == hp_max
    def test_curar_valor_negativo_levanta_value_error(self):
        with pytest.raises(ValueError):
            VampiroDasSombras().curar(-1)
    def test_curar_zero_nao_altera_hp(self):
        v = VampiroDasSombras()
        v.hp_max = 99
        v.hp = 10
        v.curar(0)
        assert v.hp == 10
    def test_hp_max_permanece_fixo_apos_cura(self):
        v = VampiroDasSombras()
        hp_max_antes = v.hp_max
        v.hp = 5
        v.curar(100)
        assert v.hp_max == hp_max_antes

class TestCriarEspecial:
    @pytest.mark.parametrize("tipo,classe_esperada", [
        ("vampiro", VampiroDasSombras),
        ("golem", GolemDePedra),
        ("cacador", CacadorSombrio),
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
    @patch("jogo.entidades.inimigo.random.random", return_value=0.50)
    def test_golem_nao_disponivel_antes_do_andar_8(self, _):
        for _ in range(20):
            i = Inimigo.gerar(andar=7)
            assert getattr(i, "tipo_especial", None) != "golem"
    @patch("jogo.entidades.inimigo.random.choice", return_value=GolemDePedra)
    @patch("jogo.entidades.inimigo.random.random", side_effect=[0.50, 0.10, 0.20])
    def test_golem_disponivel_no_andar_8(self, _rand, _choice):
        inimigo = Inimigo.gerar(andar=8)
        assert getattr(inimigo, "tipo_especial", None) == "golem"
    @patch("jogo.entidades.inimigo.random.choice", return_value=CacadorSombrio)
    @patch("jogo.entidades.inimigo.random.random", side_effect=[0.50, 0.10, 0.20])
    def test_cacador_disponivel_no_andar_10(self, _rand, _choice):
        inimigo = Inimigo.gerar(andar=10)
        assert getattr(inimigo, "tipo_especial", None) == "cacador"
    @patch("jogo.entidades.inimigo.random.choice", return_value=VampiroDasSombras)
    @patch("jogo.entidades.inimigo.random.random", side_effect=[0.50, 0.10, 0.20])
    def test_vampiro_disponivel_no_andar_15(self, _rand, _choice):
        inimigo = Inimigo.gerar(andar=15)
        assert getattr(inimigo, "tipo_especial", None) == "vampiro"
    @patch("jogo.entidades.inimigo.random.choice", return_value=Banshee)
    @patch("jogo.entidades.inimigo.random.random", side_effect=[0.50, 0.10, 0.20])
    def test_banshee_disponivel_no_andar_17(self, _rand, _choice):
        inimigo = Inimigo.gerar(andar=17)
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
        vampiro = VampiroDasSombras()
        m = self._masmorra()
        assert m.tentar_fuga(vampiro) is False
    @patch("jogo.sistemas.masmorra.random.random", return_value=0.55)
    def test_banshee_mais_dificil_fugir(self, _mock):
        banshee = Banshee()
        m = self._masmorra()
        assert m.tentar_fuga(banshee) is False
    @patch("jogo.sistemas.masmorra.random.random", return_value=0.53)
    def test_cacador_ligeiramente_mais_facil_fugir(self, _mock):
        cacador = CacadorSombrio()
        m = self._masmorra()
        assert m.tentar_fuga(cacador) is True
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
        VampiroDasSombras,
        GolemDePedra,
        CacadorSombrio,
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
        v = VampiroDasSombras()
        assert f"{v.hp}/{v.hp_max}" in repr(v)
    def test_inimigo_gerado_via_gerar_tem_hp_max(self):
        for _ in range(30):
            i = Inimigo.gerar(andar=10)
            assert hasattr(i, "hp_max")
            assert i.hp_max == i.hp