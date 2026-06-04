"""
api/schemas.py — Lote 2A
Contratos alinhados com client.ts + gameStore.ts da branch main.

Mudanças em relação ao Lote 1:
  - JogadorStatus: +andar, +inventario, -nivel
  - ItemInventario: novo modelo (inventário do jogador)
  - LojaOferta: estrutura flat (era LojaItemInfo aninhada)
  - LojaInfo: campo "ofertas" (era "itens")
  - ShopResponse: sucesso: bool (era resultado: str)
  - NewGameRequest/NewGameResponse/StatusResponse: "modo" (era "game_mode")
  - UseItemRequest / UseItemResponse: novos (endpoint /inventory/use)
  - SaveStateResponse / LoadGameRequest / LoadGameResponse: novos (save/load)
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


# ─── Entidades base ───────────────────────────────────────────────────────────

class ItemInventario(BaseModel):
    """Item no inventário do jogador (serialização plana)."""
    nome:      str
    bonus_atk: int   = 0
    bonus_hp:  int   = 0
    bonus_esq: float = 0.0


class EfeitoAtivo(BaseModel):
    """Lote 5: um efeito de status ativo no jogador (para o badge na UI)."""
    tipo:   str   # "veneno" | "fraqueza" | "esquiva_reduzida"
    turnos: int   # turnos restantes


class JogadorStatus(BaseModel):
    """
    Estado completo do jogador.
    Inclui 'andar' e 'inventario' — campos requeridos pelo client.ts.
    """
    nome:      str
    hp:        int
    hp_max:    int
    atk:       int
    esq:       float
    xp:        int
    nivel:     int                    = 1   # ← Lote D: nível real (Lote A)
    # Progresso de XP no nível atual (curva real) — barra de XP correta na UI.
    xp_nivel_atual: int               = 0   # ← Lote 6/feedback
    xp_nivel_total: int               = 1   # ← Lote 6/feedback (>=1, evita div/0)
    pontuacao: int                    = 0   # ← Lote G: pontuação (prévia do Lote H)
    score:     int                    = 0   # ← Lote H: score da run (pontuacao + andar*100)
    moedas:    int
    andar:     int                    = 0   # ← novo Lote 2A
    inventario: List[ItemInventario]  = []  # ← novo Lote 2A
    veneno_turnos: int                = 0   # ← Lote M: turnos de veneno restantes
    # ── Lote 5: efeitos de status + passivos (para os badges na tela de combate) ──
    efeitos:   List[EfeitoAtivo]      = []  # efeitos temporários ativos (veneno/fraqueza/…)
    lifesteal: float                  = 0.0  # passivo Sanguessuga (% do dano que cura)
    dom:       Optional[str]          = None # dom escolhido na criação (id) ou None
    evasao_passiva: float             = 0.0  # passivo Ágil (inimigos erram mais)


class InimigoInfo(BaseModel):
    nome:          str
    hp:            int
    hp_max:        int
    atk:           int
    dificuldade:   int
    tipo_especial: Optional[str] = None


class ItemInfo(BaseModel):
    """Item de loot / baú (não é o mesmo que ItemInventario)."""
    nome:      str
    bonus_atk: int   = 0
    bonus_hp:  int   = 0
    bonus_esq: float = 0.0


class LojaOferta(BaseModel):
    """
    Oferta individual da loja — estrutura FLAT exigida pelo ShopScreen.tsx.
    (Lote 1 usava LojaItemInfo aninhada com campo 'item'.)
    """
    nome:      str
    preco:     int
    bonus_atk: int   = 0
    bonus_hp:  int   = 0
    bonus_esq: float = 0.0


class LojaInfo(BaseModel):
    """
    Loja do mercador.
    Campo 'ofertas' (era 'itens' no Lote 1).
    """
    ofertas: List[LojaOferta]


# ─── Endpoints ────────────────────────────────────────────────────────────────

class NewGameRequest(BaseModel):
    nome: str
    modo: str = "story"              # "story" | "infinite"
    dom: Optional[str] = None        # Lote 3: dom escolhido (id) ou None


class NewGameResponse(BaseModel):
    session_id: str
    jogador:    JogadorStatus
    modo:       str = "story"


class LoreResponse(BaseModel):
    linhas: List[str]


class StatusResponse(BaseModel):
    session_id: str
    jogador:    JogadorStatus
    andar:      int
    modo:       str = "story"


class SalaResponse(BaseModel):
    tipo:      str                       # "inimigo"|"boss"|"item"|"loja"
    descricao: str
    andar:     int
    jogador:   JogadorStatus
    inimigo:   Optional[InimigoInfo] = None
    item:      Optional[ItemInfo]    = None
    loja:      Optional[LojaInfo]    = None


class CombatActionResponse(BaseModel):
    resultado:         str               # "continua"|"vitoria"|"derrota"|"fuga"|"vitoria_campanha"|"proximo"|"renasceu"
    mensagem:          str
    dano_jogador:      int  = 0
    dano_inimigo:      int  = 0
    jogador:           JogadorStatus
    inimigo:           Optional[InimigoInfo] = None
    jogador_atordoado: bool = False
    miss_jogador:      bool = False
    miss_inimigo:      bool = False
    loot:              Optional[ItemInfo]    = None


class ChestResponse(BaseModel):
    tipo:     str                        # "mimico"|"item"|"ignorado"
    mensagem: str
    jogador:  JogadorStatus
    item:     Optional[ItemInfo]    = None
    inimigo:  Optional[InimigoInfo] = None


class ShopBuyRequest(BaseModel):
    indice: int


class ShopResponse(BaseModel):
    """
    Lote 2A: sucesso agora é bool (gameStore usa res.sucesso para tocar SFX).
    """
    sucesso:  bool                       # ← era resultado: str no Lote 1
    mensagem: str
    jogador:  JogadorStatus
    loja:     Optional[LojaInfo] = None


class QuitResponse(BaseModel):
    mensagem: str
    jogador:  JogadorStatus


# ─── Inventário ───────────────────────────────────────────────────────────────

class UseItemRequest(BaseModel):
    indice: int


class UseItemResponse(BaseModel):
    sucesso:  bool
    mensagem: str
    efeito:   Dict[str, float] = {}
    jogador:  JogadorStatus


# ─── Save / Load ──────────────────────────────────────────────────────────────

class SaveStateResponse(BaseModel):
    version:    int = 1
    savedAt:    str
    playerName: str
    andar:      int
    modo:       str
    jogador:    Dict[str, Any]


class LoadGameRequest(BaseModel):
    version:    int
    savedAt:    str
    playerName: str
    andar:      int
    modo:       str
    jogador:    Dict[str, Any]


class LoadGameResponse(BaseModel):
    session_id: str
    jogador:    JogadorStatus
    modo:       str


# ─── Vitória de campanha ──────────────────────────────────────────────────────

class CampaignVictoryResponse(BaseModel):
    mensagem:      str
    jogador:       JogadorStatus
    andar_final:   int
    xp_total:      int
    moedas_totais: int