import uuid
from dataclasses import dataclass, field
from typing import Optional

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "randongeon"))

from jogo.entidades.jogador import Jogador
from jogo.entidades.inimigo import Inimigo
from jogo.entidades.loja import Loja
from jogo.sistemas.masmorra import Masmorra
from jogo.sistemas.gerador import GeradorSala


@dataclass
class GameState:
    masmorra: Masmorra
    inimigo_ativo: Optional[Inimigo] = None
    loja_ativa: Optional[Loja] = None
    sala_pendente: Optional[dict] = field(default_factory=lambda: None)


_sessions: dict[str, GameState] = {}


def create_session(nome: str) -> tuple[str, GameState]:
    session_id = str(uuid.uuid4())
    jogador = Jogador(nome)
    gerador = GeradorSala()
    masmorra = Masmorra(jogador, gerador)
    state = GameState(masmorra=masmorra)
    _sessions[session_id] = state
    return session_id, state


def get_session(session_id: str) -> Optional[GameState]:
    return _sessions.get(session_id)


def delete_session(session_id: str) -> None:
    _sessions.pop(session_id, None)
