# randongeon/tests/test_loja.py

"""
Suíte de testes unitários para jogo/entidades/loja.py — NOVO v2

Cobre:
  - __init__: estrutura do estoque e das ofertas
  - comprar(): caminho feliz, moedas insuficientes, índice inválido
  - Integração com Jogador: atributos alterados após compra
  - Mocks de random.sample para controlar quais itens são ofertados

Execute com:
    pytest tests/test_loja.py -v
"""

import pytest
from unittest.mock import patch
from jogo.entidades.loja    import Loja
from jogo.entidades.jogador import Jogador
from jogo.entidades.item    import Item


# ══════════════════════════════════════════════════════════════════════════════
# FIXTURES LOCAIS
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def loja() -> Loja:
    """Loja com ofertas aleatórias (comportamento padrão)."""
    return Loja()


@pytest.fixture
def jogador_rico() -> Jogador:
    """Jogador com moedas suficientes para comprar qualquer item."""
    return Jogador("Rico", hp=20, atk=5, moedas=100)


@pytest.fixture
def jogador_pobre() -> Jogador:
    """Jogador sem moedas para comprar nenhum item."""
    return Jogador("Pobre", hp=10, atk=3, moedas=0)


@pytest.fixture
def loja_com_ofertas_fixas():
    """
    Loja com ofertas controladas via mock de random.sample.
    Retorna sempre os dois primeiros itens do estoque: índices 0 e 1.
    """
    with patch("jogo.entidades.loja.random.sample") as mock_sample:
        l = Loja()
        mock_sample.side_effect = lambda populacao, k: populacao[:k]
        l2 = Loja()
    return l2


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 1 — Inicialização da Loja
# ══════════════════════════════════════════════════════════════════════════════

class TestInicializacaoLoja:
    """Testa a criação da Loja e sua estrutura de dados."""

    def test_estoque_tem_quatro_itens(self, loja):
        """Caminho feliz: o estoque fixo da loja deve ter exatamente 4 itens."""
        assert len(loja.estoque) == 4

    def test_ofertas_tem_dois_itens(self, loja):
        """Caminho feliz: o mercador apresenta exatamente 2 ofertas por visita."""
        assert len(loja.ofertas) == 2

    def test_ofertas_sao_subconjunto_do_estoque(self, loja):
        """Caminho feliz: as ofertas devem vir do estoque, não de fora."""
        for oferta in loja.ofertas:
            assert oferta in loja.estoque

    def test_cada_oferta_tem_chave_item(self, loja):
        """Caminho feliz: cada oferta deve ter a chave 'item'."""
        for oferta in loja.ofertas:
            assert "item" in oferta

    def test_cada_oferta_tem_chave_preco(self, loja):
        """Caminho feliz: cada oferta deve ter a chave 'preco'."""
        for oferta in loja.ofertas:
            assert "preco" in oferta

    def test_item_de_cada_oferta_e_instancia_de_item(self, loja):
        """Caminho feliz: o valor de 'item' em cada oferta deve ser um Item."""
        for oferta in loja.ofertas:
            assert isinstance(oferta["item"], Item)

    def test_preco_de_cada_oferta_e_positivo(self, loja):
        """Caminho feliz: todos os preços do estoque devem ser > 0."""
        for oferta in loja.estoque:
            assert oferta["preco"] > 0

    def test_ofertas_diferentes_entre_instancias(self):
        """
        Probabilístico: duas instâncias de Loja raramente devem ter
        as mesmas ofertas (1 em 6 de chance de serem iguais).
        Rodamos 10 vezes e esperamos ao menos uma diferença.
        """
        resultados = set()
        for _ in range(10):
            l = Loja()
            nomes = tuple(sorted(o["item"].nome for o in l.ofertas))
            resultados.add(nomes)
        # Com 4 itens escolhendo 2, há 6 combinações possíveis
        # Em 10 tentativas, a chance de sempre cair na mesma é < 1%
        assert len(resultados) > 1


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 2 — comprar(): caminho feliz
# ══════════════════════════════════════════════════════════════════════════════

class TestComprarCaminhoFeliz:
    """Testa compras bem-sucedidas na loja."""

    def test_compra_bem_sucedida_retorna_sucesso_true(self, loja, jogador_rico):
        """Caminho feliz: compra válida deve retornar {'sucesso': True}."""
        resultado = loja.comprar(0, jogador_rico)
        assert resultado["sucesso"] is True

    def test_compra_desconta_moedas_do_jogador(self, loja, jogador_rico):
        """Caminho feliz: moedas do jogador devem diminuir pelo preço do item."""
        preco = loja.ofertas[0]["preco"]
        moedas_antes = jogador_rico.moedas
        loja.comprar(0, jogador_rico)
        assert jogador_rico.moedas == moedas_antes - preco

    def test_compra_remove_item_das_ofertas(self, loja, jogador_rico):
        """Caminho feliz: item comprado deve ser removido das ofertas."""
        item_comprado = loja.ofertas[0]["item"]
        loja.comprar(0, jogador_rico)
        nomes_restantes = [o["item"].nome for o in loja.ofertas]
        assert item_comprado.nome not in nomes_restantes

    def test_compra_reduz_ofertas_em_um(self, loja, jogador_rico):
        """Caminho feliz: após uma compra, ofertas deve ter 1 item a menos."""
        qtd_antes = len(loja.ofertas)
        loja.comprar(0, jogador_rico)
        assert len(loja.ofertas) == qtd_antes - 1

    def test_compra_retorna_mensagem_string(self, loja, jogador_rico):
        """Caminho feliz: resultado deve conter chave 'mensagem' com string."""
        resultado = loja.comprar(0, jogador_rico)
        assert "mensagem" in resultado
        assert isinstance(resultado["mensagem"], str)

    def test_compra_adiciona_item_ao_inventario(self, jogador_rico):
        """
        Caminho feliz (v3): item comprado deve ser adicionado ao inventário do
        jogador (não mais aplicado diretamente). O efeito só é aplicado quando
        o jogador usa o item via combatUseItem.
        """
        item_atk = Item("Poção de Força", bonus_atk=2)
        oferta_fixa = [{"item": item_atk, "preco": 5}]

        with patch("jogo.entidades.loja.random.sample", return_value=oferta_fixa):
            loja_controlada = Loja()

        atk_antes = jogador_rico.atk
        loja_controlada.comprar(0, jogador_rico)
        # ATK NÃO muda — o item está no inventário.
        assert jogador_rico.atk == atk_antes
        assert len(jogador_rico.inventario) == 1
        assert jogador_rico.inventario[0].nome == "Poção de Força"

    def test_pode_comprar_segundo_item(self, loja, jogador_rico):
        """Caminho feliz: deve ser possível comprar o segundo item (índice 1)."""
        resultado = loja.comprar(1, jogador_rico)
        assert resultado["sucesso"] is True


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 3 — comprar(): casos de falha
# ══════════════════════════════════════════════════════════════════════════════

class TestComprarFalha:
    """Testa comportamentos de falha em compras."""

    def test_moedas_insuficientes_retorna_sucesso_false(self, loja, jogador_pobre):
        """Exceção: jogador sem moedas não deve conseguir comprar."""
        resultado = loja.comprar(0, jogador_pobre)
        assert resultado["sucesso"] is False

    def test_moedas_insuficientes_nao_altera_jogador(self, loja, jogador_pobre):
        """Exceção: falha por moedas não deve alterar atributos do jogador."""
        atk_antes    = jogador_pobre.atk
        hp_antes     = jogador_pobre.hp
        moedas_antes = jogador_pobre.moedas
        loja.comprar(0, jogador_pobre)
        assert jogador_pobre.atk    == atk_antes
        assert jogador_pobre.hp     == hp_antes
        assert jogador_pobre.moedas == moedas_antes

    def test_moedas_insuficientes_nao_remove_oferta(self, loja, jogador_pobre):
        """Exceção: falha por moedas não deve remover o item das ofertas."""
        qtd_antes = len(loja.ofertas)
        loja.comprar(0, jogador_pobre)
        assert len(loja.ofertas) == qtd_antes

    def test_moedas_insuficientes_retorna_mensagem(self, loja, jogador_pobre):
        """Exceção: mensagem de falha deve indicar o problema."""
        resultado = loja.comprar(0, jogador_pobre)
        assert "mensagem" in resultado
        assert len(resultado["mensagem"]) > 0

    def test_indice_negativo_retorna_sucesso_false(self, loja, jogador_rico):
        """Exceção: índice negativo deve retornar falha."""
        assert loja.comprar(-1, jogador_rico)["sucesso"] is False

    def test_indice_fora_do_range_retorna_sucesso_false(self, loja, jogador_rico):
        """Exceção: índice maior que as ofertas disponíveis deve retornar falha."""
        assert loja.comprar(99, jogador_rico)["sucesso"] is False

    def test_indice_exato_no_limite_retorna_falha(self, loja, jogador_rico):
        """
        Borda: índice igual ao tamanho das ofertas (fora do range por um)
        deve retornar falha (off-by-one).
        """
        indice_invalido = len(loja.ofertas)
        assert loja.comprar(indice_invalido, jogador_rico)["sucesso"] is False

    def test_comprar_exatamente_com_moedas_suficientes(self, loja):
        """
        Borda: jogador com moedas exatamente iguais ao preço deve conseguir comprar.
        """
        preco_exato = loja.ofertas[0]["preco"]
        jogador_justo = Jogador("Justo", hp=20, atk=5, moedas=preco_exato)
        resultado = loja.comprar(0, jogador_justo)
        assert resultado["sucesso"] is True
        assert jogador_justo.moedas == 0

    def test_comprar_com_uma_moeda_a_menos_falha(self, loja):
        """
        Borda: jogador com exatamente uma moeda a menos do preço não deve comprar.
        """
        preco = loja.ofertas[0]["preco"]
        jogador_quase = Jogador("Quase", hp=20, atk=5, moedas=preco - 1)
        resultado = loja.comprar(0, jogador_quase)
        assert resultado["sucesso"] is False


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 4 — Integração com Jogador
# ══════════════════════════════════════════════════════════════════════════════

class TestLojaIntegracaoJogador:
    """Testa o efeito completo de compras no estado do jogador."""

    def test_comprar_item_cura_vai_para_inventario(self, jogador_rico):
        """
        Integração (v3): Elixir Vital comprado vai para o inventário; o HP só
        é restaurado quando o jogador usa o item.
        """
        item_cura_fixo = Item("Elixir Vital", bonus_hp=8)
        oferta_fixa    = [{"item": item_cura_fixo, "preco": 10},
                          {"item": Item("Outro", bonus_atk=1), "preco": 5}]
        with patch("jogo.entidades.loja.random.sample", return_value=oferta_fixa):
            loja_ctrl = Loja()

        jogador_rico.hp = 10
        loja_ctrl.comprar(0, jogador_rico)
        # HP não muda na compra; item está no inventário.
        assert jogador_rico.hp == 10
        assert any(i.nome == "Elixir Vital" for i in jogador_rico.inventario)

    def test_comprar_item_ataque_vai_para_inventario(self, jogador_rico):
        """
        Integração (v3): item de ataque comprado vai para inventário.
        ATK só aumenta quando o jogador o usa.
        """
        item_atk_fixo = Item("Grande Poção de Força", bonus_atk=2)
        oferta_fixa   = [{"item": item_atk_fixo, "preco": 15},
                         {"item": Item("Outro", bonus_hp=1), "preco": 5}]
        with patch("jogo.entidades.loja.random.sample", return_value=oferta_fixa):
            loja_ctrl = Loja()

        atk_antes = jogador_rico.atk
        loja_ctrl.comprar(0, jogador_rico)
        assert jogador_rico.atk == atk_antes
        assert any(i.nome == "Grande Poção de Força" for i in jogador_rico.inventario)

    def test_comprar_item_esquiva_vai_para_inventario(self, jogador_rico):
        """
        Integração (v3): item de esquiva comprado vai para inventário.
        """
        item_esq_fixo = Item("Elixir do Mestre Mosca", bonus_esq=0.1)
        oferta_fixa   = [{"item": item_esq_fixo, "preco": 20},
                         {"item": Item("Outro", bonus_atk=1), "preco": 5}]
        with patch("jogo.entidades.loja.random.sample", return_value=oferta_fixa):
            loja_ctrl = Loja()

        esq_antes = jogador_rico.esq
        loja_ctrl.comprar(0, jogador_rico)
        assert jogador_rico.esq == esq_antes
        assert any(i.nome == "Elixir do Mestre Mosca" for i in jogador_rico.inventario)

    def test_compras_multiplas_acumulam_no_inventario(self, jogador_rico):
        """
        Integração (v3): duas compras em sequência adicionam ambos os itens
        no inventário, sem alterar stats até o uso.
        """
        item1 = Item("Poção Força 1", bonus_atk=2)
        item2 = Item("Poção Força 2", bonus_atk=3)
        oferta_fixa = [{"item": item1, "preco": 10},
                       {"item": item2, "preco": 10}]
        with patch("jogo.entidades.loja.random.sample", return_value=oferta_fixa):
            loja_ctrl = Loja()

        atk_antes = jogador_rico.atk
        loja_ctrl.comprar(0, jogador_rico)   # compra item1
        loja_ctrl.comprar(0, jogador_rico)   # compra item2 (agora no índice 0)
        assert jogador_rico.atk == atk_antes
        nomes = [i.nome for i in jogador_rico.inventario]
        assert nomes == ["Poção Força 1", "Poção Força 2"]