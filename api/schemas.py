from pydantic import BaseModel
from typing import Optional, Literal


class NewGameRequest(BaseModel):
    nome: str
    modo: Literal["story", "infinite"] = "story"


class NewGameResponse(BaseModel):
    session_id: str
    jogador: "JogadorStatus"
    modo: Literal["story", "infinite"] = "story"


class ItemInventario(BaseModel):
    nome: str
    bonus_atk: int
    bonus_hp: int
    bonus_esq: float


class JogadorStatus(BaseModel):
    nome: str
    hp: int
    hp_max: int
    atk: int
    esq: float
    xp: int
    moedas: int
    andar: int
    inventario: list[ItemInventario] = []


class SalaResponse(BaseModel):
    tipo: str  # "inimigo", "item", "loja", "boss", "mimico"
    descricao: str
    andar: int
    inimigo: Optional["InimigoInfo"] = None
    item: Optional["ItemInfo"] = None
    loja: Optional["LojaInfo"] = None
    jogador: JogadorStatus


class InimigoInfo(BaseModel):
    nome: str
    hp: int
    hp_max: int
    atk: int
    dificuldade: int


class ItemInfo(BaseModel):
    nome: str
    bonus_atk: int
    bonus_hp: int
    bonus_esq: float


class LojaOferta(BaseModel):
    nome: str
    preco: int
    bonus_atk: int
    bonus_hp: int
    bonus_esq: float


class LojaInfo(BaseModel):
    ofertas: list[LojaOferta]


class CombatActionResponse(BaseModel):
    resultado: str  # "continua", "vitoria", "derrota", "fuga"
    mensagem: str
    dano_jogador: int
    dano_inimigo: int
    jogador: JogadorStatus
    inimigo: Optional[InimigoInfo] = None


class ChestResponse(BaseModel):
    tipo: str  # "item", "mimico"
    mensagem: str
    item: Optional[ItemInfo] = None
    inimigo: Optional[InimigoInfo] = None
    jogador: JogadorStatus


class ShopBuyRequest(BaseModel):
    indice: int


class ShopBuyResponse(BaseModel):
    sucesso: bool
    mensagem: str
    jogador: JogadorStatus
    loja: Optional[LojaInfo] = None


class LoreResponse(BaseModel):
    linhas: list[str]


class GameOverResponse(BaseModel):
    mensagem: str
    jogador: JogadorStatus


class UseItemRequest(BaseModel):
    indice: int


class UseItemResponse(BaseModel):
    sucesso: bool
    mensagem: str
    efeito: dict = {}
    jogador: JogadorStatus


class SaveStateResponse(BaseModel):
    version: int
    savedAt: str
    playerName: str
    andar: int
    modo: Literal["story", "infinite"]
    jogador: dict


class LoadStateRequest(BaseModel):
    version: int
    savedAt: Optional[str] = None
    playerName: str
    andar: int
    modo: Literal["story", "infinite"] = "story"
    jogador: dict


class LoadStateResponse(BaseModel):
    session_id: str
    jogador: JogadorStatus
    modo: Literal["story", "infinite"]
