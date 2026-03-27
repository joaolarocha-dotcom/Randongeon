# randongeon/tests/test_gerador.py

"""
Suíte de testes unitários para jogo/sistemas/gerador.py

Cobre:
  - Criação e validação do GeradorSala
  - gerar_sala(): tipo, conteúdo e descrição retornados
  - gerar_item(): sempre retorna Item válido
  - gerar_inimigo(): sempre retorna Inimigo válido
  - Mocks de random para forçar caminhos determinísticos
  - Fake gerador (stub) para isolar dependências nos testes de Masmorra
  - Casos de borda e exceções

Execute com:
    pytest tests/test_gerador.py -v
    pytest tests/test_gerador.py -v --tb=short
"""

import pytest
from unittest.mock import patch, MagicMock
from jogo.entidades.item    import Item
from jogo.entidades.inimigo import Inimigo
from jogo.sistemas.gerador  import GeradorSala, DESCRICOES_SALA, CATALOGO_ITENS


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 1 — Criação e validação do __init__
# ══════════════════════════════════════════════════════════════════════════════

class TestCriacaoGeradorSala:
    """Testa a criação de instâncias de GeradorSala e validação dos parâmetros."""

    def test_criacao_padrao_sem_parametros(self):
        """Caminho feliz: GeradorSala() deve ser instanciado sem erros."""
        g = GeradorSala()
        assert g is not None

    def test_chance_item_padrao_e_cinco(self):
        """Caminho feliz: chance_item padrão deve ser 5."""
        g = GeradorSala()
        assert g._chance_item == 5

    def test_chance_item_customizado(self):
        """Caminho feliz: chance_item customizado deve ser armazenado."""
        g = GeradorSala(chance_item=10)
        assert g._chance_item == 10

    def test_chance_item_minimo_valido_e_dois(self):
        """Borda: chance_item=2 deve ser aceito (mínimo válido)."""
        g = GeradorSala(chance_item=2)
        assert g._chance_item == 2

    def test_chance_item_um_levanta_value_error(self):
        """Exceção: chance_item=1 deve lançar ValueError."""
        with pytest.raises(ValueError):
            GeradorSala(chance_item=1)

    def test_chance_item_zero_levanta_value_error(self):
        """Exceção: chance_item=0 deve lançar ValueError."""
        with pytest.raises(ValueError):
            GeradorSala(chance_item=0)

    def test_chance_item_negativo_levanta_value_error(self):
        """Exceção: chance_item negativo deve lançar ValueError."""
        with pytest.raises(ValueError):
            GeradorSala(chance_item=-5)


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 2 — gerar_sala(): estrutura do retorno
# ══════════════════════════════════════════════════════════════════════════════

class TestGeradorSalaRetorno:
    """Testa a estrutura e tipos do retorno de gerar_sala()."""

    def test_retorna_tupla_com_tres_elementos(self, gerador_padrao):
        """Caminho feliz: gerar_sala() deve retornar uma tupla de 3 elementos."""
        resultado = gerador_padrao.gerar_sala(andar=1)
        assert isinstance(resultado, tuple)
        assert len(resultado) == 3

    def test_primeiro_elemento_e_string_tipo(self, gerador_padrao):
        """Caminho feliz: primeiro elemento deve ser 'item' ou 'inimigo'."""
        tipo, _, _ = gerador_padrao.gerar_sala(andar=1)
        assert tipo in ("item", "inimigo")

    def test_terceiro_elemento_e_string_descricao(self, gerador_padrao):
        """Caminho feliz: terceiro elemento deve ser uma string não vazia."""
        _, _, descricao = gerador_padrao.gerar_sala(andar=1)
        assert isinstance(descricao, str)
        assert len(descricao) > 0

    def test_descricao_pertence_ao_catalogo(self, gerador_padrao):
        """Caminho feliz: descrição retornada deve estar nas descrições válidas."""
        _, _, descricao = gerador_padrao.gerar_sala(andar=1)
        assert descricao in DESCRICOES_SALA

    def test_andar_zero_levanta_value_error(self, gerador_padrao):
        """Exceção: andar=0 deve lançar ValueError."""
        with pytest.raises(ValueError):
            gerador_padrao.gerar_sala(andar=0)

    def test_andar_negativo_levanta_value_error(self, gerador_padrao):
        """Exceção: andar negativo deve lançar ValueError."""
        with pytest.raises(ValueError):
            gerador_padrao.gerar_sala(andar=-1)

    @pytest.mark.parametrize("andar", [1, 2, 3, 5, 10, 20])
    def test_gerar_sala_valida_para_varios_andares(self, gerador_padrao, andar):
        """Parametrizado: gerar_sala() deve funcionar corretamente em qualquer andar."""
        tipo, conteudo, descricao = gerador_padrao.gerar_sala(andar=andar)
        assert tipo in ("item", "inimigo")
        assert conteudo is not None
        assert isinstance(descricao, str)


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 3 — gerar_sala() com Mocks: forçando caminho de item
# ══════════════════════════════════════════════════════════════════════════════

class TestGeradorSalaMockItem:
    """
    Testa gerar_sala() com random.randint mockado para forçar
    o caminho de geração de item (randint retorna 1).
    """

    @patch("jogo.sistemas.gerador.random.randint", return_value=1)
    @patch("jogo.sistemas.gerador.random.choice")
    def test_mock_randint_1_gera_item(self, mock_choice, mock_randint, gerador_padrao):
        """
        Mock: randint=1 → deve gerar item (chance 1 em N).
        mock_choice retorna o primeiro item do catálogo para o conteúdo
        e a primeira descrição para o ambiente.
        """
        mock_choice.side_effect = [DESCRICOES_SALA[0], CATALOGO_ITENS[0]]
        tipo, conteudo, _ = gerador_padrao.gerar_sala(andar=1)
        assert tipo    == "item"
        assert isinstance(conteudo, Item)

    @patch("jogo.sistemas.gerador.random.randint", return_value=1)
    def test_mock_conteudo_item_e_instancia_de_item(self, mock_randint, gerador_padrao):
        """Mock: com randint=1 o conteúdo deve sempre ser uma instância de Item."""
        tipo, conteudo, _ = gerador_padrao.gerar_sala(andar=1)
        assert tipo == "item"
        assert isinstance(conteudo, Item)

    @patch("jogo.sistemas.gerador.random.randint", return_value=1)
    def test_mock_item_pertence_ao_catalogo(self, mock_randint, gerador_padrao):
        """Mock: item gerado deve pertencer ao CATALOGO_ITENS."""
        _, conteudo, _ = gerador_padrao.gerar_sala(andar=1)
        nomes_catalogo = [i.nome for i in CATALOGO_ITENS]
        assert conteudo.nome in nomes_catalogo


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 4 — gerar_sala() com Mocks: forçando caminho de inimigo
# ══════════════════════════════════════════════════════════════════════════════

class TestGeradorSalaMockInimigo:
    """
    Testa gerar_sala() com random.randint mockado para forçar
    o caminho de geração de inimigo (randint retorna valor > 1).
    """

    @patch("jogo.sistemas.gerador.random.randint", return_value=2)
    def test_mock_randint_2_gera_inimigo(self, mock_randint, gerador_padrao):
        """Mock: randint=2 → deve gerar inimigo (não é 1, logo não é item)."""
        tipo, conteudo, _ = gerador_padrao.gerar_sala(andar=1)
        assert tipo == "inimigo"
        assert isinstance(conteudo, Inimigo)

    @patch("jogo.sistemas.gerador.random.randint", return_value=5)
    def test_mock_randint_5_gera_inimigo(self, mock_randint, gerador_padrao):
        """Mock: randint=5 (máximo padrão) → deve gerar inimigo."""
        tipo, conteudo, _ = gerador_padrao.gerar_sala(andar=1)
        assert tipo == "inimigo"
        assert isinstance(conteudo, Inimigo)

    @patch("jogo.sistemas.gerador.random.randint", return_value=2)
    def test_mock_inimigo_tem_hp_positivo(self, mock_randint, gerador_padrao):
        """Mock: inimigo gerado deve ter hp > 0."""
        _, inimigo, _ = gerador_padrao.gerar_sala(andar=1)
        assert inimigo.hp > 0

    @patch("jogo.sistemas.gerador.random.randint", return_value=2)
    def test_mock_inimigo_tem_xp_nao_negativo(self, mock_randint, gerador_padrao):
        """Mock: inimigo gerado deve ter xp >= 0."""
        _, inimigo, _ = gerador_padrao.gerar_sala(andar=1)
        assert inimigo.xp >= 0


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 5 — gerar_item() direto
# ══════════════════════════════════════════════════════════════════════════════

class TestGeradorItem:
    """Testa o método gerar_item() de forma isolada."""

    def test_retorna_tipo_item(self, gerador_padrao):
        """Caminho feliz: tipo deve ser 'item'."""
        tipo, _, _ = gerador_padrao.gerar_item()
        assert tipo == "item"

    def test_retorna_instancia_de_item(self, gerador_padrao):
        """Caminho feliz: conteúdo deve ser instância de Item."""
        _, conteudo, _ = gerador_padrao.gerar_item()
        assert isinstance(conteudo, Item)

    def test_retorna_descricao_passada(self, gerador_padrao):
        """Caminho feliz: descrição passada deve ser retornada na tupla."""
        desc = "Sala de pedra silenciosa."
        _, _, descricao = gerador_padrao.gerar_item(descricao=desc)
        assert descricao == desc

    def test_retorna_descricao_vazia_por_padrao(self, gerador_padrao):
        """Borda: sem descrição fornecida, o terceiro elemento deve ser string vazia."""
        _, _, descricao = gerador_padrao.gerar_item()
        assert descricao == ""

    def test_item_retornado_pertence_ao_catalogo(self, gerador_padrao):
        """Invariante: em 20 chamadas, todos os itens devem ser do catálogo."""
        nomes_validos = {i.nome for i in CATALOGO_ITENS}
        for _ in range(20):
            _, item, _ = gerador_padrao.gerar_item()
            assert item.nome in nomes_validos


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 6 — gerar_inimigo() direto
# ══════════════════════════════════════════════════════════════════════════════

class TestGeradorInimigo:
    """Testa o método gerar_inimigo() de forma isolada."""

    def test_retorna_tipo_inimigo(self, gerador_padrao):
        """Caminho feliz: tipo deve ser 'inimigo'."""
        tipo, _, _ = gerador_padrao.gerar_inimigo(andar=1)
        assert tipo == "inimigo"

    def test_retorna_instancia_de_inimigo(self, gerador_padrao):
        """Caminho feliz: conteúdo deve ser instância de Inimigo."""
        _, conteudo, _ = gerador_padrao.gerar_inimigo(andar=1)
        assert isinstance(conteudo, Inimigo)

    def test_retorna_descricao_passada(self, gerador_padrao):
        """Caminho feliz: descrição fornecida deve aparecer na tupla."""
        desc = "Caverna úmida."
        _, _, descricao = gerador_padrao.gerar_inimigo(andar=1, descricao=desc)
        assert descricao == desc

    def test_retorna_descricao_vazia_por_padrao(self, gerador_padrao):
        """Borda: sem descrição fornecida, o terceiro elemento deve ser string vazia."""
        _, _, descricao = gerador_padrao.gerar_inimigo(andar=1)
        assert descricao == ""

    def test_andar_zero_levanta_value_error(self, gerador_padrao):
        """Exceção: andar=0 deve lançar ValueError."""
        with pytest.raises(ValueError):
            gerador_padrao.gerar_inimigo(andar=0)

    def test_andar_negativo_levanta_value_error(self, gerador_padrao):
        """Exceção: andar negativo deve lançar ValueError."""
        with pytest.raises(ValueError):
            gerador_padrao.gerar_inimigo(andar=-3)

    @pytest.mark.parametrize("andar", [1, 3, 5, 10])
    def test_inimigo_valido_em_varios_andares(self, gerador_padrao, andar):
        """Parametrizado: inimigo deve ser válido em qualquer andar testado."""
        _, inimigo, _ = gerador_padrao.gerar_inimigo(andar=andar)
        assert inimigo.hp  > 0
        assert inimigo.atk > 0
        assert inimigo.dificuldade >= 1


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 7 — Fake Gerador (Stub para isolar Masmorra)
# ══════════════════════════════════════════════════════════════════════════════

class TestFakeGerador:
    """
    Demonstra o padrão FakeGerador (stub) utilizado nos testes de Masmorra.
    O FakeGerador implementa a mesma interface do GeradorSala mas retorna
    valores fixos, eliminando qualquer aleatoriedade.
    """

    def test_fake_gerador_item_retorna_tipo_correto(self):
        """Stub de item: FakeGerador deve retornar tipo 'item' quando configurado."""
        item_fixo = Item("Poção Teste", bonus_hp=10)

        class FakeGeradorItem:
            def gerar_sala(self, andar=1):
                return ("item", item_fixo, "Sala de teste.")

        g = FakeGeradorItem()
        tipo, conteudo, desc = g.gerar_sala(andar=1)

        assert tipo     == "item"
        assert conteudo == item_fixo
        assert desc     == "Sala de teste."

    def test_fake_gerador_inimigo_retorna_tipo_correto(self):
        """Stub de inimigo: FakeGerador deve retornar tipo 'inimigo' quando configurado."""
        inimigo_fixo = Inimigo("Dummy", hp=5, atk=1, dificuldade=1, xp=10)

        class FakeGeradorInimigo:
            def gerar_sala(self, andar=1):
                return ("inimigo", inimigo_fixo, "Corredor escuro.")

        g = FakeGeradorInimigo()
        tipo, conteudo, _ = g.gerar_sala(andar=1)

        assert tipo     == "inimigo"
        assert conteudo == inimigo_fixo

    def test_gerador_chance_item_1_em_2_aumenta_frequencia_de_itens(self):
        """
        Probabilístico: GeradorSala(chance_item=2) deve gerar itens com
        frequência significativamente maior que chance_item=10.
        Roda 100 gerações e compara proporções.
        """
        gerador_frequente = GeradorSala(chance_item=2)
        gerador_raro      = GeradorSala(chance_item=10)

        n = 100
        itens_frequente = sum(
            1 for _ in range(n)
            if gerador_frequente.gerar_sala(andar=1)[0] == "item"
        )
        itens_raro = sum(
            1 for _ in range(n)
            if gerador_raro.gerar_sala(andar=1)[0] == "item"
        )

        # Com chance 1/2 esperamos ~50 itens; com 1/10 esperamos ~10.
        # O teste apenas verifica que frequente > raro — robustez estatística.
        assert itens_frequente > itens_raro