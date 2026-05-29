from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel

class ItemInventario(BaseModel):
    nome: str
    bonus_atk: int = 0
    bonus_hp: int = 0
    bonus_esq: float = 0.0

class JogadorStatus(BaseModel):
    nome:       str
    hp:         int
    hp_max:     int
    atk:        int
    esq:        float
    xp:         int
    # Campo legado mantido para compatibilidade com o frontend atual.
    nivel:      int = 1
    moedas:     int
    andar:      int
    inventario: List[ItemInventario]

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
    itens: List[LojaItemInfo]

class NewGameRequest(BaseModel):
    nome:      str
    game_mode: str = "infinite"

class NewGameResponse(BaseModel):
    session_id: str
    jogador:    JogadorStatus
    game_mode:  str = "infinite"

class LoreResponse(BaseModel):
    linhas: List[str]

class StatusResponse(BaseModel):
    session_id: str
    jogador:    JogadorStatus
    andar:      int
    game_mode:  str = "infinite"

class SalaResponse(BaseModel):
    tipo:      str
    descricao: str
    andar:     int
    jogador:   JogadorStatus
    inimigo:   Optional[InimigoInfo] = None
    item:      Optional[ItemInfo]    = None
    loja:      Optional[LojaInfo]    = None

class CombatActionResponse(BaseModel):
    resultado:           str
    mensagem:            str
    dano_jogador:        int  = 0
    dano_inimigo:        int  = 0
    jogador:             JogadorStatus
    inimigo:             Optional[InimigoInfo] = None
    jogador_atordoado:   bool = False
    miss_jogador:        bool = False
    miss_inimigo:        bool = False
    loot:                Optional[ItemInfo]    = None

class ChestResponse(BaseModel):
    tipo:     str
    mensagem: str
    jogador:  JogadorStatus
    item:     Optional[ItemInfo]    = None
    inimigo:  Optional[InimigoInfo] = None

class ShopBuyRequest(BaseModel):
    indice: int

class ShopResponse(BaseModel):
    resultado: str
    mensagem:  str
    jogador:   JogadorStatus
    loja:      Optional[LojaInfo] = None

class QuitResponse(BaseModel):
    mensagem: str
    jogador:  JogadorStatus

class CampaignVictoryResponse(BaseModel):
    mensagem:      str
    jogador:       JogadorStatus
    andar_final:   int
    xp_total:      int
    moedas_totais: int
