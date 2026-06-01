"""
Testes da API (FastAPI TestClient) — Lote D.

Valida o contrato que o frontend (client.ts) consome: modo, ofertas flat,
sucesso bool, /inventory/use, /save, /load, e a integração com o game logic
atual (nível do Lote A, loot por tipo do Lote C).

Rodar:  cd api && ../randongeon/.venv/Scripts/python.exe -m pytest test_api.py -q
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pytest
from fastapi.testclient import TestClient

# IMPORTANTE: importar 'main' ANTES de 'session'. main.py (api/) insere a pasta
# randongeon no sys.path; como existe um randongeon/main.py, importar 'session'
# primeiro empurraria randongeon para a frente e 'main' resolveria para o arquivo
# errado. Importando api/main.py primeiro (api/ está em sys.path[0]), evitamos isso.
from main import app
import session as session_mod
from jogo.entidades.inimigo import Inimigo, BandoDeGoblins
from jogo.entidades.item import Item
from jogo.entidades.loja import Loja

client = TestClient(app)


def _nova_sessao(modo="story", nome="Heroi"):
    r = client.post("/game/new", json={"nome": nome, "modo": modo})
    assert r.status_code == 200
    return r.json()


# ── /game/new e contrato do JogadorStatus ─────────────────────────────────────

class TestNewGame:
    def test_new_game_story(self):
        data = _nova_sessao("story")
        assert "session_id" in data
        assert data["modo"] == "story"
        j = data["jogador"]
        # campos que o client.ts exige
        for campo in ("nome", "hp", "hp_max", "atk", "esq", "xp",
                      "nivel", "moedas", "andar", "inventario"):
            assert campo in j, f"faltou {campo} no JogadorStatus"
        assert j["nivel"] == 1
        assert j["inventario"] == []

    def test_new_game_infinite_propaga_modo_na_masmorra(self):
        data = _nova_sessao("infinite")
        assert data["modo"] == "infinite"
        # Bug do Lote 1 (corrigido): a Masmorra precisa receber modo=infinite.
        state = session_mod.get_session(data["session_id"])
        assert state.masmorra.modo == "infinite"

    def test_modo_invalido_cai_para_story(self):
        data = _nova_sessao("hardcore")
        assert data["modo"] == "story"


# ── /status e /advance ────────────────────────────────────────────────────────

class TestStatusAdvance:
    def test_status_retorna_modo(self):
        data = _nova_sessao("infinite")
        r = client.get(f"/game/{data['session_id']}/status")
        assert r.status_code == 200
        assert r.json()["modo"] == "infinite"

    def test_advance_retorna_sala_valida(self):
        data = _nova_sessao("story")
        r = client.post(f"/game/{data['session_id']}/advance")
        assert r.status_code == 200
        sala = r.json()
        assert sala["tipo"] in ("inimigo", "item", "loja", "boss")
        assert sala["jogador"]["andar"] == 1


# ── Loja: contrato 'ofertas' flat + 'sucesso' bool ────────────────────────────

class TestLoja:
    def test_compra_retorna_sucesso_bool_e_ofertas_flat(self):
        data = _nova_sessao("story")
        sid = data["session_id"]
        state = session_mod.get_session(sid)
        state.loja_ativa = Loja()
        state.masmorra.jogador.moedas = 100

        r = client.post(f"/game/{sid}/shop/buy", json={"indice": 0})
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body["sucesso"], bool)
        assert body["sucesso"] is True
        # loja remanescente vem com 'ofertas' flat (não 'itens' aninhado)
        if body["loja"] is not None:
            assert "ofertas" in body["loja"]
            for of in body["loja"]["ofertas"]:
                assert {"nome", "preco", "bonus_atk", "bonus_hp", "bonus_esq"} <= set(of)
        # item foi para o inventário
        assert len(body["jogador"]["inventario"]) == 1

    def test_compra_sem_moedas_falha(self):
        data = _nova_sessao("story")
        sid = data["session_id"]
        state = session_mod.get_session(sid)
        state.loja_ativa = Loja()
        state.masmorra.jogador.moedas = 0
        r = client.post(f"/game/{sid}/shop/buy", json={"indice": 0})
        assert r.json()["sucesso"] is False

    def test_shop_leave(self):
        data = _nova_sessao("story")
        sid = data["session_id"]
        session_mod.get_session(sid).loja_ativa = Loja()
        r = client.post(f"/game/{sid}/shop/leave")
        assert r.json()["sucesso"] is True
        assert session_mod.get_session(sid).loja_ativa is None


# ── Combate ───────────────────────────────────────────────────────────────────

class TestCombate:
    def test_ataque_derrota_inimigo_fraco_e_concede_recompensa(self):
        data = _nova_sessao("story")
        sid = data["session_id"]
        state = session_mod.get_session(sid)
        state.masmorra.jogador.atk = 50
        moedas_antes = state.masmorra.jogador.moedas
        state.inimigo_ativo = Inimigo("Alvo", hp=1, atk=1, dificuldade=1, xp=5, moedas=7)

        resultado = "continua"
        for _ in range(5):
            r = client.post(f"/game/{sid}/combat/attack")
            assert r.status_code == 200
            resultado = r.json()["resultado"]
            if resultado != "continua":
                break
        assert resultado == "vitoria"
        assert state.masmorra.jogador.moedas == moedas_antes + 7


# ── Inventário (a feature recuperada) ─────────────────────────────────────────

class TestInventario:
    def test_usar_item_aplica_efeito_e_remove(self):
        data = _nova_sessao("story")
        sid = data["session_id"]
        jog = session_mod.get_session(sid).masmorra.jogador
        jog.hp = 10
        jog.adicionar_item(Item("Poção", bonus_hp=5))

        r = client.post(f"/game/{sid}/inventory/use", json={"indice": 0})
        assert r.status_code == 200
        body = r.json()
        assert body["sucesso"] is True
        assert body["efeito"].get("hp") == 5
        assert jog.hp == 15
        assert body["jogador"]["inventario"] == []   # item consumido

    def test_usar_indice_invalido_falha(self):
        data = _nova_sessao("story")
        sid = data["session_id"]
        r = client.post(f"/game/{sid}/inventory/use", json={"indice": 0})
        assert r.json()["sucesso"] is False


# ── Save / Load (preserva o nível — integração com Lote A) ────────────────────

class TestSaveLoad:
    def test_save_load_round_trip_preserva_nivel(self):
        data = _nova_sessao("story")
        sid = data["session_id"]
        jog = session_mod.get_session(sid).masmorra.jogador
        jog.ganhar_xp(60)                 # sobe para o nível 3
        assert jog.nivel == 3
        atk_apos_nivel = jog.atk          # 5 + 2*2 = 9

        save = client.get(f"/game/{sid}/save").json()
        assert save["jogador"]["nivel"] == 3

        load = client.post("/game/load", json=save).json()
        assert load["modo"] == "story"
        jl = load["jogador"]
        # nível e atk preservados, SEM level-up duplicado
        assert jl["nivel"] == 3
        assert jl["atk"] == atk_apos_nivel

    def test_save_preserva_inventario(self):
        data = _nova_sessao("story")
        sid = data["session_id"]
        session_mod.get_session(sid).masmorra.jogador.adicionar_item(
            Item("Relíquia", bonus_atk=2)
        )
        save = client.get(f"/game/{sid}/save").json()
        load = client.post("/game/load", json=save).json()
        nomes = [it["nome"] for it in load["jogador"]["inventario"]]
        assert "Relíquia" in nomes


# ── Bando de Goblins: combate sequencial (Lote E) ─────────────────────────────

class TestBandoSequencial:
    def _montar_bando(self, sid):
        """Coloca um bando de 3 goblins (cada um com 1 HP) como inimigo ativo."""
        state = session_mod.get_session(sid)
        state.masmorra.jogador.atk = 100        # mata cada goblin num golpe
        fila = BandoDeGoblins().fila()
        for g in fila:
            g.hp = 1
        state.inimigo_ativo = fila[0]
        state.fila_inimigos = fila[1:]
        return state

    def test_derrotar_goblin_traz_o_proximo(self):
        sid = _nova_sessao("story")["session_id"]
        state = self._montar_bando(sid)

        resultados = []
        for _ in range(20):
            r = client.post(f"/game/{sid}/combat/attack").json()
            resultados.append(r["resultado"])
            if r["resultado"] in ("vitoria", "derrota"):
                break

        # 2 transições "proximo" (goblin 1→2 e 2→3) e encerra em "vitoria"
        assert resultados.count("proximo") == 2
        assert resultados[-1] == "vitoria"
        assert state.fila_inimigos == []
        assert state.inimigo_ativo is None

    def test_cada_goblin_concede_recompensa(self):
        sid = _nova_sessao("story")["session_id"]
        state = self._montar_bando(sid)
        moedas_antes = state.masmorra.jogador.moedas
        total_moedas_bando = sum(g.moedas for g in [state.inimigo_ativo, *state.fila_inimigos])

        for _ in range(20):
            r = client.post(f"/game/{sid}/combat/attack").json()
            if r["resultado"] in ("vitoria", "derrota"):
                break
        # ganhou as moedas dos 3 goblins
        assert state.masmorra.jogador.moedas == moedas_antes + total_moedas_bando

    def test_fuga_escapa_do_bando_inteiro(self):
        sid = _nova_sessao("story")["session_id"]
        state = self._montar_bando(sid)
        state.masmorra.tentar_fuga = lambda inimigo=None: True   # força fuga
        r = client.post(f"/game/{sid}/combat/flee").json()
        assert r["resultado"] == "fuga"
        assert state.fila_inimigos == []
        assert state.inimigo_ativo is None
