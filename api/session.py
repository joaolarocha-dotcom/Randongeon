"""
api/session.py
Gerenciamento de sessões em memória da API Randongeon.

Lote 1:
  - GameState: adicionado game_mode, loja_ativa.
  - create_session(nome, game_mode): passa andar_max=20 para Masmorra
    quando mode=="campaign".
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
from jogo.entidades.jogador import Jogador
from jogo.sistemas.masmorra import Masmorra

_ANDAR_MAX_CAMPANHA: int = 20


@dataclass
class GameState:
    masmorra:          Masmorra
    game_mode:         str               = "infinite"  # "campaign" | "infinite"
    inimigo_ativo:     Optional[Inimigo] = None
    loja_ativa:        Optional[Any]     = None        # instância de Loja
    sala_pendente:     Optional[dict]    = field(default=None)
    jogador_atordoado: bool              = False


_sessions: dict[str, GameState] = {}


def create_session(
    nome: str,
    game_mode: str = "infinite",
) -> tuple[str, GameState]:
    session_id = str(uuid.uuid4())
    jogador    = Jogador(nome)
    andar_max  = _ANDAR_MAX_CAMPANHA if game_mode == "campaign" else None
    masmorra   = Masmorra(jogador, andar_max=andar_max)
    state      = GameState(masmorra=masmorra, game_mode=game_mode)
    _sessions[session_id] = state
    return session_id, state


def get_session(session_id: str) -> GameState:
    state = _sessions.get(session_id)
    if state is None:
        raise KeyError(f"Sessão '{session_id}' não encontrada")
    return state


def delete_session(session_id: str) -> None:
    _sessions.pop(session_id, None)