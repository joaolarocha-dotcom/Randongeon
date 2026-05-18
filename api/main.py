import sys
import os
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "randongeon"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from session import GameState, create_session, get_session, delete_session
from schemas import (
    NewGameRequest, NewGameResponse, JogadorStatus, SalaResponse,
    InimigoInfo, ItemInfo, LojaInfo, LojaOferta, CombatActionResponse,
    ChestResponse, ShopBuyRequest, ShopBuyResponse, LoreResponse,
    GameOverResponse,
)

from jogo.entidades.inimigo import Inimigo
from jogo.entidades.loja import Loja
from jogo.sistemas.masmorra import LORE

app = FastAPI(title="Randongeon API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_state(session_id: str) -> GameState:
    state = get_session(session_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")
    return state


def _jogador_status(state: GameState) -> JogadorStatus:
    j = state.masmorra.jogador
    return JogadorStatus(
        nome=j.nome,
        hp=j.hp,
        hp_max=j.hp_max,
        atk=j.atk,
        esq=j.esq,
        xp=j.xp,
        moedas=j.moedas,
        andar=state.masmorra.andar,
    )


def _inimigo_info(inimigo: Inimigo, hp_max: int = None) -> InimigoInfo:
    return InimigoInfo(
        nome=inimigo.nome,
        hp=inimigo.hp,
        hp_max=hp_max if hp_max else inimigo.hp,
        atk=inimigo.atk,
        dificuldade=inimigo.dificuldade,
    )


def _loja_info(loja: Loja) -> LojaInfo:
    ofertas = []
    for oferta in loja.ofertas:
        item = oferta["item"]
        ofertas.append(LojaOferta(
            nome=item.nome,
            preco=oferta["preco"],
            bonus_atk=item.bonus_atk,
            bonus_hp=item.bonus_hp,
            bonus_esq=item.bonus_esq,
        ))
    return LojaInfo(ofertas=ofertas)


# ── Endpoints ─────────────────────────────────────────────────────────────────


@app.post("/game/new", response_model=NewGameResponse)
def new_game(req: NewGameRequest):
    if not req.nome.strip():
        raise HTTPException(status_code=400, detail="Nome não pode ser vazio.")
    session_id, state = create_session(req.nome.strip())
    return NewGameResponse(session_id=session_id, jogador=_jogador_status(state))


@app.get("/game/{session_id}/status", response_model=JogadorStatus)
def get_status(session_id: str):
    state = _get_state(session_id)
    return _jogador_status(state)


@app.get("/game/{session_id}/lore", response_model=LoreResponse)
def get_lore(session_id: str):
    _get_state(session_id)
    return LoreResponse(linhas=LORE)


@app.post("/game/{session_id}/advance", response_model=SalaResponse)
def advance(session_id: str):
    state = _get_state(session_id)
    masmorra = state.masmorra

    if not masmorra.jogador.esta_vivo():
        raise HTTPException(status_code=400, detail="Jogador está morto.")

    masmorra.andar += 1

    if masmorra.e_andar_de_boss():
        boss = masmorra.gerar_boss()
        state.inimigo_ativo = boss
        state.sala_pendente = {"hp_max": boss.hp}
        return SalaResponse(
            tipo="boss",
            descricao=f"⚠️ Um BOSS bloqueia o caminho! {boss.nome} apareceu!",
            andar=masmorra.andar,
            inimigo=_inimigo_info(boss),
            jogador=_jogador_status(state),
        )

    tipo, conteudo, descricao = masmorra.gerador.gerar_sala(masmorra.andar)

    if tipo == "loja":
        loja = Loja()
        state.loja_ativa = loja
        state.inimigo_ativo = None
        return SalaResponse(
            tipo="loja",
            descricao=descricao,
            andar=masmorra.andar,
            loja=_loja_info(loja),
            jogador=_jogador_status(state),
        )

    elif tipo == "item":
        e_mimico = random.randint(1, 20) == 1
        if e_mimico:
            state.sala_pendente = {"tipo_real": "mimico"}
        else:
            state.sala_pendente = {"tipo_real": "item", "item": conteudo}
        return SalaResponse(
            tipo="item",
            descricao="Você avista um baú antigo no centro da sala.",
            andar=masmorra.andar,
            item=ItemInfo(
                nome=conteudo.nome,
                bonus_atk=conteudo.bonus_atk,
                bonus_hp=conteudo.bonus_hp,
                bonus_esq=conteudo.bonus_esq,
            ) if not e_mimico else None,
            jogador=_jogador_status(state),
        )

    else:  # inimigo
        e_mimico = random.randint(1, 20) == 1
        if e_mimico:
            state.sala_pendente = {"tipo_real": "mimico_disfarce"}
            return SalaResponse(
                tipo="item",
                descricao="Você avista um baú antigo no centro da sala.",
                andar=masmorra.andar,
                jogador=_jogador_status(state),
            )
        else:
            state.inimigo_ativo = conteudo
            state.sala_pendente = {"hp_max": conteudo.hp}
            return SalaResponse(
                tipo="inimigo",
                descricao=descricao,
                andar=masmorra.andar,
                inimigo=_inimigo_info(conteudo),
                jogador=_jogador_status(state),
            )


# ── Combate ───────────────────────────────────────────────────────────────────


def _get_inimigo_hp_max(state: GameState) -> int:
    if state.sala_pendente and "hp_max" in state.sala_pendente:
        return state.sala_pendente["hp_max"]
    if state.inimigo_ativo:
        return state.inimigo_ativo.hp
    return 0


@app.post("/game/{session_id}/combat/attack", response_model=CombatActionResponse)
def combat_attack(session_id: str):
    state = _get_state(session_id)
    inimigo = state.inimigo_ativo
    if inimigo is None:
        raise HTTPException(status_code=400, detail="Nenhum combate ativo.")

    jogador = state.masmorra.jogador
    hp_max_inimigo = _get_inimigo_hp_max(state)

    dano_no_inimigo = inimigo.receber_dano(jogador.atk)
    dano_no_jogador = 0
    mensagem = f"Você causou {dano_no_inimigo} de dano."

    if inimigo.esta_vivo():
        dano_no_jogador = jogador.receber_dano(inimigo.atk)
        mensagem += f" {inimigo.nome} causou {dano_no_jogador} de dano em você."

    if not jogador.esta_vivo():
        state.inimigo_ativo = None
        return CombatActionResponse(
            resultado="derrota",
            mensagem=f"{jogador.nome} foi derrotado...",
            dano_jogador=dano_no_jogador,
            dano_inimigo=dano_no_inimigo,
            jogador=_jogador_status(state),
            inimigo=_inimigo_info(inimigo, hp_max_inimigo),
        )

    if not inimigo.esta_vivo():
        jogador.ganhar_xp(inimigo.xp)
        jogador.ganhar_moedas(inimigo.moedas)
        state.inimigo_ativo = None
        return CombatActionResponse(
            resultado="vitoria",
            mensagem=f"Você derrotou {inimigo.nome}! +{inimigo.xp} XP, +{inimigo.moedas} moedas.",
            dano_jogador=dano_no_jogador,
            dano_inimigo=dano_no_inimigo,
            jogador=_jogador_status(state),
            inimigo=_inimigo_info(inimigo, hp_max_inimigo),
        )

    return CombatActionResponse(
        resultado="continua",
        mensagem=mensagem,
        dano_jogador=dano_no_jogador,
        dano_inimigo=dano_no_inimigo,
        jogador=_jogador_status(state),
        inimigo=_inimigo_info(inimigo, hp_max_inimigo),
    )


@app.post("/game/{session_id}/combat/dodge", response_model=CombatActionResponse)
def combat_dodge(session_id: str):
    state = _get_state(session_id)
    inimigo = state.inimigo_ativo
    if inimigo is None:
        raise HTTPException(status_code=400, detail="Nenhum combate ativo.")

    jogador = state.masmorra.jogador
    hp_max_inimigo = _get_inimigo_hp_max(state)

    dano_no_inimigo = 0
    dano_no_jogador = 0

    if random.random() <= jogador.esq:
        dano_no_inimigo = inimigo.receber_dano(jogador.atk)
        mensagem = f"Esquiva bem-sucedida! Você causou {dano_no_inimigo} de dano sem ser atingido."
    else:
        dano_no_jogador = jogador.receber_dano(inimigo.atk * 2)
        mensagem = f"Esquiva falhou! {inimigo.nome} causou {dano_no_jogador} de dano (dobrado)."

    if not jogador.esta_vivo():
        state.inimigo_ativo = None
        return CombatActionResponse(
            resultado="derrota",
            mensagem=f"{jogador.nome} foi derrotado...",
            dano_jogador=dano_no_jogador,
            dano_inimigo=dano_no_inimigo,
            jogador=_jogador_status(state),
            inimigo=_inimigo_info(inimigo, hp_max_inimigo),
        )

    if not inimigo.esta_vivo():
        jogador.ganhar_xp(inimigo.xp)
        jogador.ganhar_moedas(inimigo.moedas)
        state.inimigo_ativo = None
        return CombatActionResponse(
            resultado="vitoria",
            mensagem=f"Você derrotou {inimigo.nome}! +{inimigo.xp} XP, +{inimigo.moedas} moedas.",
            dano_jogador=dano_no_jogador,
            dano_inimigo=dano_no_inimigo,
            jogador=_jogador_status(state),
            inimigo=_inimigo_info(inimigo, hp_max_inimigo),
        )

    return CombatActionResponse(
        resultado="continua",
        mensagem=mensagem,
        dano_jogador=dano_no_jogador,
        dano_inimigo=dano_no_inimigo,
        jogador=_jogador_status(state),
        inimigo=_inimigo_info(inimigo, hp_max_inimigo),
    )


@app.post("/game/{session_id}/combat/flee", response_model=CombatActionResponse)
def combat_flee(session_id: str):
    state = _get_state(session_id)
    inimigo = state.inimigo_ativo
    if inimigo is None:
        raise HTTPException(status_code=400, detail="Nenhum combate ativo.")

    jogador = state.masmorra.jogador
    hp_max_inimigo = _get_inimigo_hp_max(state)

    if state.masmorra.tentar_fuga():
        state.inimigo_ativo = None
        return CombatActionResponse(
            resultado="fuga",
            mensagem="Você fugiu da batalha!",
            dano_jogador=0,
            dano_inimigo=0,
            jogador=_jogador_status(state),
            inimigo=_inimigo_info(inimigo, hp_max_inimigo),
        )

    dano_no_jogador = jogador.receber_dano(inimigo.atk)
    mensagem = f"Fuga falhou! {inimigo.nome} causou {dano_no_jogador} de dano."

    if not jogador.esta_vivo():
        state.inimigo_ativo = None
        return CombatActionResponse(
            resultado="derrota",
            mensagem=f"{jogador.nome} foi derrotado...",
            dano_jogador=dano_no_jogador,
            dano_inimigo=0,
            jogador=_jogador_status(state),
            inimigo=_inimigo_info(inimigo, hp_max_inimigo),
        )

    return CombatActionResponse(
        resultado="continua",
        mensagem=mensagem,
        dano_jogador=dano_no_jogador,
        dano_inimigo=0,
        jogador=_jogador_status(state),
        inimigo=_inimigo_info(inimigo, hp_max_inimigo),
    )


# ── Baú ───────────────────────────────────────────────────────────────────────


@app.post("/game/{session_id}/chest/open", response_model=ChestResponse)
def chest_open(session_id: str):
    state = _get_state(session_id)
    pendente = state.sala_pendente

    if pendente is None:
        raise HTTPException(status_code=400, detail="Nenhum baú pendente.")

    tipo_real = pendente.get("tipo_real", "")

    if tipo_real in ("mimico", "mimico_disfarce"):
        mimico = state.masmorra.gerar_mimico()
        state.inimigo_ativo = mimico
        state.sala_pendente = {"hp_max": mimico.hp}
        return ChestResponse(
            tipo="mimico",
            mensagem="ERA UM MÍMICO DISFARÇADO!!!",
            inimigo=_inimigo_info(mimico),
            jogador=_jogador_status(state),
        )

    item = pendente.get("item")
    if item is None:
        raise HTTPException(status_code=400, detail="Nenhum item no baú.")

    resultado = state.masmorra.aplicar_item(item)
    state.sala_pendente = None
    return ChestResponse(
        tipo="item",
        mensagem=f"Você encontrou: {item.nome}!",
        item=ItemInfo(
            nome=item.nome,
            bonus_atk=item.bonus_atk,
            bonus_hp=item.bonus_hp,
            bonus_esq=item.bonus_esq,
        ),
        jogador=_jogador_status(state),
    )


@app.post("/game/{session_id}/chest/ignore", response_model=ChestResponse)
def chest_ignore(session_id: str):
    state = _get_state(session_id)
    state.sala_pendente = None
    state.inimigo_ativo = None
    return ChestResponse(
        tipo="item",
        mensagem="Você ignorou o baú.",
        jogador=_jogador_status(state),
    )


# ── Loja ──────────────────────────────────────────────────────────────────────


@app.post("/game/{session_id}/shop/buy", response_model=ShopBuyResponse)
def shop_buy(session_id: str, req: ShopBuyRequest):
    state = _get_state(session_id)
    loja = state.loja_ativa
    if loja is None:
        raise HTTPException(status_code=400, detail="Nenhuma loja ativa.")

    resultado = loja.comprar(req.indice, state.masmorra.jogador)

    loja_info = _loja_info(loja) if loja.ofertas else None
    if not loja.ofertas:
        state.loja_ativa = None

    return ShopBuyResponse(
        sucesso=resultado["sucesso"],
        mensagem=resultado["mensagem"],
        jogador=_jogador_status(state),
        loja=loja_info,
    )


@app.post("/game/{session_id}/shop/leave", response_model=ShopBuyResponse)
def shop_leave(session_id: str):
    state = _get_state(session_id)
    state.loja_ativa = None
    return ShopBuyResponse(
        sucesso=True,
        mensagem="O mercador recolhe as coisas e acena um adeus.",
        jogador=_jogador_status(state),
        loja=None,
    )


# ── Quit ──────────────────────────────────────────────────────────────────────


@app.post("/game/{session_id}/quit", response_model=GameOverResponse)
def quit_game(session_id: str):
    state = _get_state(session_id)
    state.masmorra.desistiu = True
    response = GameOverResponse(
        mensagem=f"{state.masmorra.jogador.nome} desistiu no andar {state.masmorra.andar}.",
        jogador=_jogador_status(state),
    )
    delete_session(session_id)
    return response
