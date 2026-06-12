import pytest
from unittest.mock import patch
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
        dummy.chance_veneno = 0.0
        dummy.chance_fraqueza = 0.0
        dummy.chance_esquiva_debuff = 0.0
        dummy.esquiva = 0.0

        m.resolver_combate(dummy)
        assert j.moedas == 10

# ── Balance v3.2: Sistema de Nível e Pontuação ────────────────────────────────

class TestNivel:
    """
    Sistema de nível (config I). Custo triangular: XP_BASE_NIVEL * nivel * (nivel+1).
    Ganho por nível: +ATK_POR_NIVEL atk, +HP_POR_NIVEL hp_max, cura total.
    """

    def test_nivel_inicial_e_um(self, jogador_padrao):
        assert jogador_padrao.nivel == 1

    def test_xp_para_proximo_nivel_inicial(self, jogador_padrao):
        # 10 * 1 * 2 = 20
        assert jogador_padrao.xp_para_proximo_nivel() == 20

    def test_sobe_de_nivel_ao_atingir_threshold(self, jogador_padrao):
        jogador_padrao.ganhar_xp(20)
        assert jogador_padrao.nivel == 2

    def test_nao_sobe_com_xp_insuficiente(self, jogador_padrao):
        jogador_padrao.ganhar_xp(19)
        assert jogador_padrao.nivel == 1

    def test_ganho_de_atributos_ao_subir(self, jogador_padrao):
        jogador_padrao.ganhar_xp(20)
        assert jogador_padrao.atk    == 7    # 5 + 2
        assert jogador_padrao.hp_max == 32   # 20 + 12

    def test_cura_parcial_ao_subir(self):
        # Balanceamento: subir de nível cura 60% do HP máx (não mais total).
        j = Jogador("Ferido", hp=20, atk=5)
        j.receber_dano(15)          # hp = 5
        j.ganhar_xp(20)             # sobe para nível 2 (hp_max vira 32)
        assert j.hp == min(j.hp_max, 5 + int(j.hp_max * Jogador.CURA_NIVEL_FRACAO))
        assert j.hp < j.hp_max      # NÃO é mais cura total

    def test_multiplos_niveis_em_uma_chamada(self, jogador_padrao):
        # 60 XP total cruza L2 (20) e L3 (60) de uma vez
        jogador_padrao.ganhar_xp(60)
        assert jogador_padrao.nivel == 3
        assert jogador_padrao.atk   == 9     # 5 + 2*2

    def test_xp_permanece_cumulativo_apos_subir(self, jogador_padrao):
        jogador_padrao.ganhar_xp(25)
        assert jogador_padrao.xp == 25       # XP não é "gasto" ao subir

    def test_esq_respeita_teto_de_nivel(self):
        j = Jogador("Esquivo", hp=20, atk=5, esq=0.599)
        j.ganhar_xp(100000)         # muitos níveis
        assert j.esq <= Jogador.ESQ_MAXIMA

    def test_repr_inclui_nivel(self, jogador_padrao):
        jogador_padrao.ganhar_xp(20)
        assert "nivel=2" in repr(jogador_padrao)


class TestPontuacao:
    """Pontuação = xp + (nivel-1)*50 + moedas. Exposta via @property (só leitura)."""

    def test_pontuacao_inicial_zero(self, jogador_padrao):
        assert jogador_padrao.pontuacao == 0

    def test_pontuacao_considera_xp(self):
        j = Jogador("P", hp=20, atk=5)
        j.ganhar_xp(10)             # xp=10, nivel=1 (precisa 20)
        assert j.pontuacao == 10

    def test_pontuacao_considera_nivel_e_moedas(self, jogador_padrao):
        jogador_padrao.ganhar_xp(20)    # xp=20, nivel=2
        jogador_padrao.ganhar_moedas(5)
        assert jogador_padrao.pontuacao == 20 + 50 + 5

    def test_pontuacao_e_somente_leitura(self, jogador_padrao):
        with pytest.raises(AttributeError):
            jogador_padrao.pontuacao = 999


class TestCritico:
    """Lote crítico: jogador.rolar_dano() devolve (dano, foi_critico)."""

    def test_chance_critico_base(self):
        j = Jogador("H", hp=20, atk=10)
        assert j.chance_critico == Jogador.CHANCE_CRITICO_BASE

    def test_critico_multiplica_dano(self):
        import jogo.entidades.jogador as mod
        j = Jogador("H", hp=20, atk=10)
        with patch.object(mod.random, "random", return_value=0.0):  # garante crítico
            dano, critico = j.rolar_dano()
        assert critico is True
        assert dano == int(10 * Jogador.MULTIPLICADOR_CRITICO)

    def test_sem_critico_dano_normal(self):
        import jogo.entidades.jogador as mod
        j = Jogador("H", hp=20, atk=10)
        with patch.object(mod.random, "random", return_value=0.99):  # sem crítico
            dano, critico = j.rolar_dano()
        assert critico is False
        assert dano == 10

    def test_critico_considera_atk_efetivo(self):
        # Fraqueza reduz o ATK antes do crítico.
        import jogo.entidades.jogador as mod
        from jogo.entidades.efeitos import Fraqueza
        j = Jogador("H", hp=20, atk=10)
        j.aplicar_efeito(Fraqueza(2, reducao=4))   # atk efetivo = 6
        with patch.object(mod.random, "random", return_value=0.0):
            dano, critico = j.rolar_dano()
        assert dano == int(6 * Jogador.MULTIPLICADOR_CRITICO)


class TestVeneno:
    """Lote M: veneno (DoT) — 1 dano/turno, máx VENENO_DURACAO, curado por
    poção de cura ou ao subir de nível. Estado vive no jogador (persiste entre
    andares)."""

    def test_inicia_sem_veneno(self, jogador_padrao):
        assert jogador_padrao.veneno_turnos == 0
        assert jogador_padrao.envenenado is False

    def test_envenenar_define_duracao(self, jogador_padrao):
        jogador_padrao.envenenar()
        assert jogador_padrao.veneno_turnos == Jogador.VENENO_DURACAO
        assert jogador_padrao.envenenado is True

    def test_envenenar_nao_acumula_alem_do_teto(self, jogador_padrao):
        jogador_padrao.envenenar()
        jogador_padrao.tick_veneno()         # 3 → 2
        jogador_padrao.envenenar()           # renova, não soma
        assert jogador_padrao.veneno_turnos == Jogador.VENENO_DURACAO

    def test_tick_causa_um_de_dano_e_decrementa(self, jogador_padrao):
        jogador_padrao.envenenar()
        dano = jogador_padrao.tick_veneno()
        assert dano == 1
        assert jogador_padrao.hp == 19
        assert jogador_padrao.veneno_turnos == Jogador.VENENO_DURACAO - 1

    def test_tick_sem_veneno_nao_faz_nada(self, jogador_padrao):
        dano = jogador_padrao.tick_veneno()
        assert dano == 0
        assert jogador_padrao.hp == 20

    def test_veneno_dura_no_maximo_tres_turnos(self, jogador_padrao):
        jogador_padrao.envenenar()
        total = sum(jogador_padrao.tick_veneno() for _ in range(10))
        assert total == Jogador.VENENO_DURACAO    # só 3 ticks causaram dano
        assert jogador_padrao.envenenado is False

    def test_curar_veneno_remove(self, jogador_padrao):
        jogador_padrao.envenenar()
        jogador_padrao.curar_veneno()
        assert jogador_padrao.veneno_turnos == 0

    def test_subir_de_nivel_purga_veneno(self, jogador_padrao):
        jogador_padrao.envenenar()
        jogador_padrao.ganhar_xp(jogador_padrao.xp_para_proximo_nivel())
        assert jogador_padrao.nivel == 2
        assert jogador_padrao.veneno_turnos == 0

    def test_pocao_de_cura_purga_veneno(self):
        from jogo.entidades.item import Item
        j = Jogador("Envenenado", hp=20, atk=5)
        j.receber_dano(8)
        j.envenenar()
        Item("Poção de Cura", bonus_hp=5).usar(j)
        assert j.veneno_turnos == 0

    def test_envenenar_negativo_levanta_value_error(self, jogador_padrao):
        with pytest.raises(ValueError):
            jogador_padrao.envenenar(-1)