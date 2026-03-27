# randongeon/tests/test_inimigo.py

"""
Suíte de testes unitários para jogo/entidades/inimigo.py

Cobre:
  - Criação e validação de atributos
  - Estado: esta_vivo() e receber_dano()
  - Geração aleatória: gerar() com mocks de random
  - Escalonamento de dificuldade por andar
  - Representação: __repr__()

Execute com:
    pytest tests/test_inimigo.py -v
    pytest tests/test_inimigo.py -v --tb=short
"""

import pytest
from unittest.mock import patch
from jogo.entidades.inimigo import Inimigo, NOMES_DIFICULDADE_1, NOMES_DIFICULDADE_2


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 1 — Criação e validação do __init__
# ══════════════════════════════════════════════════════════════════════════════

class TestCriacaoInimigo:
    """Testa a criação de instâncias de Inimigo e validação dos parâmetros."""

    def test_atributos_iniciais_corretos(self, inimigo_padrao):
        """Caminho feliz: todos os atributos devem ser definidos corretamente."""
        assert inimigo_padrao.nome        == "Goblin"
        assert inimigo_padrao.hp          == 10
        assert inimigo_padrao.atk         == 3
        assert inimigo_padrao.dificuldade == 1
        assert inimigo_padrao.xp          == 15

    def test_criacao_com_dificuldade_maxima(self):
        """Caminho feliz: deve aceitar dificuldade 3 (boss)."""
        boss = Inimigo("Dragão", hp=50, atk=20, dificuldade=3, xp=200)
        assert boss.dificuldade == 3

    @pytest.mark.parametrize("nome_invalido", ["", None, 42])
    def test_nome_invalido_levanta_value_error(self, nome_invalido):
        """Exceção: nome inválido deve lançar ValueError."""
        with pytest.raises(ValueError):
            Inimigo(nome_invalido, hp=10, atk=3, dificuldade=1, xp=10)

    @pytest.mark.parametrize("hp_invalido", [0, -1, -50])
    def test_hp_invalido_levanta_value_error(self, hp_invalido):
        """Exceção: hp <= 0 deve lançar ValueError."""
        with pytest.raises(ValueError):
            Inimigo("Goblin", hp=hp_invalido, atk=3, dificuldade=1, xp=10)

    @pytest.mark.parametrize("atk_invalido", [0, -1, -10])
    def test_atk_invalido_levanta_value_error(self, atk_invalido):
        """Exceção: atk <= 0 deve lançar ValueError."""
        with pytest.raises(ValueError):
            Inimigo("Goblin", hp=10, atk=atk_invalido, dificuldade=1, xp=10)

    def test_dificuldade_zero_levanta_value_error(self):
        """Exceção: dificuldade < 1 deve lançar ValueError."""
        with pytest.raises(ValueError):
            Inimigo("Goblin", hp=10, atk=3, dificuldade=0, xp=10)

    def test_xp_negativo_levanta_value_error(self):
        """Exceção: xp negativo deve lançar ValueError."""
        with pytest.raises(ValueError):
            Inimigo("Goblin", hp=10, atk=3, dificuldade=1, xp=-5)

    def test_xp_zero_e_valido(self):
        """Borda: xp=0 deve ser aceito (inimigo que não dá experiência)."""
        i = Inimigo("Sombra", hp=5, atk=2, dificuldade=1, xp=0)
        assert i.xp == 0


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 2 — esta_vivo()
# ══════════════════════════════════════════════════════════════════════════════

class TestEstaVivo:
    """Testa o estado de vida do inimigo."""

    def test_vivo_quando_hp_maior_que_zero(self, inimigo_padrao):
        """Caminho feliz: inimigo com hp > 0 deve estar vivo."""
        assert inimigo_padrao.esta_vivo() is True

    def test_morto_quando_hp_igual_a_zero(self, inimigo_padrao):
        """Exceção de estado: hp = 0 deve retornar False."""
        inimigo_padrao.hp = 0
        assert inimigo_padrao.esta_vivo() is False

    def test_morto_apos_dano_letal(self, inimigo_padrao):
        """Inimigo com hp=10 deve morrer ao receber 10 de dano."""
        inimigo_padrao.receber_dano(10)
        assert inimigo_padrao.esta_vivo() is False


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 3 — receber_dano()
# ══════════════════════════════════════════════════════════════════════════════

class TestReceberDano:
    """Testa a aplicação de dano ao inimigo."""

    def test_dano_reduz_hp_corretamente(self, inimigo_padrao):
        """Caminho feliz: dano deve ser subtraído do hp do inimigo."""
        inimigo_padrao.receber_dano(4)
        assert inimigo_padrao.hp == 6

    def test_retorna_dano_efetivo(self, inimigo_padrao):
        """Caminho feliz: método deve retornar o dano efetivamente aplicado."""
        efetivo = inimigo_padrao.receber_dano(4)
        assert efetivo == 4

    def test_hp_nao_fica_negativo(self, inimigo_padrao):
        """Limite: hp deve parar em 0, nunca ir abaixo."""
        inimigo_padrao.receber_dano(9999)
        assert inimigo_padrao.hp == 0

    def test_dano_excessivo_retorna_hp_disponivel(self, inimigo_padrao):
        """Limite: dano efetivo é limitado ao hp atual do inimigo."""
        efetivo = inimigo_padrao.receber_dano(9999)
        assert efetivo == 10  # hp era 10

    def test_dano_zero_nao_altera_hp(self, inimigo_padrao):
        """Borda: dano 0 não deve alterar o hp."""
        inimigo_padrao.receber_dano(0)
        assert inimigo_padrao.hp == 10

    def test_dano_negativo_levanta_value_error(self, inimigo_padrao):
        """Exceção: dano negativo deve lançar ValueError."""
        with pytest.raises(ValueError):
            inimigo_padrao.receber_dano(-3)

    @pytest.mark.parametrize("dano,hp_esperado", [
        (0,    10),
        (3,     7),
        (10,    0),
        (100,   0),
    ])
    def test_dano_parametrizado(self, inimigo_padrao, dano, hp_esperado):
        """Parametrizado: verifica hp resultante para diferentes valores de dano."""
        inimigo_padrao.receber_dano(dano)
        assert inimigo_padrao.hp == hp_esperado


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 4 — gerar() com Mocks de random
# ══════════════════════════════════════════════════════════════════════════════

class TestGerar:
    """
    Testa o método estático gerar() usando mocks para controlar
    a aleatoriedade e garantir comportamento determinístico.
    """

    def test_gerar_retorna_instancia_de_inimigo(self):
        """Caminho feliz: gerar() deve retornar sempre uma instância de Inimigo."""
        inimigo = Inimigo.gerar(andar=1)
        assert isinstance(inimigo, Inimigo)

    def test_inimigo_gerado_tem_hp_positivo(self):
        """Caminho feliz: inimigo gerado deve ter hp > 0."""
        inimigo = Inimigo.gerar(andar=1)
        assert inimigo.hp > 0

    def test_inimigo_gerado_tem_xp_nao_negativo(self):
        """Caminho feliz: xp do inimigo gerado deve ser >= 0."""
        inimigo = Inimigo.gerar(andar=1)
        assert inimigo.xp >= 0

    def test_andar_zero_levanta_value_error(self):
        """Exceção: andar=0 deve lançar ValueError."""
        with pytest.raises(ValueError):
            Inimigo.gerar(andar=0)

    def test_andar_negativo_levanta_value_error(self):
        """Exceção: andar negativo deve lançar ValueError."""
        with pytest.raises(ValueError):
            Inimigo.gerar(andar=-1)

    # ── Mocks: forçando dificuldade 1 ─────────────────────────────────────────

    @patch("jogo.entidades.inimigo.random.random", return_value=0.9)
    @patch("jogo.entidades.inimigo.random.choice", return_value="Goblin")
    @patch("jogo.entidades.inimigo.random.randint", side_effect=[5, 2, 15])
    def test_mock_gera_inimigo_dificuldade_1(self, mock_randint, mock_choice, mock_random):
        """
        Mock completo: random.random=0.9 (> 0.3) → dificuldade 1.
        Valida que o inimigo gerado usa os valores mockados corretamente.
        """
        # andar=3 permite elite, mas random.random=0.9 > 0.3 → não é elite
        inimigo = Inimigo.gerar(andar=3)
        assert inimigo.dificuldade == 1
        assert inimigo.nome        == "Goblin"
        assert inimigo.hp          == 5
        assert inimigo.atk         == 2
        assert inimigo.xp          == 15

    @patch("jogo.entidades.inimigo.random.random", return_value=0.1)
    @patch("jogo.entidades.inimigo.random.choice", return_value="Orc")
    @patch("jogo.entidades.inimigo.random.randint", side_effect=[12, 4, 40])
    def test_mock_gera_inimigo_dificuldade_2(self, mock_randint, mock_choice, mock_random):
        """
        Mock completo: random.random=0.1 (< 0.3) e andar >= 3 → dificuldade 2 (elite).
        Valida que o inimigo elite usa os valores mockados corretamente.
        """
        inimigo = Inimigo.gerar(andar=3)
        assert inimigo.dificuldade == 2
        assert inimigo.nome        == "Orc"
        assert inimigo.hp          == 12
        assert inimigo.atk         == 4
        assert inimigo.xp          == 40

    @patch("jogo.entidades.inimigo.random.random", return_value=0.1)
    def test_elite_nao_aparece_antes_do_andar_3(self, mock_random):
        """
        Mock: mesmo com random.random=0.1, elite NÃO deve aparecer antes do andar 3.
        Valida a regra de andar mínimo para elites.
        """
        inimigo = Inimigo.gerar(andar=2)
        assert inimigo.dificuldade == 1

    @patch("jogo.entidades.inimigo.random.random", return_value=0.9)
    def test_dificuldade_1_sem_elite_no_andar_1(self, mock_random):
        """
        Mock: random.random=0.9 e andar=1 → sempre dificuldade 1.
        """
        inimigo = Inimigo.gerar(andar=1)
        assert inimigo.dificuldade == 1

    # ── Verificação dos pools de nomes ────────────────────────────────────────

    @patch("jogo.entidades.inimigo.random.random", return_value=0.9)
    def test_inimigo_dif1_nome_pertence_ao_pool_correto(self, mock_random):
        """
        Mock: dificuldade 1 → nome deve pertencer ao pool NOMES_DIFICULDADE_1.
        """
        inimigo = Inimigo.gerar(andar=1)
        assert inimigo.nome in NOMES_DIFICULDADE_1

    @patch("jogo.entidades.inimigo.random.random", return_value=0.1)
    def test_inimigo_dif2_nome_pertence_ao_pool_correto(self, mock_random):
        """
        Mock: dificuldade 2 → nome deve pertencer ao pool NOMES_DIFICULDADE_2.
        """
        inimigo = Inimigo.gerar(andar=3)
        assert inimigo.nome in NOMES_DIFICULDADE_2


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 5 — Escalonamento por andar
# ══════════════════════════════════════════════════════════════════════════════

class TestEscalonamentoPorAndar:
    """
    Testa estatisticamente que inimigos gerados em andares avançados
    tendem a ser mais difíceis que nos primeiros andares.
    Usa múltiplas gerações para compensar a aleatoriedade residual.
    """

    def test_inimigos_andar_alto_tem_hp_medio_maior(self):
        """
        Estatístico: média de hp dos inimigos no andar 10 deve superar
        a média no andar 1 (elite tem hp 8-15 vs comum 3-8).
        """
        hp_andar_1  = [Inimigo.gerar(andar=1).hp  for _ in range(30)]
        hp_andar_10 = [Inimigo.gerar(andar=10).hp for _ in range(30)]
        assert sum(hp_andar_10) / len(hp_andar_10) >= sum(hp_andar_1) / len(hp_andar_1)

    def test_todo_inimigo_gerado_e_instancia_valida(self):
        """Propriedade: qualquer inimigo gerado deve ser uma instância válida."""
        for andar in [1, 2, 3, 5, 10]:
            i = Inimigo.gerar(andar=andar)
            assert isinstance(i, Inimigo)
            assert i.hp  > 0
            assert i.atk > 0
            assert i.dificuldade >= 1


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 6 — Representação
# ══════════════════════════════════════════════════════════════════════════════

class TestRepresentacao:
    """Testa a representação em string do inimigo."""

    def test_repr_contem_nome(self, inimigo_padrao):
        """__repr__ deve conter o nome do inimigo."""
        assert "Goblin" in repr(inimigo_padrao)

    def test_repr_contem_hp(self, inimigo_padrao):
        """__repr__ deve conter o hp do inimigo."""
        assert "10" in repr(inimigo_padrao)

    def test_repr_contem_atk(self, inimigo_padrao):
        """__repr__ deve conter o atk do inimigo."""
        assert "3" in repr(inimigo_padrao)