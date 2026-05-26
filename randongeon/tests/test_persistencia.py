"""
Testes do round-trip de serialização/desserialização do estado de jogo.

Cobre serializar_estado → desserializar_estado preserva: stats do jogador,
HP atual vs HP_max, inventário, andar, modo.
"""

import pytest

from jogo.entidades.item import Item
from jogo.entidades.jogador import Jogador
from jogo.sistemas.gerador import GeradorSala
from jogo.sistemas.masmorra import Masmorra
from jogo.sistemas.persistencia import (
    SAVE_VERSION,
    serializar_estado,
    desserializar_estado,
)


def _estado_completo() -> tuple[Jogador, Masmorra]:
    jogador = Jogador("Heroína", hp=25, atk=7, xp=120, esq=0.5, moedas=42)
    jogador.hp = 18
    jogador.adicionar_item(Item("Erva Medicinal", bonus_hp=3))
    jogador.adicionar_item(Item("Tônico do Guerreiro", bonus_atk=1, bonus_hp=2))
    masmorra = Masmorra(jogador, GeradorSala(), modo="infinite")
    masmorra.andar = 9
    return jogador, masmorra


class TestSerializacao:
    def test_payload_inclui_versao_e_metadados(self):
        jogador, masmorra = _estado_completo()
        data = serializar_estado(jogador, masmorra, "infinite")
        assert data["version"] == SAVE_VERSION
        assert data["playerName"] == "Heroína"
        assert data["andar"] == 9
        assert data["modo"] == "infinite"
        assert "savedAt" in data and isinstance(data["savedAt"], str)

    def test_payload_inclui_jogador_serializado(self):
        jogador, masmorra = _estado_completo()
        data = serializar_estado(jogador, masmorra, "infinite")
        assert data["jogador"]["nome"] == "Heroína"
        assert data["jogador"]["hp"] == 18
        assert data["jogador"]["hp_max"] == 25
        assert data["jogador"]["atk"] == 7
        assert data["jogador"]["xp"] == 120
        assert data["jogador"]["esq"] == 0.5
        assert data["jogador"]["moedas"] == 42
        assert len(data["jogador"]["inventario"]) == 2


class TestRoundTrip:
    def test_roundtrip_preserva_estado(self):
        jogador, masmorra = _estado_completo()
        data = serializar_estado(jogador, masmorra, "infinite")

        novo_jog, nova_mas, modo = desserializar_estado(data)

        assert modo == "infinite"
        assert nova_mas.modo == "infinite"
        assert nova_mas.andar == 9
        assert novo_jog.nome == "Heroína"
        assert novo_jog.hp == 18
        assert novo_jog.hp_max == 25
        assert novo_jog.atk == 7
        assert novo_jog.xp == 120
        assert novo_jog.esq == 0.5
        assert novo_jog.moedas == 42
        assert [it.nome for it in novo_jog.inventario] == [
            "Erva Medicinal",
            "Tônico do Guerreiro",
        ]

    def test_roundtrip_inventario_com_efeitos_intactos(self):
        jogador, masmorra = _estado_completo()
        data = serializar_estado(jogador, masmorra, "infinite")
        novo_jog, _, _ = desserializar_estado(data)
        tonico = novo_jog.inventario[1]
        assert tonico.bonus_atk == 1
        assert tonico.bonus_hp == 2


class TestValidacao:
    def test_versao_futura_levanta_value_error(self):
        jogador, masmorra = _estado_completo()
        data = serializar_estado(jogador, masmorra, "story")
        data["version"] = SAVE_VERSION + 1
        with pytest.raises(ValueError):
            desserializar_estado(data)

    def test_modo_invalido_levanta_value_error(self):
        jogador, masmorra = _estado_completo()
        data = serializar_estado(jogador, masmorra, "story")
        data["modo"] = "hardcore"
        with pytest.raises(ValueError):
            desserializar_estado(data)
