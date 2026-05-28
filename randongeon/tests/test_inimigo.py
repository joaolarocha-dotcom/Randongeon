"""
Suíte de testes unitários para jogo/entidades/inimigo.py — v2

Mudanças em relação à versão anterior:
  - Parâmetro 'moedas' agora é obrigatório em Inimigo.__init__().
    Todas as chamadas inline de Inimigo(...) foram atualizadas.
  - Bloco 1: adicionados testes de validação de 'moedas' negativa e
    teste de criação verificando o atributo 'moedas'.
  - Bloco 4: mocks com side_effect atualizados para cobrir o randint
    adicional de 'moedas' na geração aleatória.
  - Bloco 5 (escalonamento): verificações de moedas incluídas.

Lote 1 — correções:
  - test_mock_gera_inimigo_dificuldade_2: andar 3 → 5 (threshold v3).
  - test_inimigo_dif2_nome_pertence_ao_pool_correto: andar 3 → 5.
  - test_inimigo_dif2_moedas_dentro_do_range: andar 3 → 5.
  - test_inimigos_dif2_tem_moedas_maiores_que_dif1_em_media: andar 3 → 5.

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
        assert inimigo_padrao.moedas      == 5   # ← novo atributo v2

    def test_criacao_com_dificuldade_maxima(self):
        """Caminho feliz: deve aceitar dificuldade 3 (boss) com moedas."""
        boss = Inimigo("Dragão", hp=50, atk=20, dificuldade=3, xp=200, moedas=100)
        assert boss.dificuldade == 3
        assert boss.moedas      == 100

    def test_criacao_com_moedas_zero(self):
        """Borda: moedas=0 deve ser aceito (inimigo que não dropa moedas)."""
        i = Inimigo("Fantasma", hp=5, atk=2, dificuldade=1, xp=10, moedas=0)
        assert i.moedas == 0

    @pytest.mark.parametrize("nome_invalido", ["", None, 42])
    def test_nome_invalido_levanta_value_error(self, nome_invalido):
        """Exceção: nome inválido deve lançar ValueError."""
        with pytest.raises(ValueError):
            Inimigo(nome_invalido, hp=10, atk=3, dificuldade=1, xp=10, moedas=0)

    @pytest.mark.parametrize("hp_invalido", [0, -1, -50])
    def test_hp_invalido_levanta_value_error(self, hp_invalido):
        """Exceção: hp <= 0 deve lançar ValueError."""
        with pytest.raises(ValueError):
            Inimigo("Goblin", hp=hp_invalido, atk=3, dificuldade=1, xp=10, moedas=0)

    @pytest.mark.parametrize("atk_invalido", [0, -1, -10])
    def test_atk_invalido_levanta_value_error(self, atk_invalido):
        """Exceção: atk <= 0 deve lançar ValueError."""
        with pytest.raises(ValueError):
            Inimigo("Goblin", hp=10, atk=atk_invalido, dificuldade=1, xp=10, moedas=0)

    def test_dificuldade_zero_levanta_value_error(self):
        """Exceção: dificuldade < 1 deve lançar ValueError."""
        with pytest.raises(ValueError):
            Inimigo("Goblin", hp=10, atk=3, dificuldade=0, xp=10, moedas=0)

    def test_xp_negativo_levanta_value_error(self):
        """Exceção: xp negativo deve lançar ValueError."""
        with pytest.raises(ValueError):
            Inimigo("Goblin", hp=10, atk=3, dificuldade=1, xp=-5, moedas=0)

    def test_moedas_negativas_levanta_value_error(self):
        """Exceção (novo v2): moedas negativas devem lançar ValueError."""
        with pytest.raises(ValueError):
            Inimigo("Goblin", hp=10, atk=3, dificuldade=1, xp=10, moedas=-1)

    def test_xp_zero_e_valido(self):
        """Borda: xp=0 deve ser aceito (inimigo que não dá experiência)."""
        i = Inimigo("Sombra", hp=5, atk=2, dificuldade=1, xp=0, moedas=0)
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
        assert inimigo_padrao.receber_dano(4) == 4

    def test_hp_nao_fica_negativo(self, inimigo_padrao):
        """Limite: hp deve parar em 0, nunca ir abaixo."""
        inimigo_padrao.receber_dano(9999)
        assert inimigo_padrao.hp == 0

    def test_dano_excessivo_retorna_hp_disponivel(self, inimigo_padrao):
        """Limite: dano efetivo é limitado ao hp atual do inimigo (hp=10)."""
        assert inimigo_padrao.receber_dano(9999) == 10

    def test_dano_zero_nao_altera_hp(self, inimigo_padrao):
        """Borda: dano 0 não deve alterar o hp."""
        inimigo_padrao.receber_dano(0)
        assert inimigo_padrao.hp == 10

    def test_dano_negativo_levanta_value_error(self, inimigo_padrao):
        """Exceção: dano negativo deve lançar ValueError."""
        with pytest.raises(ValueError):
            inimigo_padrao.receber_dano(-3)

    @pytest.mark.parametrize("dano,hp_esperado", [
        (0,   10),
        (3,    7),
        (10,   0),
        (100,  0),
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
    Testa o método estático gerar() usando mocks.

    ATENÇÃO v2: gerar() agora sorteia 4 valores via randint para
    dificuldade 1 (hp, atk, xp, moedas) e 4 para dificuldade 2.
    O side_effect do mock precisa cobrir todos esses sorteios.
    """

    def test_gerar_retorna_instancia_de_inimigo(self):
        """Caminho feliz: gerar() deve retornar sempre uma instância de Inimigo."""
        inimigo = Inimigo.gerar(andar=1)
        assert isinstance(inimigo, Inimigo)

    def test_inimigo_gerado_tem_hp_positivo(self):
        """Caminho feliz: inimigo gerado deve ter hp > 0."""
        assert Inimigo.gerar(andar=1).hp > 0

    def test_inimigo_gerado_tem_xp_nao_negativo(self):
        """Caminho feliz: xp do inimigo gerado deve ser >= 0."""
        assert Inimigo.gerar(andar=1).xp >= 0

    def test_inimigo_gerado_tem_moedas_nao_negativas(self):
        """Caminho feliz (novo v2): moedas do inimigo gerado devem ser >= 0."""
        assert Inimigo.gerar(andar=1).moedas >= 0

    def test_andar_zero_levanta_value_error(self):
        """Exceção: andar=0 deve lançar ValueError."""
        with pytest.raises(ValueError):
            Inimigo.gerar(andar=0)

    def test_andar_negativo_levanta_value_error(self):
        """Exceção: andar negativo deve lançar ValueError."""
        with pytest.raises(ValueError):
            Inimigo.gerar(andar=-1)

    @patch("jogo.entidades.inimigo.random.random", return_value=0.9)
    @patch("jogo.entidades.inimigo.random.choice", return_value="Goblin")
    @patch("jogo.entidades.inimigo.random.randint", side_effect=[5, 2, 15, 3])
    def test_mock_gera_inimigo_dificuldade_1(self, mock_randint, mock_choice, mock_random):
        """
        Mock completo: random.random=0.9 (> 0.3) → dificuldade 1.
        side_effect cobre: hp=5, atk=2, xp=15, moedas=3 (4 sorteios).
        """
        inimigo = Inimigo.gerar(andar=3)
        assert inimigo.dificuldade == 1
        assert inimigo.nome        == "Goblin"
        assert inimigo.hp          == 5
        assert inimigo.atk         == 2
        assert inimigo.xp          == 15
        assert inimigo.moedas      == 3   # ← novo v2

    @patch("jogo.entidades.inimigo.random.random", return_value=0.1)
    @patch("jogo.entidades.inimigo.random.choice", return_value="Orc")
    @patch("jogo.entidades.inimigo.random.randint", side_effect=[12, 4, 40, 8])
    def test_mock_gera_inimigo_dificuldade_2(self, mock_randint, mock_choice, mock_random):
        """
        Mock completo: random.random=0.1 (< 0.3) e andar >= 5 → dificuldade 2.
        FIX Lote 1: andar=3 → andar=5 (threshold elite mudou para andar 5 na v3).
        side_effect cobre: hp=12, atk=4, xp=40, moedas=8 (4 sorteios).
        """
        inimigo = Inimigo.gerar(andar=5)   # FIX: era andar=3
        assert inimigo.dificuldade == 2
        assert inimigo.nome        == "Orc"
        assert inimigo.hp          == 12
        assert inimigo.atk         == 4
        assert inimigo.xp          == 40
        assert inimigo.moedas      == 8   # ← novo v2

    @patch("jogo.entidades.inimigo.random.random", return_value=0.1)
    def test_elite_nao_aparece_antes_do_andar_3(self, mock_random):
        """
        Mock: mesmo com random.random=0.1, elite NÃO deve aparecer antes do andar 3.
        """
        inimigo = Inimigo.gerar(andar=2)
        assert inimigo.dificuldade == 1

    @patch("jogo.entidades.inimigo.random.random", return_value=0.9)
    def test_dificuldade_1_sem_elite_no_andar_1(self, mock_random):
        """Mock: random.random=0.9 e andar=1 → sempre dificuldade 1."""
        assert Inimigo.gerar(andar=1).dificuldade == 1

    @patch("jogo.entidades.inimigo.random.random", return_value=0.9)
    def test_inimigo_dif1_nome_pertence_ao_pool_correto(self, mock_random):
        """Mock: dificuldade 1 → nome deve pertencer ao pool NOMES_DIFICULDADE_1."""
        assert Inimigo.gerar(andar=1).nome in NOMES_DIFICULDADE_1

    @patch("jogo.entidades.inimigo.random.random", return_value=0.1)
    def test_inimigo_dif2_nome_pertence_ao_pool_correto(self, mock_random):
        """
        Mock: dificuldade 2 → nome deve pertencer ao pool NOMES_DIFICULDADE_2.
        FIX Lote 1: andar=3 → andar=5 (threshold elite mudou para andar 5 na v3).
        """
        assert Inimigo.gerar(andar=5).nome in NOMES_DIFICULDADE_2   # FIX: era andar=3

    @patch("jogo.entidades.inimigo.random.random", return_value=0.9)
    def test_inimigo_dif1_moedas_dentro_do_range(self, mock_random):
        """
        Caminho feliz (novo v2): moedas de inimigo dificuldade 1
        devem estar no range definido (0 a 5).
        """
        for _ in range(20):
            i = Inimigo.gerar(andar=1)
            assert 0 <= i.moedas <= 5

    @patch("jogo.entidades.inimigo.random.random", return_value=0.1)
    def test_inimigo_dif2_moedas_dentro_do_range(self, mock_random):
        """
        Caminho feliz (novo v2): moedas de inimigo dificuldade 2
        devem estar no range definido (6 a 11).
        FIX Lote 1: andar=3 → andar=5 (threshold elite mudou para andar 5 na v3).
        """
        for _ in range(20):
            i = Inimigo.gerar(andar=5)   # FIX: era andar=3
            assert 6 <= i.moedas <= 11


class TestEscalonamentoPorAndar:
    """
    Testa estatisticamente que inimigos em andares avançados
    tendem a ser mais difíceis que nos primeiros andares.
    """

    def test_inimigos_andar_alto_tem_hp_medio_maior(self):
        """
        Estatístico: média de hp no andar 10 deve superar a do andar 1.
        Elite (andar 10): hp 8-15. Comum (andar 1): hp 3-8.
        """
        hp_andar_1  = [Inimigo.gerar(andar=1).hp  for _ in range(30)]
        hp_andar_10 = [Inimigo.gerar(andar=10).hp for _ in range(30)]
        assert (sum(hp_andar_10) / 30) >= (sum(hp_andar_1) / 30)

    def test_todo_inimigo_gerado_e_instancia_valida(self):
        """Propriedade: qualquer inimigo gerado em qualquer andar deve ser válido."""
        for andar in [1, 2, 3, 5, 10]:
            i = Inimigo.gerar(andar=andar)
            assert isinstance(i, Inimigo)
            assert i.hp   > 0
            assert i.atk  > 0
            assert i.dificuldade >= 1
            assert i.moedas      >= 0   # ← novo v2

    def test_inimigos_dif2_tem_moedas_maiores_que_dif1_em_media(self):
        """
        Estatístico (novo v2): média de moedas de inimigos elite (dif=2)
        deve superar a de inimigos comuns (dif=1).
        Elite: moedas 6-11. Comum: moedas 0-5.
        FIX Lote 1: andar=3 → andar=5 para garantir dificuldade 2 gerada.
        """
        with patch("jogo.entidades.inimigo.random.random", return_value=0.9):
            moedas_dif1 = [Inimigo.gerar(andar=1).moedas for _ in range(20)]
        with patch("jogo.entidades.inimigo.random.random", return_value=0.1):
            moedas_dif2 = [Inimigo.gerar(andar=5).moedas for _ in range(20)]  # FIX: era andar=3
        assert (sum(moedas_dif2) / 20) > (sum(moedas_dif1) / 20)


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