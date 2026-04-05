"""
Suíte de testes unitários para jogo/entidades/item.py — v2

Mudanças em relação à versão anterior:
  - Item agora aceita 'bonus_esq' (bônus de esquiva).
  - Regra de item inútil atualizada: os TRÊS bônus precisam ser zero
    para lançar ValueError (antes eram dois).
  - Bloco 1: testes de validação de bonus_esq negativo adicionados.
  - Bloco 5 (novo): testa usar() com bonus_esq — integração com aumenta_esq().
  - conftest: nova fixture 'item_esquiva' disponível globalmente.

Execute com:
    pytest tests/test_item.py -v
    pytest tests/test_item.py -v --tb=short
"""

import pytest
from unittest.mock import MagicMock
from jogo.entidades.item    import Item
from jogo.entidades.jogador import Jogador


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 1 — Criação e validação do __init__
# ══════════════════════════════════════════════════════════════════════════════

class TestCriacaoItem:
    """Testa a criação de instâncias de Item e validação dos parâmetros."""

    def test_item_cura_criado_corretamente(self, item_cura):
        """Caminho feliz: item de cura deve ter bonus_hp e nome corretos."""
        assert item_cura.nome      == "Elixir Vital"
        assert item_cura.bonus_hp  == 5
        assert item_cura.bonus_atk == 0
        assert item_cura.bonus_esq == 0.0   # ← novo atributo v2

    def test_item_ataque_criado_corretamente(self, item_ataque):
        """Caminho feliz: item de ataque deve ter bonus_atk e nome corretos."""
        assert item_ataque.nome      == "Poção de Força"
        assert item_ataque.bonus_atk == 3
        assert item_ataque.bonus_hp  == 0
        assert item_ataque.bonus_esq == 0.0

    def test_item_misto_criado_corretamente(self, item_misto):
        """Caminho feliz: item misto deve ter ambos os bônus corretos."""
        assert item_misto.bonus_atk == 2
        assert item_misto.bonus_hp  == 3

    def test_item_esquiva_criado_corretamente(self, item_esquiva):
        """Caminho feliz (novo v2): item de esquiva deve ter bonus_esq correto."""
        assert item_esquiva.nome      == "Poção do Mestre Gato"
        assert item_esquiva.bonus_esq == 0.1
        assert item_esquiva.bonus_atk == 0
        assert item_esquiva.bonus_hp  == 0

    def test_item_com_todos_os_bonus(self):
        """Caminho feliz (novo v2): item com atk, hp e esq simultâneos."""
        item = Item("Tônico Supremo", bonus_atk=2, bonus_hp=5, bonus_esq=0.1)
        assert item.bonus_atk == 2
        assert item.bonus_hp  == 5
        assert item.bonus_esq == 0.1

    @pytest.mark.parametrize("nome_invalido", ["", None, 0, True])
    def test_nome_invalido_levanta_value_error(self, nome_invalido):
        """Exceção: nome inválido deve lançar ValueError."""
        with pytest.raises(ValueError):
            Item(nome_invalido, bonus_hp=5)

    def test_bonus_atk_negativo_levanta_value_error(self):
        """Exceção: bonus_atk negativo deve lançar ValueError."""
        with pytest.raises(ValueError):
            Item("Item Maldito", bonus_atk=-1)

    def test_bonus_hp_negativo_levanta_value_error(self):
        """Exceção: bonus_hp negativo deve lançar ValueError."""
        with pytest.raises(ValueError):
            Item("Veneno", bonus_hp=-3)

    def test_bonus_esq_negativo_levanta_value_error(self):
        """Exceção (novo v2): bonus_esq negativo deve lançar ValueError."""
        with pytest.raises(ValueError):
            Item("Maldicao", bonus_esq=-0.1)

    def test_todos_bonus_zero_levanta_value_error(self):
        """
        Exceção (atualizado v2): item sem NENHUM dos três bônus
        não deve ser criado. A regra agora verifica atk, hp E esq.
        """
        with pytest.raises(ValueError):
            Item("Item Inútil", bonus_atk=0, bonus_hp=0, bonus_esq=0)

    def test_apenas_bonus_esq_e_valido(self):
        """
        Borda (novo v2): item com apenas bonus_esq > 0 deve ser criado.
        Isso verifica que a validação reconhece esq como bônus suficiente.
        """
        item = Item("Elixir Gato", bonus_esq=0.05)
        assert item.bonus_esq == 0.05
        assert item.bonus_atk == 0
        assert item.bonus_hp  == 0

    def test_apenas_bonus_atk_e_valido(self):
        """Borda: item com apenas bonus_atk > 0 deve ser criado."""
        item = Item("Adaga", bonus_atk=2)
        assert item.bonus_atk == 2

    def test_apenas_bonus_hp_e_valido(self):
        """Borda: item com apenas bonus_hp > 0 deve ser criado."""
        item = Item("Poção", bonus_hp=10)
        assert item.bonus_hp == 10


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 2 — usar() com bonus_hp
# ══════════════════════════════════════════════════════════════════════════════

class TestUsarItemCura:
    """Testa o uso de itens de cura no jogador."""

    def test_usar_cura_aumenta_hp_do_jogador(self, item_cura, jogador_ferido):
        """Caminho feliz: usar item de cura deve aumentar o hp do jogador."""
        hp_antes = jogador_ferido.hp
        item_cura.usar(jogador_ferido)
        assert jogador_ferido.hp == hp_antes + item_cura.bonus_hp

    def test_usar_cura_retorna_hp_recuperado_no_dict(self, item_cura, jogador_ferido):
        """Caminho feliz: resultado deve conter chave 'hp' com valor efetivo."""
        resultado = item_cura.usar(jogador_ferido)
        assert "hp" in resultado
        assert resultado["hp"] == item_cura.bonus_hp

    def test_usar_cura_nao_ultrapassa_hp_maximo(self, jogador_padrao):
        """Limite: cura não deve ultrapassar hp_max do jogador."""
        item = Item("Mega Poção", bonus_hp=9999)
        item.usar(jogador_padrao)
        assert jogador_padrao.hp <= jogador_padrao.hp_max

    def test_usar_cura_em_hp_cheio_retorna_zero(self, jogador_padrao):
        """Borda: usar cura em hp cheio deve retornar hp=0 no resultado."""
        resultado = Item("Poção Desperdiçada", bonus_hp=10).usar(jogador_padrao)
        assert resultado["hp"] == 0

    def test_usar_cura_nao_inclui_chave_atk(self, item_cura, jogador_ferido):
        """Borda: resultado de item só de cura não deve ter chave 'atk'."""
        assert "atk" not in item_cura.usar(jogador_ferido)

    def test_usar_cura_nao_inclui_chave_esq(self, item_cura, jogador_ferido):
        """Borda (novo v2): resultado de item só de cura não deve ter chave 'esq'."""
        assert "esq" not in item_cura.usar(jogador_ferido)

    @pytest.mark.parametrize("bonus_hp,hp_inicial,hp_esperado", [
        (3,  5,  8),
        (5,  5, 10),
        (15, 5, 20),
        (99, 5, 20),
    ])
    def test_cura_parametrizada(self, bonus_hp, hp_inicial, hp_esperado):
        """Parametrizado: verifica hp resultante para diferentes bônus de cura."""
        jogador = Jogador("Teste", hp=20, atk=5)
        jogador.hp = hp_inicial
        Item("Poção", bonus_hp=bonus_hp).usar(jogador)
        assert jogador.hp == hp_esperado


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 3 — usar() com bonus_atk
# ══════════════════════════════════════════════════════════════════════════════

class TestUsarItemAtaque:
    """Testa o uso de itens de ataque no jogador."""

    def test_usar_ataque_aumenta_atk_do_jogador(self, item_ataque, jogador_padrao):
        """Caminho feliz: usar item de ataque deve incrementar o atk do jogador."""
        atk_antes = jogador_padrao.atk
        item_ataque.usar(jogador_padrao)
        assert jogador_padrao.atk == atk_antes + item_ataque.bonus_atk

    def test_usar_ataque_retorna_bonus_no_dict(self, item_ataque, jogador_padrao):
        """Caminho feliz: resultado deve conter chave 'atk' com o bônus concedido."""
        resultado = item_ataque.usar(jogador_padrao)
        assert "atk" in resultado
        assert resultado["atk"] == item_ataque.bonus_atk

    def test_usar_ataque_nao_altera_hp(self, item_ataque, jogador_padrao):
        """Garantia: item de ataque não deve alterar o hp do jogador."""
        hp_antes = jogador_padrao.hp
        item_ataque.usar(jogador_padrao)
        assert jogador_padrao.hp == hp_antes

    def test_usar_ataque_nao_inclui_chave_hp(self, item_ataque, jogador_padrao):
        """Borda: resultado de item só de ataque não deve ter chave 'hp'."""
        assert "hp" not in item_ataque.usar(jogador_padrao)

    def test_usar_ataque_nao_inclui_chave_esq(self, item_ataque, jogador_padrao):
        """Borda (novo v2): resultado de item só de ataque não deve ter chave 'esq'."""
        assert "esq" not in item_ataque.usar(jogador_padrao)

    def test_usar_ataque_acumula_em_multiplos_usos(self, jogador_padrao):
        """Acúmulo: múltiplos itens de ataque devem se acumular corretamente."""
        atk_antes = jogador_padrao.atk
        Item("Espada", bonus_atk=3).usar(jogador_padrao)
        Item("Adaga",  bonus_atk=2).usar(jogador_padrao)
        assert jogador_padrao.atk == atk_antes + 5

    @pytest.mark.parametrize("bonus_atk,atk_inicial,atk_esperado", [
        (1,  5,  6),
        (3,  5,  8),
        (10, 5, 15),
    ])
    def test_ataque_parametrizado(self, bonus_atk, atk_inicial, atk_esperado):
        """Parametrizado: verifica atk resultante para diferentes bônus."""
        jogador = Jogador("Teste", hp=20, atk=atk_inicial)
        Item("Arma", bonus_atk=bonus_atk).usar(jogador)
        assert jogador.atk == atk_esperado


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 4 — usar() com bônus combinados (misto)
# ══════════════════════════════════════════════════════════════════════════════

class TestUsarItemMisto:
    """Testa o uso de itens com bonus_atk e bonus_hp simultaneamente."""

    def test_usar_misto_aplica_ambos_os_bonus(self, item_misto, jogador_ferido):
        """Caminho feliz: ambos os bônus devem ser aplicados ao jogador."""
        atk_antes = jogador_ferido.atk
        hp_antes  = jogador_ferido.hp
        item_misto.usar(jogador_ferido)
        assert jogador_ferido.atk == atk_antes + item_misto.bonus_atk
        assert jogador_ferido.hp  == hp_antes  + item_misto.bonus_hp

    def test_usar_misto_retorna_ambas_as_chaves(self, item_misto, jogador_ferido):
        """Caminho feliz: resultado deve conter as chaves 'atk' e 'hp'."""
        resultado = item_misto.usar(jogador_ferido)
        assert "atk" in resultado
        assert "hp"  in resultado

    def test_usar_misto_valores_corretos_no_resultado(self, item_misto, jogador_ferido):
        """Caminho feliz: valores no resultado devem refletir os bônus corretos."""
        resultado = item_misto.usar(jogador_ferido)
        assert resultado["atk"] == item_misto.bonus_atk
        assert resultado["hp"]  == item_misto.bonus_hp


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 5 (NOVO v2) — usar() com bonus_esq
# ══════════════════════════════════════════════════════════════════════════════

class TestUsarItemEsquiva:
    """Testa o uso de itens de esquiva no jogador — novo na v2."""

    def test_usar_esquiva_aumenta_esq_do_jogador(self, item_esquiva, jogador_padrao):
        """Caminho feliz: usar item de esquiva deve aumentar a esq do jogador."""
        esq_antes = jogador_padrao.esq
        item_esquiva.usar(jogador_padrao)
        assert round(jogador_padrao.esq, 2) == round(esq_antes + item_esquiva.bonus_esq, 2)

    def test_usar_esquiva_retorna_esq_no_dict(self, item_esquiva, jogador_padrao):
        """Caminho feliz: resultado deve conter chave 'esq' com valor aplicado."""
        resultado = item_esquiva.usar(jogador_padrao)
        assert "esq" in resultado
        assert round(resultado["esq"], 2) == round(item_esquiva.bonus_esq, 2)

    def test_usar_esquiva_nao_altera_hp(self, item_esquiva, jogador_padrao):
        """Garantia: item de esquiva não deve alterar o hp do jogador."""
        hp_antes = jogador_padrao.hp
        item_esquiva.usar(jogador_padrao)
        assert jogador_padrao.hp == hp_antes

    def test_usar_esquiva_nao_altera_atk(self, item_esquiva, jogador_padrao):
        """Garantia: item de esquiva não deve alterar o atk do jogador."""
        atk_antes = jogador_padrao.atk
        item_esquiva.usar(jogador_padrao)
        assert jogador_padrao.atk == atk_antes

    def test_usar_esquiva_nao_inclui_chave_hp(self, item_esquiva, jogador_padrao):
        """Borda: resultado de item só de esquiva não deve ter chave 'hp'."""
        assert "hp" not in item_esquiva.usar(jogador_padrao)

    def test_usar_esquiva_nao_inclui_chave_atk(self, item_esquiva, jogador_padrao):
        """Borda: resultado de item só de esquiva não deve ter chave 'atk'."""
        assert "atk" not in item_esquiva.usar(jogador_padrao)

    def test_usar_esquiva_respeita_esq_max(self, jogador_padrao):
        """Limite: esquiva não deve ultrapassar esq_max=1.0 mesmo com bônus enorme."""
        item_gigante = Item("Elixir Divino", bonus_esq=9999.0)
        item_gigante.usar(jogador_padrao)
        assert jogador_padrao.esq <= jogador_padrao.esq_max

    def test_usar_esquiva_acumula_em_multiplos_usos(self, jogador_padrao):
        """Acúmulo: múltiplos itens de esquiva devem se acumular até o limite."""
        esq_antes = jogador_padrao.esq
        Item("Poção Gato 1", bonus_esq=0.1).usar(jogador_padrao)
        Item("Poção Gato 2", bonus_esq=0.1).usar(jogador_padrao)
        assert round(jogador_padrao.esq, 2) == round(min(1.0, esq_antes + 0.2), 2)

    @pytest.mark.parametrize("bonus_esq,esq_inicial,esq_esperada", [
        (0.1, 0.3, 0.4),
        (0.2, 0.3, 0.5),
        (0.7, 0.3, 1.0),   # limitado ao max=1.0
        (9.9, 0.3, 1.0),
    ])
    def test_esquiva_parametrizada(self, bonus_esq, esq_inicial, esq_esperada):
        """Parametrizado: verifica esq resultante para diferentes bônus de esquiva."""
        jogador = Jogador("Teste", hp=20, atk=5, esq=esq_inicial)
        Item("Elixir", bonus_esq=bonus_esq).usar(jogador)
        assert round(jogador.esq, 2) == esq_esperada


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 6 — usar() com todos os bônus combinados (triplo)
# ══════════════════════════════════════════════════════════════════════════════

class TestUsarItemTriplo:
    """Testa itens com os três bônus simultaneamente — novo na v2."""

    def test_item_triplo_aplica_todos_os_bonus(self, jogador_ferido):
        """
        Caminho feliz: item com atk, hp e esq deve aplicar todos os três.
        """
        item = Item("Tônico Supremo", bonus_atk=2, bonus_hp=5, bonus_esq=0.1)
        atk_antes = jogador_ferido.atk
        hp_antes  = jogador_ferido.hp
        esq_antes = jogador_ferido.esq

        resultado = item.usar(jogador_ferido)

        assert jogador_ferido.atk == atk_antes + 2
        assert jogador_ferido.hp  == hp_antes  + 5
        assert round(jogador_ferido.esq, 2) == round(esq_antes + 0.1, 2)
        assert "atk" in resultado
        assert "hp"  in resultado
        assert "esq" in resultado

    def test_item_triplo_retorna_valores_corretos(self, jogador_ferido):
        """Caminho feliz: dict retornado deve conter os três bônus aplicados."""
        item = Item("Tônico Supremo", bonus_atk=2, bonus_hp=5, bonus_esq=0.1)
        resultado = item.usar(jogador_ferido)
        assert resultado["atk"] == 2
        assert resultado["hp"]  == 5
        assert round(resultado["esq"], 2) == 0.1


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 7 — Exceções em usar()
# ══════════════════════════════════════════════════════════════════════════════

class TestUsarExcecoes:
    """Testa o tratamento de entradas inválidas em usar()."""

    def test_usar_com_jogador_none_levanta_value_error(self, item_cura):
        """Exceção: passar None como jogador deve lançar ValueError."""
        with pytest.raises(ValueError):
            item_cura.usar(None)

    def test_usar_ataque_com_jogador_none_levanta_value_error(self, item_ataque):
        """Exceção: None deve lançar ValueError independente do tipo de item."""
        with pytest.raises(ValueError):
            item_ataque.usar(None)

    def test_usar_esquiva_com_jogador_none_levanta_value_error(self, item_esquiva):
        """Exceção (novo v2): item de esquiva com None também deve lançar ValueError."""
        with pytest.raises(ValueError):
            item_esquiva.usar(None)


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 8 — usar() com Mock do Jogador (stub)
# ══════════════════════════════════════════════════════════════════════════════

class TestUsarComMockJogador:
    """
    Testa usar() isolando a dependência do Jogador via MagicMock.
    Verifica que o item chama os métodos corretos.
    """

    def test_item_cura_chama_curar_no_jogador(self, item_cura):
        """Mock: usar() deve chamar jogador.curar() com o bonus_hp correto."""
        jogador_mock = MagicMock()
        jogador_mock.curar.return_value = item_cura.bonus_hp
        item_cura.usar(jogador_mock)
        jogador_mock.curar.assert_called_once_with(item_cura.bonus_hp)

    def test_item_ataque_incrementa_atk_diretamente(self, item_ataque):
        """Mock: usar() deve incrementar jogador.atk diretamente."""
        jogador_mock     = MagicMock()
        jogador_mock.atk = 5
        item_ataque.usar(jogador_mock)
        assert jogador_mock.atk == 5 + item_ataque.bonus_atk

    def test_item_esquiva_chama_aumenta_esq_no_jogador(self, item_esquiva):
        """
        Mock (novo v2): usar() deve chamar jogador.aumenta_esq()
        com o bonus_esq correto.
        """
        jogador_mock = MagicMock()
        jogador_mock.aumenta_esq.return_value = item_esquiva.bonus_esq
        item_esquiva.usar(jogador_mock)
        jogador_mock.aumenta_esq.assert_called_once_with(item_esquiva.bonus_esq)

    def test_item_cura_nao_chama_curar_quando_apenas_atk(self):
        """Mock: item com apenas bonus_atk NÃO deve chamar curar() no jogador."""
        item         = Item("Espada Pura", bonus_atk=5)
        jogador_mock = MagicMock()
        jogador_mock.atk = 3
        item.usar(jogador_mock)
        jogador_mock.curar.assert_not_called()

    def test_item_esquiva_nao_chama_aumenta_esq_quando_apenas_hp(self, item_cura):
        """Mock (novo v2): item de cura NÃO deve chamar aumenta_esq()."""
        jogador_mock = MagicMock()
        jogador_mock.curar.return_value = 5
        item_cura.usar(jogador_mock)
        jogador_mock.aumenta_esq.assert_not_called()


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 9 — Representação
# ══════════════════════════════════════════════════════════════════════════════

class TestRepresentacao:
    """Testa a representação em string do item."""

    def test_repr_contem_nome(self, item_cura):
        """__repr__ deve conter o nome do item."""
        assert "Elixir Vital" in repr(item_cura)

    def test_repr_contem_bonus_hp(self, item_cura):
        """__repr__ deve conter o bonus_hp."""
        assert "5" in repr(item_cura)

    def test_repr_contem_bonus_atk(self, item_ataque):
        """__repr__ deve conter o bonus_atk."""
        assert "3" in repr(item_ataque)