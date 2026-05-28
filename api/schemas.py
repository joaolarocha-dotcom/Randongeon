"""
api/schemas.py
Modelos Pydantic para request/response da API Randongeon.

Lote 1 — correções alinhadas com gameStore.ts v3.1:
  - SalaResponse.tipo usa "inimigo" (não "monstro") e "item" (não "baú").
  - LojaInfo / LojaItemInfo: estrutura aninhada que gameStore espera.
  - ChestResponse.tipo: usa "mimico"|"item"|"ignorado" (não "resultado").
  - ShopBuyRequest: por índice (não por nome).
  - ShopResponse.loja: LojaInfo (não itens_loja list).
  - QuitResponse: retorna mensagem + jogador.
  - game_mode em NewGameRequest/NewGameResponse.
  - CampaignVictoryResponse novo.
"""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel


# ─── Entidades base ───────────────────────────────────────────────────────────

class JogadorStatus(BaseModel):
    nome:   str
    hp:     int
    hp_max: int
    atk:    int
    esq:    float
    xp:     int
    nivel:  int
    moedas: int


class InimigoInfo(BaseModel):
    nome:          str
    hp:            int
    hp_max:        int
    atk:           int
    dificuldade:   int
    tipo_especial: Optional[str] = None


class ItemInfo(BaseModel):
    nome:      str
    bonus_atk: int   = 0
    bonus_hp:  int   = 0
    bonus_esq: float = 0.0


class LojaItemInfo(BaseModel):
    item:  ItemInfo
    preco: int


class LojaInfo(BaseModel):
    """Estrutura da loja esperada pelo gameStore (res.loja.itens[i])."""
    itens: List[LojaItemInfo]


# ─── Endpoints ────────────────────────────────────────────────────────────────

class NewGameRequest(BaseModel):
    nome:      str
    game_mode: str = "infinite"          # "campaign" | "infinite"


class NewGameResponse(BaseModel):
    session_id: str
    jogador:    JogadorStatus
    game_mode:  str = "infinite"


class LoreResponse(BaseModel):
    linhas: List[str]                    # gameStore: res.linhas


class StatusResponse(BaseModel):
    session_id: str
    jogador:    JogadorStatus
    andar:      int
    game_mode:  str = "infinite"


class SalaResponse(BaseModel):
    # FIX: "inimigo" (não "monstro"), "item" (não "baú")
    tipo:      str                       # "inimigo"|"boss"|"item"|"loja"
    descricao: str
    andar:     int
    jogador:   JogadorStatus
    inimigo:   Optional[InimigoInfo] = None   # presente para tipo="inimigo"|"boss"
    item:      Optional[ItemInfo]    = None   # presente para tipo="item"
    loja:      Optional[LojaInfo]    = None   # presente para tipo="loja"


class CombatActionResponse(BaseModel):
    # resultado: "continua"|"vitoria"|"derrota"|"fuga"|"vitoria_campanha"
    resultado:         str
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
    # FIX: campo "tipo" (não "resultado") — gameStore usa res.tipo === "mimico"
    tipo:     str                        # "mimico"|"item"|"ignorado"
    mensagem: str
    jogador:  JogadorStatus
    item:     Optional[ItemInfo]    = None
    inimigo:  Optional[InimigoInfo] = None


class ShopBuyRequest(BaseModel):
    # FIX: por índice (não nome) — gameStore: api.shopBuy(sessionId, indice)
    indice: int


class ShopResponse(BaseModel):
    resultado: str                       # "compra_efetuada"|"sem_moedas"|"indice_invalido"|"saiu"
    mensagem:  str
    jogador:   JogadorStatus
    loja:      Optional[LojaInfo] = None  # FIX: LojaInfo (não itens_loja list)


class QuitResponse(BaseModel):
    # FIX: gameStore espera res.mensagem + res.jogador
    mensagem: str
    jogador:  JogadorStatus


class CampaignVictoryResponse(BaseModel):
    """Retornado dentro de CombatActionResponse com resultado='vitoria_campanha'."""
    mensagem:      str
    jogador:       JogadorStatus
    andar_final:   int
    xp_total:      int
    moedas_totais: int