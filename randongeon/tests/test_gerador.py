"""
Suíte de testes unitários para jogo/sistemas/gerador.py

Mudanças em relação à versão anterior:
  - GeradorSala default chance_item mudou de 5 para 20.
  - gerar_sala() agora usa randint(1,10) com TRÊS saídas:
      sorte=1  → loja   (10%)
      sorte=2  → item   (10%)
      sorte>=3 → inimigo(80%)
  - Novo método gerar_loja() retorna ("loja", None, descricao).
  - test_primeiro_elemento_e_string_tipo agora inclui "loja".
  - Bloco 3 (mock item) atualizado: randint=2 força item (não mais 1).
  - Bloco novo: gerar_loja() testado isoladamente.
  - CATALOGO_ITENS tem novos itens com bonus_esq.

Execute com:
    pytest tests/test_gerador.py -v
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

    def test_chance_item_padrao_e_vinte(self):
        """
        Caminho feliz (atualizado v2): chance_item padrão agora é 20.
        O valor mudou de 5 para 20 porque o gerador passou a usar
        randint(1,10) com loja/item/inimigo — o padrão foi ajustado.
        """
        g = GeradorSala()
        assert g._chance_item == 20

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

    def test_primeiro_elemento_e_string_tipo_valido(self, gerador_padrao):
        """
        Caminho feliz (atualizado v2): primeiro elemento deve ser
        'item', 'inimigo' OU 'loja' — três saídas possíveis agora.
        """
        tipo, _, _ = gerador_padrao.gerar_sala(andar=1)
        assert tipo in ("item", "inimigo", "loja")

    def test_terceiro_elemento_e_string(self, gerador_padrao):
        """Caminho feliz: terceiro elemento deve ser uma string."""
        _, _, descricao = gerador_padrao.gerar_sala(andar=1)
        assert isinstance(descricao, str)

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
        """
        Parametrizado (atualizado v2): gerar_sala() deve retornar sempre
        uma tupla válida. conteudo pode ser None quando tipo='loja'.
        """
        tipo, conteudo, descricao = gerador_padrao.gerar_sala(andar=andar)
        assert tipo in ("item", "inimigo", "loja")
        assert isinstance(descricao, str)
        # quando é loja, conteudo é None por design
        if tipo != "loja":
            assert conteudo is not None

    def test_descricao_de_inimigo_pertence_ao_catalogo(self, gerador_padrao):
        """
        Caminho feliz: quando tipo='inimigo', descricao deve estar em DESCRICOES_SALA.
        """
        with patch("jogo.sistemas.gerador.random.randint", return_value=5):
            _, _, descricao = gerador_padrao.gerar_sala(andar=1)
        assert descricao in DESCRICOES_SALA

    def test_descricao_de_item_pertence_ao_catalogo(self, gerador_padrao):
        """Caminho feliz: quando tipo='item', descricao deve estar em DESCRICOES_SALA."""
        with patch("jogo.sistemas.gerador.random.randint", return_value=4):
            _, _, descricao = gerador_padrao.gerar_sala(andar=1)
        assert descricao in DESCRICOES_SALA


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 3 (NOVO v2) — gerar_sala() forçando caminho de loja
# ══════════════════════════════════════════════════════════════════════════════

class TestGeradorSalaMockLoja:
    """
    Testa o caminho da loja em gerar_sala().
    Na v2, randint=1 → loja (antes era item).
    """

    @patch("jogo.sistemas.gerador.random.randint", return_value=1)
    def test_mock_randint_1_gera_loja(self, mock_randint, gerador_padrao):
        """
        Mock: randint=1 → deve gerar loja.
        Na v2 randint=1 não gera mais item — agora gera loja.
        """
        tipo, conteudo, _ = gerador_padrao.gerar_sala(andar=1)
        assert tipo    == "loja"
        assert conteudo is None

    @patch("jogo.sistemas.gerador.random.randint", return_value=1)
    def test_mock_loja_descricao_e_string(self, mock_randint, gerador_padrao):
        """Mock: descrição de loja deve ser uma string não vazia."""
        _, _, descricao = gerador_padrao.gerar_sala(andar=1)
        assert isinstance(descricao, str)
        assert len(descricao) > 0

    @patch("jogo.sistemas.gerador.random.randint", return_value=1)
    def test_mock_loja_conteudo_e_none(self, mock_randint, gerador_padrao):
        """
        Mock: conteudo da loja deve ser None.
        A loja é instanciada pela Masmorra, não pelo Gerador.
        """
        _, conteudo, _ = gerador_padrao.gerar_sala(andar=1)
        assert conteudo is None


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 4 (atualizado v2) — gerar_sala() forçando caminho de item
# ══════════════════════════════════════════════════════════════════════════════

class TestGeradorSalaMockItem:
    """
    Testa gerar_sala() forçando o caminho de item.
    MUDANÇA v2: randint=2 agora força item (antes era randint=1).
    """

    @patch("jogo.sistemas.gerador.random.randint", return_value=4)
    def test_mock_randint_2_gera_item(self, mock_randint, gerador_padrao):
        """Mock: randint=4 → deve gerar item (faixa item é sorte 4-6)."""
        tipo, conteudo, _ = gerador_padrao.gerar_sala(andar=1)
        assert tipo == "item"
        assert isinstance(conteudo, Item)

    @patch("jogo.sistemas.gerador.random.randint", return_value=6)
    def test_mock_randint_6_gera_item(self, mock_randint, gerador_padrao):
        """Balance: faixa de item ampliada para 4-6 (10%→15%)."""
        tipo, _, _ = gerador_padrao.gerar_sala(andar=1)
        assert tipo == "item"

    @patch("jogo.sistemas.gerador.random.randint", return_value=4)
    def test_mock_item_pertence_ao_catalogo(self, mock_randint, gerador_padrao):
        """Mock: item gerado deve pertencer ao CATALOGO_ITENS."""
        _, conteudo, _ = gerador_padrao.gerar_sala(andar=1)
        nomes_catalogo = [i.nome for i in CATALOGO_ITENS]
        assert conteudo.nome in nomes_catalogo

    @patch("jogo.sistemas.gerador.random.randint", return_value=4)
    def test_mock_item_conteudo_nao_e_none(self, mock_randint, gerador_padrao):
        """Mock: conteudo de item não deve ser None."""
        _, conteudo, _ = gerador_padrao.gerar_sala(andar=1)
        assert conteudo is not None


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 5 (atualizado v2) — gerar_sala() forçando caminho de inimigo
# ══════════════════════════════════════════════════════════════════════════════

class TestGeradorSalaMockInimigo:
    """
    Testa gerar_sala() forçando o caminho de inimigo.
    MUDANÇA v2: qualquer randint >= 3 força inimigo.
    """

    @patch("jogo.sistemas.gerador.random.randint", return_value=7)
    def test_mock_randint_3_gera_inimigo(self, mock_randint, gerador_padrao):
        """Mock: randint=7 → deve gerar inimigo (faixa 7-20; item subiu p/ 4-6)."""
        tipo, conteudo, _ = gerador_padrao.gerar_sala(andar=1)
        assert tipo == "inimigo"
        assert isinstance(conteudo, Inimigo)

    @patch("jogo.sistemas.gerador.random.randint", return_value=20)
    def test_mock_randint_10_gera_inimigo(self, mock_randint, gerador_padrao):
        """Mock: randint=20 (máximo) → deve gerar inimigo."""
        tipo, conteudo, _ = gerador_padrao.gerar_sala(andar=1)
        assert tipo == "inimigo"
        assert isinstance(conteudo, Inimigo)

    @patch("jogo.sistemas.gerador.random.randint", return_value=10)
    def test_mock_inimigo_tem_hp_positivo(self, mock_randint, gerador_padrao):
        """Mock: inimigo gerado deve ter hp > 0."""
        _, inimigo, _ = gerador_padrao.gerar_sala(andar=1)
        assert inimigo.hp > 0

    @patch("jogo.sistemas.gerador.random.randint", return_value=10)
    def test_mock_inimigo_tem_moedas_nao_negativas(self, mock_randint, gerador_padrao):
        """Mock (novo v2): inimigo gerado deve ter moedas >= 0."""
        _, inimigo, _ = gerador_padrao.gerar_sala(andar=1)
        assert inimigo.moedas >= 0


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 6 — gerar_loja() direto (NOVO v2)
# ══════════════════════════════════════════════════════════════════════════════

class TestGeradorLoja:
    """Testa o método gerar_loja() de forma isolada — novo na v2."""

    def test_retorna_tipo_loja(self, gerador_padrao):
        """Caminho feliz: tipo deve ser 'loja'."""
        tipo, _, _ = gerador_padrao.gerar_loja()
        assert tipo == "loja"

    def test_retorna_conteudo_none(self, gerador_padrao):
        """
        Caminho feliz: conteudo deve ser None.
        A loja é instanciada pela Masmorra ao tratar o resultado.
        """
        _, conteudo, _ = gerador_padrao.gerar_loja()
        assert conteudo is None

    def test_retorna_descricao_string_nao_vazia(self, gerador_padrao):
        """Caminho feliz: descrição deve ser uma string não vazia."""
        _, _, descricao = gerador_padrao.gerar_loja()
        assert isinstance(descricao, str)
        assert len(descricao) > 0

    def test_retorna_tupla_com_tres_elementos(self, gerador_padrao):
        """Caminho feliz: deve retornar exatamente 3 elementos (compatível com Masmorra)."""
        resultado = gerador_padrao.gerar_loja()
        assert isinstance(resultado, tuple)
        assert len(resultado) == 3

    def test_descricao_do_mercador_e_consistente(self, gerador_padrao):
        """
        Invariante: a descrição da loja deve ser sempre a mesma
        (não é aleatória — é texto fixo do mercador).
        """
        _, _, desc1 = gerador_padrao.gerar_loja()
        _, _, desc2 = gerador_padrao.gerar_loja()
        assert desc1 == desc2


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 7 — gerar_item() direto
# ══════════════════════════════════════════════════════════════════════════════

class TestGeradorItem:
    """Testa o método gerar_item() de forma isolada."""

    def test_retorna_tipo_item(self, gerador_padrao):
        """Caminho feliz: tipo deve ser 'item'."""
        assert gerador_padrao.gerar_item()[0] == "item"

    def test_retorna_instancia_de_item(self, gerador_padrao):
        """Caminho feliz: conteúdo deve ser instância de Item."""
        _, conteudo, _ = gerador_padrao.gerar_item()
        assert isinstance(conteudo, Item)

    def test_retorna_descricao_passada(self, gerador_padrao):
        """Caminho feliz: descrição passada deve ser retornada na tupla."""
        _, _, descricao = gerador_padrao.gerar_item(descricao="Sala teste")
        assert descricao == "Sala teste"

    def test_retorna_descricao_vazia_por_padrao(self, gerador_padrao):
        """Borda: sem descrição fornecida, terceiro elemento deve ser string vazia."""
        assert gerador_padrao.gerar_item()[2] == ""

    def test_item_retornado_pertence_ao_catalogo(self, gerador_padrao):
        """Invariante: em 20 chamadas, todos os itens devem ser do catálogo."""
        nomes_validos = {i.nome for i in CATALOGO_ITENS}
        for _ in range(20):
            _, item, _ = gerador_padrao.gerar_item()
            assert item.nome in nomes_validos

    def test_catalogo_contem_itens_de_esquiva(self, gerador_padrao):
        """
        Caminho feliz (novo v2): CATALOGO_ITENS deve conter itens com bonus_esq.
        Verifica que a expansão do catálogo foi aplicada corretamente.
        """
        itens_esq = [i for i in CATALOGO_ITENS if i.bonus_esq > 0]
        assert len(itens_esq) >= 1


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 8 — gerar_inimigo() direto
# ══════════════════════════════════════════════════════════════════════════════

class TestGeradorInimigo:
    """Testa o método gerar_inimigo() de forma isolada."""

    def test_retorna_tipo_inimigo(self, gerador_padrao):
        """Caminho feliz: tipo deve ser 'inimigo'."""
        assert gerador_padrao.gerar_inimigo(andar=1)[0] == "inimigo"

    def test_retorna_instancia_de_inimigo(self, gerador_padrao):
        """Caminho feliz: conteúdo deve ser instância de Inimigo."""
        _, conteudo, _ = gerador_padrao.gerar_inimigo(andar=1)
        assert isinstance(conteudo, Inimigo)

    def test_retorna_descricao_passada(self, gerador_padrao):
        """Caminho feliz: descrição fornecida deve aparecer na tupla."""
        _, _, descricao = gerador_padrao.gerar_inimigo(andar=1, descricao="Caverna.")
        assert descricao == "Caverna."

    def test_retorna_descricao_vazia_por_padrao(self, gerador_padrao):
        """Borda: sem descrição fornecida, terceiro elemento deve ser string vazia."""
        assert gerador_padrao.gerar_inimigo(andar=1)[2] == ""

    def test_andar_zero_levanta_value_error(self, gerador_padrao):
        """Exceção: andar=0 deve lançar ValueError."""
        with pytest.raises(ValueError):
            gerador_padrao.gerar_inimigo(andar=0)

    def test_andar_negativo_levanta_value_error(self, gerador_padrao):
        """Exceção: andar negativo deve lançar ValueError."""
        with pytest.raises(ValueError):
            gerador_padrao.gerar_inimigo(andar=-3)

    def test_inimigo_tem_moedas_nao_negativas(self, gerador_padrao):
        """Caminho feliz (novo v2): inimigo gerado deve ter moedas >= 0."""
        _, inimigo, _ = gerador_padrao.gerar_inimigo(andar=1)
        assert inimigo.moedas >= 0

    @pytest.mark.parametrize("andar", [1, 3, 5, 10])
    def test_inimigo_valido_em_varios_andares(self, gerador_padrao, andar):
        """Parametrizado: inimigo deve ser válido em qualquer andar."""
        _, inimigo, _ = gerador_padrao.gerar_inimigo(andar=andar)
        assert inimigo.hp  > 0
        assert inimigo.atk > 0
        assert inimigo.dificuldade >= 1
        assert inimigo.moedas >= 0


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 9 — Fake Gerador (Stub)
# ══════════════════════════════════════════════════════════════════════════════

class TestFakeGerador:
    """Demonstra o padrão FakeGerador (stub) para isolar Masmorra nos testes."""

    def test_fake_gerador_item_retorna_tipo_correto(self):
        """Stub de item: deve retornar tipo 'item'."""
        item_fixo = Item("Poção Teste", bonus_hp=10)
        class FakeGeradorItem:
            def gerar_sala(self, andar=1):
                return ("item", item_fixo, "Sala de teste.")
        tipo, conteudo, desc = FakeGeradorItem().gerar_sala()
        assert tipo == "item" and conteudo == item_fixo

    def test_fake_gerador_inimigo_retorna_tipo_correto(self):
        """Stub de inimigo: deve retornar tipo 'inimigo'."""
        inimigo_fixo = Inimigo("Dummy", hp=5, atk=1, dificuldade=1, xp=10, moedas=2)
        class FakeGeradorInimigo:
            def gerar_sala(self, andar=1):
                return ("inimigo", inimigo_fixo, "Corredor.")
        tipo, conteudo, _ = FakeGeradorInimigo().gerar_sala()
        assert tipo == "inimigo" and conteudo == inimigo_fixo

    def test_fake_gerador_loja_retorna_tipo_correto(self):
        """
        Stub de loja (novo v2): deve retornar tipo 'loja' com conteudo None.
        Permite testar a Masmorra sem instanciar a Loja real.
        """
        class FakeGeradorLoja:
            def gerar_sala(self, andar=1):
                return ("loja", None, "Mercador apareceu.")
        tipo, conteudo, desc = FakeGeradorLoja().gerar_sala()
        assert tipo == "loja"
        assert conteudo is None
        assert desc == "Mercador apareceu."