# randongeon/jogo/sistemas/persistencia.py

"""
Serialização e desserialização do estado de jogo.

O formato é um dict JSON-serializável com versão para permitir migrações
futuras. Captura tudo o necessário para retomar uma run: stats do jogador,
inventário, andar atual e modo.
"""

from datetime import datetime, timezone

from jogo.entidades.item import Item
from jogo.entidades.jogador import Jogador
from jogo.sistemas.gerador import GeradorSala
from jogo.sistemas.masmorra import Masmorra


SAVE_VERSION = 1


def serializar_jogador(jogador: Jogador) -> dict:
    return {
        "nome": jogador.nome,
        "hp": jogador.hp,
        "hp_max": jogador.hp_max,
        "atk": jogador.atk,
        "xp": jogador.xp,
        "esq": jogador.esq,
        "esq_max": jogador.esq_max,
        "moedas": jogador.moedas,
        "inventario": [
            {
                "nome": it.nome,
                "bonus_atk": it.bonus_atk,
                "bonus_hp": it.bonus_hp,
                "bonus_esq": it.bonus_esq,
            }
            for it in jogador.inventario
        ],
    }


def desserializar_jogador(data: dict) -> Jogador:
    j = Jogador(
        nome=data["nome"],
        hp=int(data["hp_max"]),
        atk=int(data["atk"]),
        xp=int(data.get("xp", 0)),
        esq=float(data.get("esq", 0.3)),
        moedas=int(data.get("moedas", 0)),
    )
    j.hp = int(data["hp"])
    j.esq_max = float(data.get("esq_max", 1))
    j.inventario = []
    for raw in data.get("inventario", []) or []:
        item = Item(
            nome=raw["nome"],
            bonus_atk=int(raw.get("bonus_atk", 0)),
            bonus_hp=int(raw.get("bonus_hp", 0)),
            bonus_esq=float(raw.get("bonus_esq", 0)),
        )
        j.inventario.append(item)
    return j


def serializar_estado(jogador: Jogador, masmorra: Masmorra, modo: str) -> dict:
    return {
        "version": SAVE_VERSION,
        "savedAt": datetime.now(timezone.utc).isoformat(),
        "playerName": jogador.nome,
        "andar": masmorra.andar,
        "modo": modo,
        "jogador": serializar_jogador(jogador),
    }


def desserializar_estado(data: dict) -> tuple[Jogador, Masmorra, str]:
    if "version" in data and int(data["version"]) > SAVE_VERSION:
        raise ValueError(
            f"Versão do save ({data['version']}) é mais nova do que esta versão do jogo (max {SAVE_VERSION})."
        )

    modo = data.get("modo", "story")
    if modo not in ("story", "infinite"):
        raise ValueError("Campo 'modo' inválido no save.")

    jogador = desserializar_jogador(data["jogador"])
    andar_max = 20 if modo == "story" else None
    masmorra = Masmorra(jogador, GeradorSala(), andar_max=andar_max)
    masmorra.andar = int(data.get("andar", 0))
    return jogador, masmorra, modo
