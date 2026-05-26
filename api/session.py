import uuid
from dataclasses import dataclass, field
from typing import Optional

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "randongeon"))

from jogo.entidades.jogador import Jogador
from jogo.entidades.inimigo import Inimigo
from jogo.entidades.item import Item
from jogo.entidades.loja import Loja
from jogo.sistemas.masmorra import Masmorra
from jogo.sistemas.gerador import GeradorSala


ITENS_INICIAIS = [
    ("Erva Medicinal", {"bonus_hp": 3}),
    ("Poção de Força", {"bonus_atk": 1}),
]


def _criar_inventario_inicial() -> list[Item]:
    return [Item(nome, **kwargs) for nome, kwargs in ITENS_INICIAIS]


@dataclass
class GameState:
    masmorra: Masmorra
    modo: str = "story"
    inimigo_ativo: Optional[Inimigo] = None
    loja_ativa: Optional[Loja] = None
    sala_pendente: Optional[dict] = field(default_factory=lambda: None)
    pending_shop_after_boss: bool = False


_sessions: dict[str, GameState] = {}


def create_session(nome: str, modo: str = "story") -> tuple[str, GameState]:
    session_id = str(uuid.uuid4())
    jogador = Jogador(nome)
    for item in _criar_inventario_inicial():
        jogador.adicionar_item(item)
    gerador = GeradorSala()
    masmorra = Masmorra(jogador, gerador, modo=modo)
    state = GameState(masmorra=masmorra, modo=modo)
    _sessions[session_id] = state
    return session_id, state


def register_session(state: GameState) -> str:
    """Registra um GameState reconstruído (load) e retorna o novo session_id."""
    session_id = str(uuid.uuid4())
    _sessions[session_id] = state
    return session_id


def get_session(session_id: str) -> Optional[GameState]:
    return _sessions.get(session_id)


def delete_session(session_id: str) -> None:
    _sessions.pop(session_id, None)
