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


def _descobrir_caminho_randongeon() -> str:
    """
    Localiza a pasta `randongeon/` (mesma lógica de api/main.py).
    Aceita override via env var RANDONGEON_PATH.
    """
    env_path = os.environ.get("RANDONGEON_PATH")
    if env_path and os.path.isdir(env_path):
        return env_path

    here = os.path.dirname(os.path.abspath(__file__))
    candidatos = [
        os.path.join(here, "..", "randongeon"),
        os.path.join(here, "randongeon"),
    ]
    cur = here
    for _ in range(4):
        candidatos.append(os.path.join(cur, "randongeon"))
        cur = os.path.dirname(cur)

    for cand in candidatos:
        cand_abs = os.path.abspath(cand)
        if os.path.isdir(os.path.join(cand_abs, "jogo", "entidades")):
            return cand_abs

    return os.path.abspath(os.path.join(here, "..", "randongeon"))


sys.path.insert(0, _descobrir_caminho_randongeon())

from jogo.entidades.inimigo import Inimigo
from jogo.entidades.item    import Item
from jogo.entidades.jogador import Jogador
from jogo.entidades.dom     import aplicar_dom
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
    # Lote E: fila de inimigos restantes de um Bando de Goblins (combate
    # sequencial). Vazia em encontros normais.
    fila_inimigos:     list              = field(default_factory=list)


_sessions: dict[str, GameState] = {}


def _itens_iniciais() -> list[Item]:
    """Itens básicos que todo herói recebe ao começar uma run (Lote F)."""
    return [
        Item("Poção de Cura Pequena", bonus_hp=4),
        Item("Punhal Gasto",          bonus_atk=1),
    ]


def create_session(
    nome: str,
    modo: str = "story",
    dom: Optional[str] = None,
) -> tuple[str, GameState]:
    """Cria uma sessão nova a partir do nome do herói, do modo e do dom (Lote 3)."""
    if modo not in _MODOS_VALIDOS:
        modo = "story"

    session_id = str(uuid.uuid4())
    jogador    = Jogador(nome)
    aplicar_dom(jogador, dom)             # Lote 3: dom de slot único (no-op se None)
    for item in _itens_iniciais():        # Lote F: inventário inicial
        jogador.adicionar_item(item)
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


def restore_session(masmorra, game_mode: str) -> tuple[str, GameState]:
    session_id = str(uuid.uuid4())
    state = GameState(masmorra=masmorra, game_mode=game_mode)
    _sessions[session_id] = state
    return session_id, state