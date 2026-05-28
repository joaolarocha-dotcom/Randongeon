"""
Testes para o sistema de inventário do Jogador.

Cobre: adicionar_item, usar_item, inventario_resumo.
"""

import pytest

from jogo.entidades.item import Item
from jogo.entidades.jogador import Jogador


@pytest.fixture
def erva() -> Item:
    return Item("Erva Medicinal", bonus_hp=3)


@pytest.fixture
def pocao_atk() -> Item:
    return Item("Poção de Força", bonus_atk=1)


class TestInventarioInicial:
    def test_inventario_comeca_vazio(self, jogador_padrao):
        assert jogador_padrao.inventario == []


class TestAdicionarItem:
    def test_adiciona_item_aumenta_tamanho(self, jogador_padrao, erva):
        jogador_padrao.adicionar_item(erva)
        assert len(jogador_padrao.inventario) == 1
        assert jogador_padrao.inventario[0] is erva

    def test_adiciona_multiplos_itens_preserva_ordem(self, jogador_padrao, erva, pocao_atk):
        jogador_padrao.adicionar_item(erva)
        jogador_padrao.adicionar_item(pocao_atk)
        assert [it.nome for it in jogador_padrao.inventario] == ["Erva Medicinal", "Poção de Força"]

    def test_adiciona_none_levanta_value_error(self, jogador_padrao):
        with pytest.raises(ValueError):
            jogador_padrao.adicionar_item(None)


class TestUsarItem:
    def test_usar_item_aplica_efeito_e_remove(self, jogador_padrao, pocao_atk):
        atk_antes = jogador_padrao.atk
        jogador_padrao.adicionar_item(pocao_atk)
        efeito = jogador_padrao.usar_item(0)
        assert efeito == {"atk": 1}
        assert jogador_padrao.atk == atk_antes + 1
        assert jogador_padrao.inventario == []

    def test_usar_item_cura_respeita_hp_max(self, jogador_padrao, erva):
        jogador_padrao.hp = 18  # hp_max=20 → cura efetiva = 2
        jogador_padrao.adicionar_item(erva)
        efeito = jogador_padrao.usar_item(0)
        assert efeito == {"hp": 2}
        assert jogador_padrao.hp == 20

    def test_usar_item_indice_invalido_levanta_index_error(self, jogador_padrao):
        with pytest.raises(IndexError):
            jogador_padrao.usar_item(0)

    def test_usar_item_indice_negativo_levanta_index_error(self, jogador_padrao, erva):
        jogador_padrao.adicionar_item(erva)
        with pytest.raises(IndexError):
            jogador_padrao.usar_item(-1)

    def test_usar_item_mantem_ordem_dos_restantes(self, jogador_padrao, erva, pocao_atk):
        jogador_padrao.adicionar_item(erva)
        jogador_padrao.adicionar_item(pocao_atk)
        jogador_padrao.usar_item(0)
        assert [it.nome for it in jogador_padrao.inventario] == ["Poção de Força"]


class TestInventarioResumo:
    def test_resumo_vazio_retorna_lista_vazia(self, jogador_padrao):
        assert jogador_padrao.inventario_resumo() == []

    def test_resumo_contem_atributos_serializaveis(self, jogador_padrao, erva, pocao_atk):
        jogador_padrao.adicionar_item(erva)
        jogador_padrao.adicionar_item(pocao_atk)
        resumo = jogador_padrao.inventario_resumo()
        assert resumo == [
            {"nome": "Erva Medicinal", "bonus_atk": 0, "bonus_hp": 3, "bonus_esq": 0},
            {"nome": "Poção de Força", "bonus_atk": 1, "bonus_hp": 0, "bonus_esq": 0},
        ]
