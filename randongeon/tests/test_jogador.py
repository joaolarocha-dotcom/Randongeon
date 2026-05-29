import pytest
from jogo.entidades.jogador import Jogador

class TestCriacaoJogador:
    def test_atributos_iniciais_corretos(self, jogador_padrao):
        assert jogador_padrao.nome   == "Herói"
        assert jogador_padrao.hp     == 20
        assert jogador_padrao.hp_max == 20
        assert jogador_padrao.atk    == 5
        assert jogador_padrao.xp     == 0
        assert jogador_padrao.esq    == 0.3
        assert jogador_padrao.moedas == 0

    def test_hp_inicial_igual_ao_hp_max(self):
        j = Jogador("Novo", hp=30, atk=5)
        assert j.hp == j.hp_max

    def test_criacao_com_xp_inicial(self):
        j = Jogador("Com XP", hp=20, atk=5, xp=50)
        assert j.xp == 50

    def test_criacao_com_esq_customizada(self):
        j = Jogador("Ninja", hp=20, atk=5, esq=0.7)
        assert j.esq == 0.7

    def test_criacao_com_moedas_iniciais(self):
        j = Jogador("Rico", hp=20, atk=5, moedas=100)
        assert j.moedas == 100

    def test_esq_max_e_definido_como_um(self):
        j = Jogador("Teste", hp=20, atk=5)
        assert j.esq_max == 1

    @pytest.mark.parametrize("nome_invalido", ["", None, 123, "  "])
    def test_nome_invalido_levanta_value_error(self, nome_invalido):
        with pytest.raises(ValueError):
            Jogador(nome_invalido, hp=20, atk=5)

    @pytest.mark.parametrize("hp_invalido", [0, -1, -100])
    def test_hp_invalido_levanta_value_error(self, hp_invalido):
        with pytest.raises(ValueError):
            Jogador("Herói", hp=hp_invalido, atk=5)

    @pytest.mark.parametrize("atk_invalido", [0, -1, -10])
    def test_atk_invalido_levanta_value_error(self, atk_invalido):
        with pytest.raises(ValueError):
            Jogador("Herói", hp=20, atk=atk_invalido)

    def test_xp_negativo_levanta_value_error(self):
        with pytest.raises(ValueError):
            Jogador("Herói", hp=20, atk=5, xp=-1)

    def test_esq_negativa_levanta_value_error(self):
        with pytest.raises(ValueError):
            Jogador("Herói", hp=20, atk=5, esq=-0.1)

class TestEstaVivo:
    def test_vivo_quando_hp_maior_que_zero(self, jogador_padrao):
        assert jogador_padrao.esta_vivo() is True

    def test_morto_quando_hp_igual_a_zero(self, jogador_padrao):
        jogador_padrao.hp = 0
        assert jogador_padrao.esta_vivo() is False

    def test_morto_apos_dano_letal(self, jogador_quase_morto):
        jogador_quase_morto.receber_dano(1)
        assert jogador_quase_morto.esta_vivo() is False

    def test_vivo_apos_cura_que_evita_morte(self, jogador_quase_morto):
        jogador_quase_morto.curar(10)
        assert jogador_quase_morto.esta_vivo() is True

class TestReceberDano:
    def test_dano_reduz_hp_corretamente(self, jogador_padrao):
        jogador_padrao.receber_dano(8)
        assert jogador_padrao.hp == 12

    def test_retorna_dano_efetivo_aplicado(self, jogador_padrao):
        assert jogador_padrao.receber_dano(7) == 7

    def test_hp_nao_fica_negativo_com_dano_excessivo(self, jogador_padrao):
        jogador_padrao.receber_dano(9999)
        assert jogador_padrao.hp == 0

    def test_retorno_limitado_ao_hp_disponivel(self, jogador_ferido):
        assert jogador_ferido.receber_dano(9999) == 5

    def test_dano_zero_nao_altera_hp(self, jogador_padrao):
        jogador_padrao.receber_dano(0)
        assert jogador_padrao.hp == 20

    def test_dano_exato_ao_hp_atual_mata_jogador(self, jogador_padrao):
        jogador_padrao.receber_dano(20)
        assert jogador_padrao.hp == 0

    def test_dano_negativo_levanta_value_error(self, jogador_padrao):
        with pytest.raises(ValueError):
            jogador_padrao.receber_dano(-5)

    @pytest.mark.parametrize("dano,hp_esperado", [
        (0, 20), (5, 15), (10, 10), (20, 0), (99, 0),
    ])
    def test_dano_parametrizado(self, jogador_padrao, dano, hp_esperado):
        jogador_padrao.receber_dano(dano)
        assert jogador_padrao.hp == hp_esperado

class TestCurar:
    def test_cura_aumenta_hp(self, jogador_ferido):
        jogador_ferido.curar(10)
        assert jogador_ferido.hp == 15

    def test_retorna_hp_efetivamente_recuperado(self, jogador_ferido):
        assert jogador_ferido.curar(10) == 10

    def test_cura_nao_ultrapassa_hp_maximo(self, jogador_ferido):
        jogador_ferido.curar(9999)
        assert jogador_ferido.hp == jogador_ferido.hp_max

    def test_retorno_limitado_ao_espaco_disponivel(self, jogador_ferido):
        assert jogador_ferido.curar(9999) == 15

    def test_cura_zero_nao_altera_hp(self, jogador_padrao):
        hp_antes = jogador_padrao.hp
        jogador_padrao.curar(0)
        assert jogador_padrao.hp == hp_antes

    def test_cura_zero_retorna_zero(self, jogador_padrao):
        assert jogador_padrao.curar(0) == 0

    def test_cura_em_hp_cheio_retorna_zero(self, jogador_padrao):
        assert jogador_padrao.curar(50) == 0

    def test_cura_negativa_levanta_value_error(self, jogador_padrao):
        with pytest.raises(ValueError):
            jogador_padrao.curar(-1)

    @pytest.mark.parametrize("cura,hp_esperado", [
        (0, 5), (5, 10), (15, 20), (99, 20),
    ])
    def test_cura_parametrizada(self, jogador_ferido, cura, hp_esperado):
        jogador_ferido.curar(cura)
        assert jogador_ferido.hp == hp_esperado

class TestGanharXp:
    def test_xp_acumulado_corretamente(self, jogador_padrao):
        jogador_padrao.ganhar_xp(30)
        assert jogador_padrao.xp == 30

    def test_xp_acumulado_em_multiplas_chamadas(self, jogador_padrao):
        jogador_padrao.ganhar_xp(20)
        jogador_padrao.ganhar_xp(30)
        assert jogador_padrao.xp == 50

    def test_ganhar_xp_zero_nao_altera_xp(self, jogador_padrao):
        jogador_padrao.ganhar_xp(0)
        assert jogador_padrao.xp == 0

    def test_xp_negativo_levanta_value_error(self, jogador_padrao):
        with pytest.raises(ValueError):
            jogador_padrao.ganhar_xp(-10)

    @pytest.mark.parametrize("xp_ganho,xp_esperado", [
        (0, 0), (10, 10), (100, 100), (999, 999),
    ])
    def test_xp_parametrizado(self, jogador_padrao, xp_ganho, xp_esperado):
        jogador_padrao.ganhar_xp(xp_ganho)
        assert jogador_padrao.xp == xp_esperado

class TestSequenciasDeEstado:
    def test_sequencia_dano_e_cura(self, jogador_padrao):
        jogador_padrao.receber_dano(15)
        assert jogador_padrao.hp == 5
        jogador_padrao.curar(8)
        assert jogador_padrao.hp == 13

    def test_multiplos_danos_acumulam(self, jogador_padrao):
        jogador_padrao.receber_dano(5)
        jogador_padrao.receber_dano(5)
        jogador_padrao.receber_dano(5)
        assert jogador_padrao.hp == 5

    def test_cura_apos_dano_excessivo_retorna_ao_maximo(self, jogador_padrao):
        jogador_padrao.receber_dano(18)
        jogador_padrao.curar(9999)
        assert jogador_padrao.hp == jogador_padrao.hp_max

    def test_repr_contem_informacoes_principais(self, jogador_padrao):
        rep = repr(jogador_padrao)
        assert "Herói" in rep
        assert "20"    in rep
        assert "5"     in rep

class TestAumentaEsq:
    def test_aumenta_esq_incrementa_corretamente(self, jogador_padrao):
        esq_antes = jogador_padrao.esq
        jogador_padrao.aumenta_esq(0.1)
        assert round(jogador_padrao.esq, 2) == round(esq_antes + 0.1, 2)

    def test_retorna_ganho_efetivo(self, jogador_padrao):
        ganho = jogador_padrao.aumenta_esq(0.1)
        assert round(ganho, 2) == 0.1

    def test_esq_nao_ultrapassa_esq_max(self, jogador_padrao):
        jogador_padrao.aumenta_esq(9999.0)
        assert jogador_padrao.esq <= jogador_padrao.esq_max

    def test_esq_para_exatamente_em_um(self, jogador_padrao):
        jogador_padrao.aumenta_esq(9999.0)
        assert jogador_padrao.esq == 1.0

    def test_retorno_limitado_ao_espaco_disponivel(self):
        j = Jogador("Quase Max", hp=20, atk=5, esq=0.95)
        ganho = j.aumenta_esq(0.5)
        assert round(ganho, 2) == 0.05

    def test_aumenta_esq_zero_nao_altera_valor(self, jogador_padrao):
        esq_antes = jogador_padrao.esq
        jogador_padrao.aumenta_esq(0)
        assert jogador_padrao.esq == esq_antes

    def test_esq_negativa_levanta_value_error(self, jogador_padrao):
        with pytest.raises(ValueError):
            jogador_padrao.aumenta_esq(-0.1)

    @pytest.mark.parametrize("bonus,esq_inicial,esq_esperada", [
        (0.0, 0.3, 0.3),
        (0.1, 0.3, 0.4),
        (0.5, 0.3, 0.8),
        (0.9, 0.3, 1.0),
        (9.9, 0.3, 1.0),
    ])
    def test_aumenta_esq_parametrizado(self, bonus, esq_inicial, esq_esperada):
        j = Jogador("Teste", hp=20, atk=5, esq=esq_inicial)
        j.aumenta_esq(bonus)
        assert round(j.esq, 2) == esq_esperada

class TestGanharMoedas:
    def test_moedas_acumuladas_corretamente(self, jogador_padrao):
        jogador_padrao.ganhar_moedas(30)
        assert jogador_padrao.moedas == 30

    def test_moedas_acumuladas_em_multiplas_chamadas(self, jogador_padrao):
        jogador_padrao.ganhar_moedas(15)
        jogador_padrao.ganhar_moedas(25)
        assert jogador_padrao.moedas == 40

    def test_ganhar_zero_moedas_nao_altera_total(self, jogador_padrao):
        jogador_padrao.ganhar_moedas(0)
        assert jogador_padrao.moedas == 0

    def test_moedas_negativas_levanta_value_error(self, jogador_padrao):
        with pytest.raises(ValueError):
            jogador_padrao.ganhar_moedas(-10)

    def test_moedas_acumulam_sobre_valor_inicial(self):
        j = Jogador("Rico", hp=20, atk=5, moedas=50)
        j.ganhar_moedas(25)
        assert j.moedas == 75

    @pytest.mark.parametrize("ganho,saldo_esperado", [
        (0, 0), (10, 10), (100, 100), (999, 999),
    ])
    def test_ganhar_moedas_parametrizado(self, jogador_padrao, ganho, saldo_esperado):
        jogador_padrao.ganhar_moedas(ganho)
        assert jogador_padrao.moedas == saldo_esperado

    def test_vitoria_de_combate_concede_moedas(self):
        from jogo.sistemas.masmorra import Masmorra
        from jogo.entidades.inimigo  import Inimigo

        j = Jogador("Lutador", hp=100, atk=50)
        m = Masmorra(j)

        dummy = Inimigo.__new__(Inimigo)
        dummy.nome = "Dummy"
        dummy.hp = 1
        dummy.hp_max = 1
        dummy.atk = 0
        dummy.dificuldade = 1
        dummy.xp = 5
        dummy.moedas = 10
        dummy.modificador_fuga = 0.0
        dummy.cura_percentual = 0.0
        dummy.absorcao_dano = 0
        dummy.bonus_atk_por_turno = 0
        dummy.chance_atordoar = 0.0
        dummy.tipo_especial = None
        dummy.chance_miss = 0.10
        dummy.chance_drop = 0.10

        m.resolver_combate(dummy)
        assert j.moedas == 10