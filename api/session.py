"""
api/session.py — Lote 2A
Gerenciamento de sessões em memória.

Mudanças em relação ao Lote 1:
  - "game_mode" renomeado para "modo" em todo o arquivo.
  - Modos: "story" (boss a cada 5 andares, andar_max=20)
           "infinite" (boss a cada 3 andares, sem limite)
  - Adicionado load_session() para restaurar runs salvas.
  - Masmorra recebe parâmetro modo= além de andar_max=.
"""
from __future__ import annotations

import os
import sys
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "randongeon"),
)

from jogo.entidades.inimigo import Inimigo
from jogo.entidades.item    import Item
from jogo.entidades.jogador import Jogador
from jogo.sistemas.masmorra import Masmorra

_ANDAR_MAX_STORY: int = 20
_MODOS_VALIDOS         = {"story", "infinite"}


@dataclass
class GameState:
    masmorra:          Masmorra
    modo:              str               = "story"     # "story" | "infinite"
    inimigo_ativo:     Optional[Inimigo] = None
    loja_ativa:        Optional[Any]     = None
    sala_pendente:     Optional[dict]    = field(default=None)
    jogador_atordoado: bool              = False


_sessions: dict[str, GameState] = {}


def create_session(
    nome: str,
    modo: str = "story",
) -> tuple[str, GameState]:
    """Cria uma sessão nova a partir do nome do herói e do modo."""
    if modo not in _MODOS_VALIDOS:
        modo = "story"

    session_id = str(uuid.uuid4())
    jogador    = Jogador(nome)
    andar_max  = _ANDAR_MAX_STORY if modo == "story" else None
    masmorra   = Masmorra(jogador, andar_max=andar_max, modo=modo)
    state      = GameState(masmorra=masmorra, modo=modo)
    _sessions[session_id] = state
    return session_id, state


def load_session(
    jogador: Jogador,
    modo: str = "story",
    andar: int = 0,
) -> tuple[str, GameState]:
    """
    Reconstrói uma sessão a partir de um Jogador já restaurado (save/load).
    O andar atual é restaurado manualmente após criação da Masmorra.
    """
    if modo not in _MODOS_VALIDOS:
        modo = "story"

    session_id = str(uuid.uuid4())
    andar_max  = _ANDAR_MAX_STORY if modo == "story" else None
    masmorra   = Masmorra(jogador, andar_max=andar_max, modo=modo)
    masmorra.andar = max(0, andar)
    state      = GameState(masmorra=masmorra, modo=modo)
    _sessions[session_id] = state
    return session_id, state


def get_session(session_id: str) -> GameState:
    state = _sessions.get(session_id)
    if state is None:
        raise KeyError(f"Sessão '{session_id}' não encontrada")
    return state


def delete_session(session_id: str) -> None:
    _sessions.pop(session_id, None)