# randongeon/tests/test_jogador.py

"""
Suíte de testes unitários para jogo/entidades/jogador.py

Cobre:
  - Criação e validação de atributos
  - Sistema de vida: receber_dano() e curar()
  - Estado: esta_vivo()
  - Progressão: ganhar_xp()
  - Representação: __repr__()

Execute com:
    pytest tests/test_jogador.py -v
    pytest tests/test_jogador.py -v --tb=short
"""

import pytest
from jogo.entidades.jogador import Jogador


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 1 — Criação e validação do __init__
# ══════════════════════════════════════════════════════════════════════════════

class TestCriacaoJogador:
    """Testa a criação de instâncias de Jogador e validação dos parâmetros."""

    def test_atributos_iniciais_corretos(self, jogador_padrao):
        """Caminho feliz: todos os atributos devem ser definidos corretamente."""
        assert jogador_padrao.nome   == "Herói"
        assert jogador_padrao.hp     == 20
        assert jogador_padrao.hp_max == 20
        assert jogador_padrao.atk    == 5
        assert jogador_padrao.xp     == 0

    def test_hp_inicial_igual_ao_hp_max(self):
        """hp e hp_max devem ser iguais no momento da criação."""
        j = Jogador("Novo", hp=30, atk=5)
        assert j.hp == j.hp_max

    def test_criacao_com_xp_inicial(self):
        """Deve aceitar xp inicial >= 0."""
        j = Jogador("Com XP", hp=20, atk=5, xp=50)
        assert j.xp == 50

    @pytest.mark.parametrize("nome_invalido", [
        "",          # string vazia
        None,        # None
        123,         # tipo errado
        "  ",        # só espaços — falha no 'not nome'
    ])
    def test_nome_invalido_levanta_value_error(self, nome_invalido):
        """Exceção: nome inválido deve lançar ValueError."""
        with pytest.raises(ValueError):
            Jogador(nome_invalido, hp=20, atk=5)

    @pytest.mark.parametrize("hp_invalido", [0, -1, -100])
    def test_hp_invalido_levanta_value_error(self, hp_invalido):
        """Exceção: hp <= 0 deve lançar ValueError."""
        with pytest.raises(ValueError):
            Jogador("Herói", hp=hp_invalido, atk=5)

    @pytest.mark.parametrize("atk_invalido", [0, -1, -10])
    def test_atk_invalido_levanta_value_error(self, atk_invalido):
        """Exceção: atk <= 0 deve lançar ValueError."""
        with pytest.raises(ValueError):
            Jogador("Herói", hp=20, atk=atk_invalido)

    def test_xp_negativo_levanta_value_error(self):
        """Exceção: xp inicial negativo deve lançar ValueError."""
        with pytest.raises(ValueError):
            Jogador("Herói", hp=20, atk=5, xp=-1)


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 2 — esta_vivo()
# ══════════════════════════════════════════════════════════════════════════════

class TestEstaVivo:
    """Testa o estado de vida do jogador."""

    def test_vivo_quando_hp_maior_que_zero(self, jogador_padrao):
        """Caminho feliz: jogador com hp > 0 deve estar vivo."""
        assert jogador_padrao.esta_vivo() is True

    def test_morto_quando_hp_igual_a_zero(self, jogador_padrao):
        """Exceção de estado: hp = 0 deve retornar False."""
        jogador_padrao.hp = 0
        assert jogador_padrao.esta_vivo() is False

    def test_morto_apos_dano_letal(self, jogador_quase_morto):
        """Jogador com hp=1 deve morrer ao receber qualquer dano."""
        jogador_quase_morto.receber_dano(1)
        assert jogador_quase_morto.esta_vivo() is False

    def test_vivo_apos_cura_que_evita_morte(self, jogador_quase_morto):
        """Jogador curado antes de morrer deve permanecer vivo."""
        jogador_quase_morto.curar(10)
        assert jogador_quase_morto.esta_vivo() is True


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 3 — receber_dano()
# ══════════════════════════════════════════════════════════════════════════════

class TestReceberDano:
    """Testa a aplicação de dano ao jogador."""

    def test_dano_reduz_hp_corretamente(self, jogador_padrao):
        """Caminho feliz: dano deve ser subtraído do hp atual."""
        jogador_padrao.receber_dano(8)
        assert jogador_padrao.hp == 12

    def test_retorna_dano_efetivo_aplicado(self, jogador_padrao):
        """Caminho feliz: retorno deve ser o dano efetivamente sofrido."""
        dano_efetivo = jogador_padrao.receber_dano(7)
        assert dano_efetivo == 7

    def test_hp_nao_fica_negativo_com_dano_excessivo(self, jogador_padrao):
        """Limite: hp deve parar em 0, nunca ir abaixo."""
        jogador_padrao.receber_dano(9999)
        assert jogador_padrao.hp == 0

    def test_retorno_limitado_ao_hp_disponivel(self, jogador_ferido):
        """Limite: dano efetivo não pode ser maior que o hp atual."""
        dano_efetivo = jogador_ferido.receber_dano(9999)
        assert dano_efetivo == jogador_ferido.hp_max - (jogador_ferido.hp_max - 5)
        # hp era 5, então dano efetivo máximo é 5
        assert dano_efetivo == 5

    def test_dano_zero_nao_altera_hp(self, jogador_padrao):
        """Borda: dano zero não deve alterar o hp."""
        jogador_padrao.receber_dano(0)
        assert jogador_padrao.hp == 20

    def test_dano_exato_ao_hp_atual_mata_jogador(self, jogador_padrao):
        """Borda: dano exatamente igual ao hp deve levar a hp=0."""
        jogador_padrao.receber_dano(20)
        assert jogador_padrao.hp == 0

    def test_dano_negativo_levanta_value_error(self, jogador_padrao):
        """Exceção: dano negativo deve lançar ValueError."""
        with pytest.raises(ValueError):
            jogador_padrao.receber_dano(-5)

    @pytest.mark.parametrize("dano,hp_esperado", [
        (0,  20),
        (5,  15),
        (10, 10),
        (20,  0),
        (99,  0),
    ])
    def test_dano_parametrizado(self, jogador_padrao, dano, hp_esperado):
        """Parametrizado: verifica hp resultante para diferentes valores de dano."""
        jogador_padrao.receber_dano(dano)
        assert jogador_padrao.hp == hp_esperado


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 4 — curar()
# ══════════════════════════════════════════════════════════════════════════════

class TestCurar:
    """Testa a restauração de HP do jogador."""

    def test_cura_aumenta_hp(self, jogador_ferido):
        """Caminho feliz: cura deve aumentar o hp do jogador."""
        jogador_ferido.curar(10)
        assert jogador_ferido.hp == 15

    def test_retorna_hp_efetivamente_recuperado(self, jogador_ferido):
        """Caminho feliz: retorno deve ser o HP efetivamente curado."""
        recuperado = jogador_ferido.curar(10)
        assert recuperado == 10

    def test_cura_nao_ultrapassa_hp_maximo(self, jogador_ferido):
        """Limite: cura em excesso não deve ultrapassar hp_max."""
        jogador_ferido.curar(9999)
        assert jogador_ferido.hp == jogador_ferido.hp_max

    def test_retorno_limitado_ao_espaco_disponivel(self, jogador_ferido):
        """Limite: retorno reflete apenas o espaço disponível de hp."""
        # hp=5, hp_max=20 — espaço disponível é 15
        recuperado = jogador_ferido.curar(9999)
        assert recuperado == 15

    def test_cura_zero_nao_altera_hp(self, jogador_padrao):
        """Borda: curar(0) não deve alterar o hp."""
        hp_antes = jogador_padrao.hp
        jogador_padrao.curar(0)
        assert jogador_padrao.hp == hp_antes

    def test_cura_zero_retorna_zero(self, jogador_padrao):
        """Borda: curar(0) deve retornar 0."""
        assert jogador_padrao.curar(0) == 0

    def test_cura_em_hp_cheio_retorna_zero(self, jogador_padrao):
        """Borda: curar jogador com hp cheio não deve alterar nada."""
        recuperado = jogador_padrao.curar(50)
        assert recuperado == 0
        assert jogador_padrao.hp == jogador_padrao.hp_max

    def test_cura_negativa_levanta_value_error(self, jogador_padrao):
        """Exceção: quantidade negativa deve lançar ValueError."""
        with pytest.raises(ValueError):
            jogador_padrao.curar(-1)

    @pytest.mark.parametrize("cura,hp_esperado", [
        (0,  5),
        (5,  10),
        (15, 20),
        (99, 20),  # limitado ao hp_max=20
    ])
    def test_cura_parametrizada(self, jogador_ferido, cura, hp_esperado):
        """Parametrizado: verifica hp resultante para diferentes valores de cura."""
        # jogador_ferido tem hp=5, hp_max=20
        jogador_ferido.curar(cura)
        assert jogador_ferido.hp == hp_esperado


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 5 — ganhar_xp()
# ══════════════════════════════════════════════════════════════════════════════

class TestGanharXp:
    """Testa o ganho de experiência do jogador."""

    def test_xp_acumulado_corretamente(self, jogador_padrao):
        """Caminho feliz: xp deve ser somado ao acumulado atual."""
        jogador_padrao.ganhar_xp(30)
        assert jogador_padrao.xp == 30

    def test_xp_acumulado_em_multiplas_chamadas(self, jogador_padrao):
        """Caminho feliz: xp deve acumular em chamadas sucessivas."""
        jogador_padrao.ganhar_xp(20)
        jogador_padrao.ganhar_xp(30)
        assert jogador_padrao.xp == 50

    def test_ganhar_xp_zero_nao_altera_xp(self, jogador_padrao):
        """Borda: ganhar 0 xp não deve alterar o xp atual."""
        jogador_padrao.ganhar_xp(0)
        assert jogador_padrao.xp == 0

    def test_xp_negativo_levanta_value_error(self, jogador_padrao):
        """Exceção: xp negativo deve lançar ValueError."""
        with pytest.raises(ValueError):
            jogador_padrao.ganhar_xp(-10)

    @pytest.mark.parametrize("xp_ganho,xp_esperado", [
        (0,   0),
        (10,  10),
        (100, 100),
        (999, 999),
    ])
    def test_xp_parametrizado(self, jogador_padrao, xp_ganho, xp_esperado):
        """Parametrizado: verifica xp acumulado para diferentes ganhos."""
        jogador_padrao.ganhar_xp(xp_ganho)
        assert jogador_padrao.xp == xp_esperado


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 6 — Sequências de estado (testes de integração da entidade)
# ══════════════════════════════════════════════════════════════════════════════

class TestSequenciasDeEstado:
    """
    Testa sequências de operações que refletem situações reais do jogo.
    Valida que os métodos interagem corretamente entre si.
    """

    def test_sequencia_dano_e_cura(self, jogador_padrao):
        """Jogador recebe dano e depois é curado parcialmente."""
        jogador_padrao.receber_dano(15)   # hp: 20 → 5
        assert jogador_padrao.hp == 5
        jogador_padrao.curar(8)            # hp: 5 → 13
        assert jogador_padrao.hp == 13
        assert jogador_padrao.esta_vivo() is True

    def test_sequencia_dano_letal_e_xp(self, jogador_padrao):
        """Jogador morto não deve poder ganhar xp (xp é independente, mas hp=0)."""
        jogador_padrao.receber_dano(9999)
        assert jogador_padrao.esta_vivo() is False
        # ganhar_xp não depende de estar vivo — é responsabilidade do combate
        jogador_padrao.ganhar_xp(50)
        assert jogador_padrao.xp == 50  # xp acumula mesmo após morte

    def test_multiplos_danos_acumulam(self, jogador_padrao):
        """Danos consecutivos devem se acumular corretamente."""
        jogador_padrao.receber_dano(5)
        jogador_padrao.receber_dano(5)
        jogador_padrao.receber_dano(5)
        assert jogador_padrao.hp == 5

    def test_cura_apos_dano_excessivo_retorna_ao_maximo(self, jogador_padrao):
        """Jogador que recebeu dano pode ser curado de volta ao máximo."""
        jogador_padrao.receber_dano(18)   # hp: 20 → 2
        jogador_padrao.curar(9999)         # hp: 2 → 20 (hp_max)
        assert jogador_padrao.hp == jogador_padrao.hp_max

    def test_repr_contem_informacoes_principais(self, jogador_padrao):
        """__repr__ deve conter nome, hp e atk do jogador."""
        rep = repr(jogador_padrao)
        assert "Herói"  in rep
        assert "20"     in rep
        assert "5"      in rep