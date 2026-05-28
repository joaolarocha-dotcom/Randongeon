"""
api/main.py
FastAPI — 12 endpoints REST do Randongeon.

Lote 1 — correções alinhadas com gameStore.ts v3.1:
  - advance(): tipo="inimigo" (não "monstro"), tipo="item" (não "baú").
  - lore: retorna {"linhas": [...]} (não {"lore": "..."}).
  - shopBuy: aceita indice (int), não item_nome.
  - ShopResponse: campo "loja" (LojaInfo), não "itens_loja".
  - chest/open: campo "tipo" (não "resultado").
  - quit: retorna QuitResponse {mensagem, jogador}.
  - Mantidos: miss mechanic, loot drops, vitoria_campanha.

Pylance reportMissingImports → falsos positivos (severity 4).
Funcionam normalmente via terminal com o venv ativado.
"""
from __future__ import annotations

import os
import random
import sys

sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "randongeon"),
)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import (
    CampaignVictoryResponse,
    ChestResponse,
    CombatActionResponse,
    InimigoInfo,
    ItemInfo,
    LojaInfo,
    LojaItemInfo,
    JogadorStatus,
    LoreResponse,
    NewGameRequest,
    NewGameResponse,
    QuitResponse,
    SalaResponse,
    ShopBuyRequest,
    ShopResponse,
    StatusResponse,
)
from session import GameState, create_session, delete_session, get_session
from jogo.entidades.inimigo import Inimigo
from jogo.entidades.loja    import Loja
from jogo.sistemas.masmorra import CHANCE_MISS_JOGADOR, LORE, POOL_LOOT

app = FastAPI(title="Randongeon API", version="3.1-lote1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ANDAR_MAX_CAMPANHA: int = 20


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _get_session(session_id: str) -> GameState:
    try:
        return get_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")


def _jogador_status(state: GameState) -> JogadorStatus:
    j = state.masmorra.jogador
    return JogadorStatus(
        nome=j.nome,
        hp=j.hp,
        hp_max=getattr(j, "hp_max", j.hp),
        atk=j.atk,
        esq=j.esq,
        xp=j.xp,
        nivel=getattr(j, "nivel", 1),
        moedas=j.moedas,
    )


def _inimigo_info(inimigo: Inimigo) -> InimigoInfo:
    return InimigoInfo(
        nome=inimigo.nome,
        hp=inimigo.hp,
        hp_max=getattr(inimigo, "hp_max", inimigo.hp),
        atk=inimigo.atk,
        dificuldade=inimigo.dificuldade,
        tipo_especial=getattr(inimigo, "tipo_especial", None),
    )


def _item_info(item) -> ItemInfo:
    return ItemInfo(
        nome=item.nome,
        bonus_atk=getattr(item, "bonus_atk", 0),
        bonus_hp=getattr(item, "bonus_hp", 0),
        bonus_esq=getattr(item, "bonus_esq", 0.0),
    )


def _loja_info(loja) -> LojaInfo:
    """
    Serializa Loja para LojaInfo.
    Suporta loja.itens como lista de tuples (item, preco)
    ou de objetos com .item / .preco.
    """
    result = []
    for entrada in loja.itens:
        if isinstance(entrada, (list, tuple)):
            item, preco = entrada
        else:
            item, preco = entrada.item, entrada.preco
        result.append(LojaItemInfo(item=_item_info(item), preco=preco))
    return LojaInfo(itens=result)


def _rolar_loot(inimigo: Inimigo):
    """
    Boss (dificuldade 3) → 50%.
    Outros → chance_drop individual do inimigo.
    """
    chance = 0.50 if inimigo.dificuldade == 3 else inimigo.chance_drop
    return random.choice(POOL_LOOT) if random.random() < chance else None


def _processar_ataque_inimigo(
    state: GameState,
    inimigo: Inimigo,
    mensagem: str,
) -> tuple[int, bool, str]:
    """
    Resolve o turno do inimigo: escala ATK (Caçador), rola miss,
    aplica dano, atordoa (Banshee).
    Retorna (dano_inimigo, miss_inimigo, mensagem_atualizada).
    """
    jogador = state.masmorra.jogador

    if getattr(inimigo, "bonus_atk_por_turno", 0):
        inimigo.atk += inimigo.bonus_atk_por_turno

    miss_inimigo = False
    dano_inimigo = 0

    if random.random() < getattr(inimigo, "chance_miss", 0.10):
        miss_inimigo = True
        mensagem += f" {inimigo.nome} errou o ataque!"
    else:
        dano_inimigo = jogador.receber_dano(inimigo.atk)
        mensagem += f" {inimigo.nome} causou {dano_inimigo} de dano."

        if getattr(inimigo, "cura_percentual", 0):
            cura = max(1, int(dano_inimigo * inimigo.cura_percentual))
            inimigo.curar(cura)

        if getattr(inimigo, "chance_atordoar", 0):
            if random.random() < inimigo.chance_atordoar:
                state.jogador_atordoado = True
                mensagem += f" {jogador.nome} foi atordoado!"

    return dano_inimigo, miss_inimigo, mensagem


def _checar_vitoria_campanha(
    session_id: str,
    state: GameState,
    inimigo: Inimigo,
    mensagem: str,
    dano_jogador: int,
    dano_inimigo: int,
    miss_jogador: bool,
    miss_inimigo: bool,
    loot_drop,
) -> CombatActionResponse | None:
    if (
        state.game_mode == "campaign"
        and state.masmorra.andar >= ANDAR_MAX_CAMPANHA
        and inimigo.dificuldade == 3
    ):
        resp = CombatActionResponse(
            resultado="vitoria_campanha",
            mensagem=(
                f"🏆 {state.masmorra.jogador.nome} conquistou o "
                "Coração da Masmorra! A masmorra foi vencida!"
            ),
            dano_jogador=dano_jogador,
            dano_inimigo=dano_inimigo,
            jogador=_jogador_status(state),
            miss_jogador=miss_jogador,
            miss_inimigo=miss_inimigo,
            loot=_item_info(loot_drop) if loot_drop else None,
        )
        delete_session(session_id)
        return resp
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Nova partida
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/game/new", response_model=NewGameResponse)
def new_game(req: NewGameRequest):
    session_id, state = create_session(req.nome.strip(), req.game_mode)
    return NewGameResponse(
        session_id=session_id,
        jogador=_jogador_status(state),
        game_mode=state.game_mode,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Status
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/game/{session_id}/status", response_model=StatusResponse)
def get_status(session_id: str):
    state = _get_session(session_id)
    return StatusResponse(
        session_id=session_id,
        jogador=_jogador_status(state),
        andar=state.masmorra.andar,
        game_mode=state.game_mode,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Lore
# FIX: retorna {"linhas": [...]} — gameStore: set({ loreLinhas: res.linhas })
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/game/{session_id}/lore", response_model=LoreResponse)
def get_lore(session_id: str):
    _get_session(session_id)
    return LoreResponse(linhas=LORE)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Avançar de sala
# FIX: tipo="inimigo" (não "monstro"), tipo="item" (não "baú")
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/game/{session_id}/advance", response_model=SalaResponse)
def advance(session_id: str):
    state    = _get_session(session_id)
    masmorra = state.masmorra

    state.inimigo_ativo     = None
    state.loja_ativa        = None
    state.sala_pendente     = None
    state.jogador_atordoado = False

    # Campanha: andar máximo → re-spawn boss final sem incrementar
    if state.game_mode == "campaign" and masmorra.andar >= ANDAR_MAX_CAMPANHA:
        boss = masmorra.gerar_boss()
        state.inimigo_ativo = boss
        state.sala_pendente = {"hp_max": boss.hp_max}
        return SalaResponse(
            tipo="boss",
            descricao="⚠️ O Coração da Masmorra bloqueia a saída! Não há escapatória!",
            andar=masmorra.andar,
            inimigo=_inimigo_info(boss),
            jogador=_jogador_status(state),
        )

    # Avanço normal
    masmorra.andar += 1

    if masmorra.e_andar_de_boss():
        boss = masmorra.gerar_boss()
        state.inimigo_ativo = boss
        state.sala_pendente = {"hp_max": boss.hp_max}
        return SalaResponse(
            tipo="boss",
            descricao=f"Um guardião emerge das sombras do andar {masmorra.andar}!",
            andar=masmorra.andar,
            inimigo=_inimigo_info(boss),
            jogador=_jogador_status(state),
        )

    tipo, conteudo, descricao = masmorra.gerador.gerar_sala(masmorra.andar)

    if tipo == "inimigo":
        inimigo = conteudo
        state.inimigo_ativo = inimigo
        state.sala_pendente = {"hp_max": inimigo.hp_max}
        return SalaResponse(
            tipo="inimigo",           # FIX: era "monstro"
            descricao=descricao,
            andar=masmorra.andar,
            inimigo=_inimigo_info(inimigo),
            jogador=_jogador_status(state),
        )

    if tipo == "item":
        item = conteudo
        state.sala_pendente = {"item": item}
        return SalaResponse(
            tipo="item",              # FIX: era "baú"
            descricao=descricao,
            andar=masmorra.andar,
            item=_item_info(item) if item else None,
            jogador=_jogador_status(state),
        )

    if tipo == "loja":
        loja = Loja()
        state.loja_ativa = loja
        return SalaResponse(
            tipo="loja",
            descricao=descricao,
            andar=masmorra.andar,
            loja=_loja_info(loja),
            jogador=_jogador_status(state),
        )

    # fallback
    return SalaResponse(
        tipo=tipo,
        descricao=descricao,
        andar=masmorra.andar,
        jogador=_jogador_status(state),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Atacar
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/game/{session_id}/combat/attack", response_model=CombatActionResponse)
def combat_attack(session_id: str):
    state   = _get_session(session_id)
    jogador = state.masmorra.jogador
    inimigo = state.inimigo_ativo

    if inimigo is None:
        raise HTTPException(status_code=400, detail="Sem inimigo ativo")

    miss_jogador = False
    miss_inimigo = False
    dano_jogador = 0
    dano_inimigo = 0
    loot_drop    = None

    # Turno do jogador
    if state.jogador_atordoado:
        state.jogador_atordoado = False
        mensagem = f"{jogador.nome} está atordoado e perde o turno!"
    elif random.random() < CHANCE_MISS_JOGADOR:
        miss_jogador = True
        mensagem = "Você errou o ataque!"
    else:
        dano_jogador = inimigo.receber_dano(jogador.atk)
        mensagem = f"Você causou {dano_jogador} de dano."
        if getattr(inimigo, "cura_percentual", 0):
            inimigo.curar(max(1, int(dano_jogador * inimigo.cura_percentual)))

    # Inimigo morto?
    if inimigo.hp <= 0:
        jogador.ganhar_xp(inimigo.xp)
        jogador.ganhar_moedas(inimigo.moedas)
        loot_drop = _rolar_loot(inimigo)
        if loot_drop:
            state.masmorra.aplicar_item(loot_drop)
        mensagem += f" {inimigo.nome} foi derrotado!"
        state.inimigo_ativo = None

        campanha = _checar_vitoria_campanha(
            session_id, state, inimigo, mensagem,
            dano_jogador, 0, miss_jogador, False, loot_drop,
        )
        if campanha:
            return campanha

        return CombatActionResponse(
            resultado="vitoria",
            mensagem=mensagem,
            dano_jogador=dano_jogador,
            dano_inimigo=0,
            jogador=_jogador_status(state),
            inimigo=_inimigo_info(inimigo),
            miss_jogador=miss_jogador,
            miss_inimigo=False,
            loot=_item_info(loot_drop) if loot_drop else None,
        )

    # Turno do inimigo
    dano_inimigo, miss_inimigo, mensagem = _processar_ataque_inimigo(
        state, inimigo, mensagem
    )

    # Jogador morto?
    if jogador.hp <= 0:
        state.inimigo_ativo = None
        delete_session(session_id)
        return CombatActionResponse(
            resultado="derrota",
            mensagem=mensagem + " Você foi derrotado...",
            dano_jogador=dano_jogador,
            dano_inimigo=dano_inimigo,
            jogador=_jogador_status(state),
            miss_jogador=miss_jogador,
            miss_inimigo=miss_inimigo,
        )

    return CombatActionResponse(
        resultado="continua",
        mensagem=mensagem,
        dano_jogador=dano_jogador,
        dano_inimigo=dano_inimigo,
        jogador=_jogador_status(state),
        inimigo=_inimigo_info(inimigo),
        jogador_atordoado=state.jogador_atordoado,
        miss_jogador=miss_jogador,
        miss_inimigo=miss_inimigo,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 6. Esquivar
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/game/{session_id}/combat/dodge", response_model=CombatActionResponse)
def combat_dodge(session_id: str):
    state   = _get_session(session_id)
    jogador = state.masmorra.jogador
    inimigo = state.inimigo_ativo

    if inimigo is None:
        raise HTTPException(status_code=400, detail="Sem inimigo ativo")

    miss_jogador = False
    dano_jogador = 0
    loot_drop    = None

    era_atordoado = state.jogador_atordoado
    if era_atordoado:
        state.jogador_atordoado = False
        mensagem = f"{jogador.nome} está atordoado e perde o turno!"
        esquivou = False
    else:
        esquivou = random.random() < jogador.esq
        mensagem = ""

    if esquivou:
        mensagem = f"{jogador.nome} esquivou com sucesso!"
        if random.random() < CHANCE_MISS_JOGADOR:
            miss_jogador = True
            mensagem += " Mas errou o contra-ataque!"
        else:
            dano_jogador = inimigo.receber_dano(jogador.atk)
            mensagem += f" Contra-atacou por {dano_jogador} de dano."
            if getattr(inimigo, "cura_percentual", 0):
                inimigo.curar(max(1, int(dano_jogador * inimigo.cura_percentual)))

        if inimigo.hp <= 0:
            jogador.ganhar_xp(inimigo.xp)
            jogador.ganhar_moedas(inimigo.moedas)
            loot_drop = _rolar_loot(inimigo)
            if loot_drop:
                state.masmorra.aplicar_item(loot_drop)
            mensagem += f" {inimigo.nome} foi derrotado!"
            state.inimigo_ativo = None

            campanha = _checar_vitoria_campanha(
                session_id, state, inimigo, mensagem,
                dano_jogador, 0, miss_jogador, False, loot_drop,
            )
            if campanha:
                return campanha

            return CombatActionResponse(
                resultado="vitoria",
                mensagem=mensagem,
                dano_jogador=dano_jogador,
                dano_inimigo=0,
                jogador=_jogador_status(state),
                inimigo=_inimigo_info(inimigo),
                miss_jogador=miss_jogador,
                miss_inimigo=False,
                loot=_item_info(loot_drop) if loot_drop else None,
            )

        # Esquivou — inimigo não ataca neste turno
        return CombatActionResponse(
            resultado="continua",
            mensagem=mensagem,
            dano_jogador=dano_jogador,
            dano_inimigo=0,
            jogador=_jogador_status(state),
            inimigo=_inimigo_info(inimigo),
            miss_jogador=miss_jogador,
            miss_inimigo=False,
        )

    # Esquiva falhou → inimigo ataca
    if not mensagem:
        mensagem = "A esquiva falhou!"

    dano_inimigo, miss_inimigo, mensagem = _processar_ataque_inimigo(
        state, inimigo, mensagem
    )

    if jogador.hp <= 0:
        delete_session(session_id)
        return CombatActionResponse(
            resultado="derrota",
            mensagem=mensagem + " Você foi derrotado...",
            dano_jogador=0,
            dano_inimigo=dano_inimigo,
            jogador=_jogador_status(state),
            miss_jogador=False,
            miss_inimigo=miss_inimigo,
        )

    return CombatActionResponse(
        resultado="continua",
        mensagem=mensagem,
        dano_jogador=0,
        dano_inimigo=dano_inimigo,
        jogador=_jogador_status(state),
        inimigo=_inimigo_info(inimigo),
        jogador_atordoado=state.jogador_atordoado,
        miss_jogador=False,
        miss_inimigo=miss_inimigo,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 7. Fugir
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/game/{session_id}/combat/flee", response_model=CombatActionResponse)
def combat_flee(session_id: str):
    state   = _get_session(session_id)
    jogador = state.masmorra.jogador
    inimigo = state.inimigo_ativo

    if inimigo is None:
        raise HTTPException(status_code=400, detail="Sem inimigo ativo")

    if state.masmorra.tentar_fuga(inimigo):
        state.inimigo_ativo = None
        return CombatActionResponse(
            resultado="fuga",
            mensagem=f"{jogador.nome} fugiu com sucesso!",
            dano_jogador=0,
            dano_inimigo=0,
            jogador=_jogador_status(state),
        )

    # Fuga falhou → inimigo ataca
    mensagem = "A fuga falhou!"
    dano_inimigo, miss_inimigo, mensagem = _processar_ataque_inimigo(
        state, inimigo, mensagem
    )

    if jogador.hp <= 0:
        delete_session(session_id)
        return CombatActionResponse(
            resultado="derrota",
            mensagem=mensagem + " Você foi derrotado...",
            dano_jogador=0,
            dano_inimigo=dano_inimigo,
            jogador=_jogador_status(state),
            miss_inimigo=miss_inimigo,
        )

    return CombatActionResponse(
        resultado="continua",
        mensagem=mensagem,
        dano_jogador=0,
        dano_inimigo=dano_inimigo,
        jogador=_jogador_status(state),
        inimigo=_inimigo_info(inimigo),
        jogador_atordoado=state.jogador_atordoado,
        miss_inimigo=miss_inimigo,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 8 & 9. Baú
# FIX: campo "tipo" (não "resultado") — gameStore: res.tipo === "mimico"
# ═══════════════════════════════════════════════════════════════════════════════

_CHANCE_MIMICO = 0.20

@app.post("/game/{session_id}/chest/open", response_model=ChestResponse)
def chest_open(session_id: str):
    state = _get_session(session_id)

    if random.random() < _CHANCE_MIMICO:
        mimico = state.masmorra.gerar_mimico()
        state.inimigo_ativo = mimico
        return ChestResponse(
            tipo="mimico",           # FIX: campo "tipo", não "resultado"
            mensagem="Era uma armadilha! Um Mímico ataca!",
            jogador=_jogador_status(state),
            inimigo=_inimigo_info(mimico),
        )

    # Item do baú: preferência ao item da sala; senão, sorteia do pool
    item_sala = (state.sala_pendente or {}).get("item")
    item = item_sala if item_sala else random.choice(POOL_LOOT)
    state.masmorra.aplicar_item(item)

    return ChestResponse(
        tipo="item",
        mensagem=f"Você encontrou {item.nome}!",
        jogador=_jogador_status(state),
        item=_item_info(item),
    )


@app.post("/game/{session_id}/chest/ignore", response_model=ChestResponse)
def chest_ignore(session_id: str):
    state = _get_session(session_id)
    return ChestResponse(
        tipo="ignorado",
        mensagem="Você ignorou o baú e seguiu em frente.",
        jogador=_jogador_status(state),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 10 & 11. Loja
# FIX: shopBuy por índice; ShopResponse.loja = LojaInfo
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/game/{session_id}/shop/buy", response_model=ShopResponse)
def shop_buy(session_id: str, req: ShopBuyRequest):
    state = _get_session(session_id)
    loja  = state.loja_ativa

    if loja is None:
        raise HTTPException(status_code=400, detail="Nenhuma loja ativa")

    jogador = state.masmorra.jogador

    try:
        entrada = loja.itens[req.indice]
    except IndexError:
        return ShopResponse(
            resultado="indice_invalido",
            mensagem=f"Índice {req.indice} não existe na loja.",
            jogador=_jogador_status(state),
            loja=_loja_info(loja),
        )

    if isinstance(entrada, (list, tuple)):
        item, preco = entrada
    else:
        item, preco = entrada.item, entrada.preco

    if jogador.moedas < preco:
        return ShopResponse(
            resultado="sem_moedas",
            mensagem=(
                f"Moedas insuficientes. "
                f"Precisa de {preco}, você tem {jogador.moedas}."
            ),
            jogador=_jogador_status(state),
            loja=_loja_info(loja),
        )

    jogador.moedas -= preco
    state.masmorra.aplicar_item(item)

    # Remove o item comprado da loja
    loja.itens.pop(req.indice)
    loja_atualizada = _loja_info(loja) if loja.itens else None

    return ShopResponse(
        resultado="compra_efetuada",
        mensagem=f"Você comprou {item.nome} por {preco} moedas!",
        jogador=_jogador_status(state),
        loja=loja_atualizada,          # None quando loja fica vazia → gameStore vai para menu
    )


@app.post("/game/{session_id}/shop/leave", response_model=ShopResponse)
def shop_leave(session_id: str):
    state = _get_session(session_id)
    state.loja_ativa = None
    return ShopResponse(
        resultado="saiu",
        mensagem="Você saiu da loja.",
        jogador=_jogador_status(state),
        loja=None,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 12. Desistir
# FIX: retorna QuitResponse {mensagem, jogador} — gameStore: res.mensagem + res.jogador
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/game/{session_id}/quit", response_model=QuitResponse)
def quit_game(session_id: str):
    state = _get_session(session_id)
    jogador_final = _jogador_status(state)
    delete_session(session_id)
    return QuitResponse(
        mensagem=(
            f"{jogador_final.nome} desistiu no andar "
            f"{state.masmorra.andar}. "
            f"XP obtido: {jogador_final.xp}."
        ),
        jogador=jogador_final,
    )