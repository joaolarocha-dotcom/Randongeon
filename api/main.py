"""
api/main.py — Lote 2A
FastAPI — endpoints REST do Randongeon.

Mudanças em relação ao Lote 1:
  - _jogador_status(): inclui andar e inventario (requeridos pelo client.ts).
  - _loja_info(): estrutura flat com campo "ofertas" usando loja.ofertas
    (era "itens" com estrutura aninhada; corrige bug de AttributeError).
  - shop_buy(): usa loja.comprar() e retorna sucesso: bool (era resultado: str).
  - new_game() / get_status(): "modo" em vez de "game_mode".
  - _checar_vitoria_campanha(): verifica modo=="story" (era "campaign").
  - advance(): verifica modo=="story" para re-spawn do boss final.
  - Novos endpoints:
      POST /game/{id}/inventory/use  → usar item do inventário em combate
      GET  /game/{id}/save           → serializar estado para o frontend
      POST /game/load                → reconstituir sessão de um save
"""
from __future__ import annotations

import os
import random
import sys
from datetime import datetime, timezone

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
    ItemInventario,
    LojaInfo,
    LojaOferta,
    JogadorStatus,
    LoreResponse,
    LoadGameRequest,
    LoadGameResponse,
    NewGameRequest,
    NewGameResponse,
    QuitResponse,
    SalaResponse,
    SaveStateResponse,
    ShopBuyRequest,
    ShopResponse,
    StatusResponse,
    UseItemRequest,
    UseItemResponse,
)
from session import GameState, create_session, delete_session, get_session, load_session
from jogo.entidades.inimigo import Inimigo, BandoDeGoblins
from jogo.entidades.item    import Item
from jogo.entidades.jogador import Jogador
from jogo.entidades.loja    import Loja
from jogo.sistemas.masmorra import CHANCE_MISS_JOGADOR, LORE, POOL_LOOT

app = FastAPI(title="Randongeon API", version="3.1-lote2a")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ANDAR_MAX_STORY: int = 20


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _get_session(session_id: str) -> GameState:
    try:
        return get_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")


def _jogador_status(state: GameState) -> JogadorStatus:
    """
    Lote 2A: inclui 'andar' e 'inventario' — requeridos pelo client.ts.
    """
    j = state.masmorra.jogador
    inventario = [
        ItemInventario(
            nome=it.nome,
            bonus_atk=getattr(it, "bonus_atk", 0),
            bonus_hp=getattr(it, "bonus_hp", 0),
            bonus_esq=getattr(it, "bonus_esq", 0.0),
        )
        for it in getattr(j, "inventario", [])
    ]
    return JogadorStatus(
        nome=j.nome,
        hp=j.hp,
        hp_max=getattr(j, "hp_max", j.hp),
        atk=j.atk,
        esq=j.esq,
        xp=j.xp,
        nivel=getattr(j, "nivel", 1),    # ← Lote D: nível real (Lote A)
        pontuacao=getattr(j, "pontuacao", 0),  # ← Lote G
        moedas=j.moedas,
        andar=state.masmorra.andar,      # ← novo Lote 2A
        inventario=inventario,            # ← novo Lote 2A
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


def _loja_info(loja: Loja) -> LojaInfo:
    """
    Lote 2A: estrutura FLAT via loja.ofertas (lista de dicts).
    Corrige o bug do Lote 1 que usava loja.itens (AttributeError).
    """
    ofertas = []
    for entrada in loja.ofertas:
        # Loja.ofertas é lista de {"item": Item, "preco": int}
        item  = entrada["item"]
        preco = entrada["preco"]
        ofertas.append(LojaOferta(
            nome=item.nome,
            preco=preco,
            bonus_atk=getattr(item, "bonus_atk", 0),
            bonus_hp=getattr(item, "bonus_hp", 0),
            bonus_esq=getattr(item, "bonus_esq", 0.0),
        ))
    return LojaInfo(ofertas=ofertas)


def _rolar_loot(inimigo: Inimigo):
    chance = 0.50 if inimigo.dificuldade == 3 else getattr(inimigo, "chance_drop", 0.08)
    # Lote D: usa o pool por tipo do inimigo (tabela_loot, Lote C) em vez do
    # POOL_LOOT genérico. Fallback para POOL_LOOT se for um inimigo sem o método.
    pool = inimigo.tabela_loot() if hasattr(inimigo, "tabela_loot") else POOL_LOOT
    return random.choice(pool) if random.random() < chance else None


def _processar_ataque_inimigo(
    state: GameState,
    inimigo: Inimigo,
    mensagem: str,
) -> tuple[int, bool, str]:
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

        # Lifesteal (Nosferatu): cura ao causar dano. Agora com feedback no log.
        if getattr(inimigo, "cura_percentual", 0) and dano_inimigo > 0:
            curou = inimigo.curar(max(1, int(dano_inimigo * inimigo.cura_percentual)))
            if curou > 0:
                mensagem += f" {inimigo.nome} drenou {curou} de vida!"

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
    """Lote 2A: verifica modo=='story' (era 'campaign')."""
    if (
        state.modo == "story"                            # ← era "campaign"
        and state.masmorra.andar >= ANDAR_MAX_STORY
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
    """Lote 2A: aceita 'modo' em vez de 'game_mode'."""
    session_id, state = create_session(req.nome.strip(), req.modo)
    return NewGameResponse(
        session_id=session_id,
        jogador=_jogador_status(state),
        modo=state.modo,
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
        modo=state.modo,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Lore
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/game/{session_id}/lore", response_model=LoreResponse)
def get_lore(session_id: str):
    _get_session(session_id)
    return LoreResponse(linhas=LORE)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Avançar de sala
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/game/{session_id}/advance", response_model=SalaResponse)
def advance(session_id: str):
    state    = _get_session(session_id)
    masmorra = state.masmorra

    state.inimigo_ativo     = None
    state.loja_ativa        = None
    state.sala_pendente     = None
    state.jogador_atordoado = False
    state.fila_inimigos     = []        # Lote E: zera fila de bando anterior

    # Story: andar máximo atingido → re-spawn boss final
    if state.modo == "story" and masmorra.andar_max and masmorra.andar >= masmorra.andar_max:
        boss = masmorra.gerar_boss()
        state.inimigo_ativo = boss
        return SalaResponse(
            tipo="boss",
            descricao="⚠️ O Coração da Masmorra bloqueia a saída! Não há escapatória!",
            andar=masmorra.andar,
            inimigo=_inimigo_info(boss),
            jogador=_jogador_status(state),
        )

    masmorra.andar += 1

    if masmorra.e_andar_de_boss():
        boss = masmorra.gerar_boss()
        state.inimigo_ativo = boss
        return SalaResponse(
            tipo="boss",
            descricao=f"Um guardião emerge das sombras do andar {masmorra.andar}!",
            andar=masmorra.andar,
            inimigo=_inimigo_info(boss),
            jogador=_jogador_status(state),
        )

    tipo, conteudo, descricao = masmorra.gerador.gerar_sala(masmorra.andar)

    if tipo == "inimigo":
        # Lote E: uma horda vira um Bando de Goblins — 3 lutas em sequência.
        if getattr(conteudo, "tipo_especial", None) == "horda":
            fila = BandoDeGoblins().fila()
            state.inimigo_ativo = fila[0]
            state.fila_inimigos = fila[1:]
            conteudo  = fila[0]
            descricao = "Uma horda de goblins irrompe pela porta — eles vêm um atrás do outro!"
        else:
            state.inimigo_ativo = conteudo
        return SalaResponse(
            tipo="inimigo",
            descricao=descricao,
            andar=masmorra.andar,
            inimigo=_inimigo_info(conteudo),
            jogador=_jogador_status(state),
        )

    if tipo == "item":
        state.sala_pendente = {"item": conteudo}
        return SalaResponse(
            tipo="item",
            descricao=descricao,
            andar=masmorra.andar,
            item=_item_info(conteudo) if conteudo else None,
            jogador=_jogador_status(state),
        )

    if tipo == "loja":
        loja = Loja()
        state.loja_ativa = loja
        return SalaResponse(
            tipo="loja",
            descricao=descricao,
            andar=masmorra.andar,
            loja=_loja_info(loja),     # ← usa nova _loja_info() com ofertas flat
            jogador=_jogador_status(state),
        )

    # Fallback
    return SalaResponse(
        tipo=tipo,
        descricao=descricao,
        andar=masmorra.andar,
        jogador=_jogador_status(state),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Atacar
# ═══════════════════════════════════════════════════════════════════════════════

def _resolver_derrota_inimigo(
    session_id: str,
    state: GameState,
    inimigo: Inimigo,
    mensagem: str,
    dano_jogador: int,
    miss_jogador: bool,
) -> CombatActionResponse:
    """
    Inimigo morreu: concede recompensa (XP/moedas/loot) e decide o que vem.

    Lote E: se ainda houver goblins na fila do Bando, retorna resultado
    'proximo' com o próximo inimigo (a luta continua). Caso contrário, encerra
    com 'vitoria' (ou vitória de campanha, se for o boss final).
    Centraliza a lógica antes duplicada em attack e dodge.
    """
    jogador = state.masmorra.jogador
    jogador.ganhar_xp(inimigo.xp)
    jogador.ganhar_moedas(inimigo.moedas)
    loot_drop = _rolar_loot(inimigo)
    if loot_drop:
        jogador.adicionar_item(loot_drop)        # Lote F: loot vai pro inventário
        mensagem += f" ✨ {loot_drop.nome} caiu no chão!"
    mensagem += f" {inimigo.nome} foi derrotado!"

    # Ainda há goblins na fila do bando? → próximo inimigo
    if state.fila_inimigos:
        proximo = state.fila_inimigos.pop(0)
        state.inimigo_ativo = proximo
        return CombatActionResponse(
            resultado="proximo",
            mensagem=mensagem + f" {proximo.nome} avança!",
            dano_jogador=dano_jogador,
            dano_inimigo=0,
            jogador=_jogador_status(state),
            inimigo=_inimigo_info(proximo),
            miss_jogador=miss_jogador,
            miss_inimigo=False,
            loot=_item_info(loot_drop) if loot_drop else None,
        )

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


@app.post("/game/{session_id}/combat/attack", response_model=CombatActionResponse)
def combat_attack(session_id: str):
    state   = _get_session(session_id)
    jogador = state.masmorra.jogador
    inimigo = state.inimigo_ativo

    if inimigo is None:
        raise HTTPException(status_code=400, detail="Sem inimigo ativo")

    miss_jogador = False
    dano_jogador = 0
    loot_drop    = None

    if state.jogador_atordoado:
        state.jogador_atordoado = False
        mensagem = f"{jogador.nome} está atordoado e perde o turno!"
    elif random.random() < CHANCE_MISS_JOGADOR:
        miss_jogador = True
        mensagem = "Você errou o ataque!"
    else:
        dano_jogador = inimigo.receber_dano(jogador.atk)
        mensagem = f"Você causou {dano_jogador} de dano."
        # Lote F: REMOVIDO o heal aqui — o Nosferatu não deve se curar quando
        # APANHA. O lifesteal correto está em _processar_ataque_inimigo (cura
        # quando o inimigo ataca o jogador).

    if inimigo.hp <= 0:
        return _resolver_derrota_inimigo(
            session_id, state, inimigo, mensagem, dano_jogador, miss_jogador
        )

    dano_inimigo, miss_inimigo, mensagem = _processar_ataque_inimigo(state, inimigo, mensagem)

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

    if state.jogador_atordoado:
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
            # Lote F: REMOVIDO o heal aqui (vampiro não cura ao apanhar).

        if inimigo.hp <= 0:
            return _resolver_derrota_inimigo(
                session_id, state, inimigo, mensagem, dano_jogador, miss_jogador
            )

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

    if not mensagem:
        mensagem = "A esquiva falhou!"

    dano_inimigo, miss_inimigo, mensagem = _processar_ataque_inimigo(state, inimigo, mensagem)

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

    # Lote F: fuga de boss na campanha. A cada boss a fuga fica mais difícil;
    # no andar final (20), fugir é IMPOSSÍVEL — vencer ou morrer.
    andar     = state.masmorra.andar
    andar_max = state.masmorra.andar_max
    if state.modo == "story" and inimigo.dificuldade == 3:
        if andar_max and andar >= andar_max:
            mensagem = "Não há para onde fugir! O Coração da Masmorra bloqueia a saída!"
            dano_inimigo, miss_inimigo, mensagem = _processar_ataque_inimigo(
                state, inimigo, mensagem
            )
            if jogador.hp <= 0:
                delete_session(session_id)
                return CombatActionResponse(
                    resultado="derrota",
                    mensagem=mensagem + " Você foi derrotado...",
                    dano_jogador=0, dano_inimigo=dano_inimigo,
                    jogador=_jogador_status(state),
                    miss_inimigo=miss_inimigo,
                )
            return CombatActionResponse(
                resultado="continua",
                mensagem=mensagem,
                dano_jogador=0, dano_inimigo=dano_inimigo,
                jogador=_jogador_status(state),
                inimigo=_inimigo_info(inimigo),
                jogador_atordoado=state.jogador_atordoado,
                miss_inimigo=miss_inimigo,
            )
        # Bosses intermediários: chance de fuga cai conforme o andar.
        inimigo.modificador_fuga = -0.15 * (andar // 5)

    if state.masmorra.tentar_fuga(inimigo):
        state.inimigo_ativo = None
        state.fila_inimigos = []        # Lote E: fugir escapa do bando inteiro
        return CombatActionResponse(
            resultado="fuga",
            mensagem=f"{jogador.nome} fugiu com sucesso!",
            dano_jogador=0,
            dano_inimigo=0,
            jogador=_jogador_status(state),
        )

    mensagem = "A fuga falhou!"
    dano_inimigo, miss_inimigo, mensagem = _processar_ataque_inimigo(state, inimigo, mensagem)

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
# ═══════════════════════════════════════════════════════════════════════════════

_CHANCE_MIMICO = 0.20


@app.post("/game/{session_id}/chest/open", response_model=ChestResponse)
def chest_open(session_id: str):
    state = _get_session(session_id)

    if random.random() < _CHANCE_MIMICO:
        mimico = state.masmorra.gerar_mimico()
        state.inimigo_ativo = mimico
        return ChestResponse(
            tipo="mimico",
            mensagem="Era uma armadilha! Um Mímico ataca!",
            jogador=_jogador_status(state),
            inimigo=_inimigo_info(mimico),
        )

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
# Lote 2A: usa loja.comprar() que retorna {sucesso, mensagem}
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/game/{session_id}/shop/buy", response_model=ShopResponse)
def shop_buy(session_id: str, req: ShopBuyRequest):
    state = _get_session(session_id)
    loja  = state.loja_ativa

    if loja is None:
        raise HTTPException(status_code=400, detail="Nenhuma loja ativa")

    jogador   = state.masmorra.jogador
    resultado = loja.comprar(req.indice, jogador)   # ← usa loja.comprar()

    loja_atualizada = _loja_info(loja) if loja.ofertas else None

    return ShopResponse(
        sucesso=resultado["sucesso"],          # ← bool (era resultado: str)
        mensagem=resultado["mensagem"],
        jogador=_jogador_status(state),
        loja=loja_atualizada,
    )


@app.post("/game/{session_id}/shop/leave", response_model=ShopResponse)
def shop_leave(session_id: str):
    state = _get_session(session_id)
    state.loja_ativa = None
    return ShopResponse(
        sucesso=True,
        mensagem="Você saiu da loja.",
        jogador=_jogador_status(state),
        loja=None,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 12. Desistir
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


# ═══════════════════════════════════════════════════════════════════════════════
# 13. Inventário — usar item durante combate  (NOVO Lote 2A)
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/game/{session_id}/inventory/use", response_model=UseItemResponse)
def inventory_use(session_id: str, req: UseItemRequest):
    state   = _get_session(session_id)
    jogador = state.masmorra.jogador

    if not getattr(jogador, "inventario", None):
        return UseItemResponse(
            sucesso=False,
            mensagem="Inventário vazio.",
            efeito={},
            jogador=_jogador_status(state),
        )

    try:
        efeito = jogador.usar_item(req.indice)
    except IndexError:
        return UseItemResponse(
            sucesso=False,
            mensagem=f"Índice {req.indice} inválido no inventário.",
            efeito={},
            jogador=_jogador_status(state),
        )

    # Serializa efeito: converte valores para float
    efeito_serial = {k: float(v) for k, v in efeito.items()}
    partes = []
    if "hp" in efeito:
        partes.append(f"HP +{efeito['hp']}")
    if "atk" in efeito:
        partes.append(f"ATK +{efeito['atk']}")
    if "esq" in efeito:
        partes.append(f"ESQ +{efeito['esq'] * 100:.0f}%")

    mensagem = "Item usado! " + ", ".join(partes) if partes else "Item sem efeito."

    return UseItemResponse(
        sucesso=True,
        mensagem=mensagem,
        efeito=efeito_serial,
        jogador=_jogador_status(state),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 14. Save — serializar estado da run  (NOVO Lote 2A)
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/game/{session_id}/save", response_model=SaveStateResponse)
def save_game(session_id: str):
    state = _get_session(session_id)
    j     = state.masmorra.jogador

    inventario_serial = [
        {
            "nome":      it.nome,
            "bonus_atk": getattr(it, "bonus_atk", 0),
            "bonus_hp":  getattr(it, "bonus_hp", 0),
            "bonus_esq": getattr(it, "bonus_esq", 0.0),
        }
        for it in getattr(j, "inventario", [])
    ]

    return SaveStateResponse(
        version=1,
        savedAt=datetime.now(timezone.utc).isoformat(),
        playerName=j.nome,
        andar=state.masmorra.andar,
        modo=state.modo,
        jogador={
            "nome":      j.nome,
            "hp":        j.hp,
            "hp_max":    getattr(j, "hp_max", j.hp),
            "atk":       j.atk,
            "xp":        j.xp,
            "nivel":     getattr(j, "nivel", 1),   # ← Lote D: preserva o nível (Lote A)
            "esq":       j.esq,
            "esq_max":   getattr(j, "esq_max", 1),
            "moedas":    j.moedas,
            "inventario": inventario_serial,
        },
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 15. Load — reconstituir sessão de um save  (NOVO Lote 2A)
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/game/load", response_model=LoadGameResponse)
def load_game(req: LoadGameRequest):
    jdata = req.jogador

    try:
        jogador = Jogador(
            nome=str(jdata["nome"]),
            hp=int(jdata["hp_max"]),
            atk=int(jdata["atk"]),
            xp=int(jdata.get("xp", 0)),
            esq=float(jdata.get("esq", 0.3)),
            moedas=int(jdata.get("moedas", 0)),
        )
        jogador.hp = min(int(jdata["hp"]), jogador.hp_max)
        # Lote D: restaura o nível salvo. Sem isso o nível voltaria a 1 e o
        # próximo ganho de XP causaria level-ups duplicados (atk/hp em dobro).
        jogador.nivel = int(jdata.get("nivel", 1))
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=f"Dados do save inválidos: {exc}")

    # Restaura inventário
    for raw in jdata.get("inventario", []) or []:
        try:
            bonus_atk = int(raw.get("bonus_atk", 0))
            bonus_hp  = int(raw.get("bonus_hp", 0))
            bonus_esq = float(raw.get("bonus_esq", 0.0))
            if bonus_atk == 0 and bonus_hp == 0 and bonus_esq == 0.0:
                continue  # item sem bônus não é válido
            it = Item(
                nome=str(raw["nome"]),
                bonus_atk=bonus_atk,
                bonus_hp=bonus_hp,
                bonus_esq=bonus_esq,
            )
            jogador.inventario.append(it)
        except (KeyError, ValueError):
            pass  # item corrompido: ignora

    modo = req.modo if req.modo in {"story", "infinite"} else "story"
    session_id, state = load_session(jogador, modo=modo, andar=req.andar)

    return LoadGameResponse(
        session_id=session_id,
        jogador=_jogador_status(state),
        modo=state.modo,
    )