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
from jogo.entidades.efeitos import Veneno, Fraqueza

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
        # Lote F: toda run começa com 2 itens iniciais
        assert len(j["inventario"]) == 2

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
        state.masmorra.jogador.inventario.clear()    # isola dos itens iniciais
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
        # item comprado foi para o inventário
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
        jog.inventario.clear()                 # isola dos itens iniciais
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
        session_mod.get_session(sid).masmorra.jogador.inventario.clear()
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

    def test_save_load_round_trip_preserva_critico(self):
        # Lote crítico: a chance de crítico (relevante p/ o dom Sortudo) sobrevive ao save.
        data = _nova_sessao("story")
        sid = data["session_id"]
        jog = session_mod.get_session(sid).masmorra.jogador
        jog.chance_critico = 0.42
        save = client.get(f"/game/{sid}/save").json()
        assert abs(save["jogador"]["chance_critico"] - 0.42) < 1e-9

        load = client.post("/game/load", json=save).json()
        novo_sid = load["session_id"]
        jl = session_mod.get_session(novo_sid).masmorra.jogador
        assert abs(jl.chance_critico - 0.42) < 1e-9

    def test_save_load_round_trip_preserva_veneno(self):
        # Lote save: o veneno em andamento deve sobreviver ao save/load (.txt).
        data = _nova_sessao("story")
        sid = data["session_id"]
        jog = session_mod.get_session(sid).masmorra.jogador
        jog.envenenar()                       # veneno_turnos = VENENO_DURACAO
        save = client.get(f"/game/{sid}/save").json()
        assert save["jogador"]["veneno_turnos"] == jog.veneno_turnos

        load = client.post("/game/load", json=save).json()
        novo_sid = load["session_id"]
        jl = session_mod.get_session(novo_sid).masmorra.jogador
        assert jl.veneno_turnos == jog.veneno_turnos


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

    def test_texto_diferencia_goblin_individual_do_bando(self):
        # Lote 2 textos: goblin intermediário cai um por um; o "Bando foi
        # derrotado" só aparece quando o ÚLTIMO tomba.
        # Robusto a misses do jogador (10%): coletamos as mensagens até a vitória.
        sid = _nova_sessao("story")["session_id"]
        self._montar_bando(sid)

        msgs = []
        resultado = None
        for _ in range(30):
            r = client.post(f"/game/{sid}/combat/attack").json()
            msgs.append(r["mensagem"])
            resultado = r["resultado"]
            if resultado in ("vitoria", "derrota"):
                break

        assert resultado == "vitoria"
        # transições intermediárias falam de UM goblin, nunca do bando inteiro
        intermediarias = [m for m in msgs if "Outro goblin avança" in m]
        assert intermediarias, "esperava ao menos uma transição de goblin individual"
        for m in intermediarias:
            assert "O goblin foi derrotado" in m
            assert "Bando de Goblins foi derrotado" not in m
        # só a mensagem final anuncia a derrota do bando
        assert "Bando de Goblins foi derrotado" in msgs[-1]


# ── Correções do Lote F ───────────────────────────────────────────────────────

class TestCorrecoesLoteF:
    def test_loot_vai_para_inventario(self):
        sid = _nova_sessao("story")["session_id"]
        state = session_mod.get_session(sid)
        jog = state.masmorra.jogador
        jog.inventario.clear()
        jog.atk = 100
        alvo = Inimigo("Alvo", hp=1, atk=1, dificuldade=1, xp=5, moedas=2)
        alvo.chance_drop = 1.0                  # dropa sempre
        state.inimigo_ativo = alvo
        for _ in range(5):
            r = client.post(f"/game/{sid}/combat/attack").json()
            if r["resultado"] in ("vitoria", "derrota"):
                break
        assert len(jog.inventario) >= 1          # loot foi pro inventário

    def test_inventario_inicial_tem_dois_itens(self):
        data = _nova_sessao("infinite")          # vale para qualquer modo
        assert len(data["jogador"]["inventario"]) == 2

    def test_nosferatu_cura_ao_atacar_com_mensagem(self):
        from main import _processar_ataque_inimigo
        from jogo.entidades.inimigo import Nosferatu
        sid = _nova_sessao("story")["session_id"]
        state = session_mod.get_session(sid)
        nosf = Nosferatu()
        nosf.hp = 5
        nosf.atk = 10
        nosf.chance_miss = 0.0                   # garante o acerto
        state.inimigo_ativo = nosf
        _, miss, msg = _processar_ataque_inimigo(state, nosf, "")
        assert miss is False
        assert nosf.hp > 5                        # se curou
        assert "drenou" in msg                    # com feedback no log

    def test_boss_final_nao_pode_fugir(self):
        sid = _nova_sessao("story")["session_id"]
        state = session_mod.get_session(sid)
        state.masmorra.andar = state.masmorra.andar_max   # andar 20
        state.inimigo_ativo = state.masmorra.gerar_boss()
        state.masmorra.tentar_fuga = lambda inimigo=None: True  # mesmo forçando
        r = client.post(f"/game/{sid}/combat/flee").json()
        assert r["resultado"] != "fuga"           # não conseguiu fugir
        assert state.inimigo_ativo is not None     # boss continua na luta

    def test_boss_intermediario_fuga_fica_mais_dificil(self):
        # No andar 15 o boss recebe modificador de fuga negativo forte.
        sid = _nova_sessao("story")["session_id"]
        state = session_mod.get_session(sid)
        state.masmorra.andar = 15
        boss = state.masmorra.gerar_boss()
        state.inimigo_ativo = boss
        # tenta fugir uma vez (cai no ramo que ajusta modificador_fuga)
        client.post(f"/game/{sid}/combat/flee")
        assert boss.modificador_fuga == -0.15 * (15 // 5)   # -0.45


# ── Vitória de campanha + pontuação (Lote G) ──────────────────────────────────

class TestVitoriaCampanha:
    def test_boss_andar_20_renasce_uma_vez_e_so_a_2a_morte_vence(self):
        """Lote 4: o Coração da Masmorra tem 2 fases — a 1ª morte o faz renascer
        a 50% e em fúria; só a 2ª morte dispara a vitória de campanha."""
        sid = _nova_sessao("story")["session_id"]
        state = session_mod.get_session(sid)
        jog = state.masmorra.jogador
        jog.atk = 1000
        jog.hp = jog.hp_max = 10000        # blinda contra o contra-ataque em fúria
        state.masmorra.andar = state.masmorra.andar_max   # andar 20
        boss = state.masmorra.gerar_boss()
        boss.hp = 1
        state.inimigo_ativo = boss

        # 1ª morte → renasce (NÃO vence a campanha ainda) e volta a 50% do HP máx.
        r1 = client.post(f"/game/{sid}/combat/attack").json()
        assert r1["resultado"] == "renasceu"
        assert r1["inimigo"]["hp"] == round(boss.hp_max * 0.50)

        # 2ª morte → agora sim a campanha é vencida.
        resultado = "continua"
        for _ in range(5):
            r = client.post(f"/game/{sid}/combat/attack").json()
            resultado = r["resultado"]
            if resultado != "continua":
                break
        assert resultado == "vitoria_campanha"

    def test_status_inclui_pontuacao(self):
        sid = _nova_sessao("story")["session_id"]
        jog = session_mod.get_session(sid).masmorra.jogador
        jog.ganhar_xp(20)                  # sobe para o nível 2
        r = client.get(f"/game/{sid}/status").json()
        assert "pontuacao" in r["jogador"]
        assert r["jogador"]["pontuacao"] == jog.pontuacao

    def test_status_inclui_score_com_andar(self):
        sid = _nova_sessao("infinite")["session_id"]
        state = session_mod.get_session(sid)
        state.masmorra.andar = 5
        r = client.get(f"/game/{sid}/status").json()
        # score = pontuacao + andar*100
        assert r["jogador"]["score"] == state.masmorra.calcular_score()
        assert r["jogador"]["score"] >= 500   # pelo menos o bônus do andar 5


# ── Dom de slot único (Lote 3) ────────────────────────────────────────────────

class TestDomAPI:
    def test_new_game_com_dom_aplica_passivo(self):
        r = client.post("/game/new", json={"nome": "H", "modo": "story", "dom": "sanguessuga"}).json()
        jog = session_mod.get_session(r["session_id"]).masmorra.jogador
        assert jog.dom == "sanguessuga"
        assert jog.lifesteal == 0.10

    def test_new_game_sem_dom_ok(self):
        r = client.post("/game/new", json={"nome": "H", "modo": "story"}).json()
        jog = session_mod.get_session(r["session_id"]).masmorra.jogador
        assert jog.dom is None

    def test_save_load_preserva_dom(self):
        r = client.post("/game/new", json={"nome": "H", "modo": "story", "dom": "agil"}).json()
        sid = r["session_id"]
        save = client.get(f"/game/{sid}/save").json()
        assert save["jogador"]["dom"] == "agil"
        load = client.post("/game/load", json=save).json()
        jl = session_mod.get_session(load["session_id"]).masmorra.jogador
        assert jl.dom == "agil"
        assert jl.evasao_passiva == 0.10


# ── Lote 5: efeitos de status expostos no JogadorStatus (badges na UI) ─────────

class TestEfeitosNoStatus:
    def test_sem_efeitos_lista_vazia(self):
        sid = _nova_sessao("story")["session_id"]
        j = client.get(f"/game/{sid}/status").json()["jogador"]
        assert j["efeitos"] == []
        assert j["dom"] is None
        assert j["lifesteal"] == 0.0

    def test_efeitos_ativos_aparecem_com_turnos(self):
        sid = _nova_sessao("story")["session_id"]
        jog = session_mod.get_session(sid).masmorra.jogador
        jog.aplicar_efeito(Veneno(3))
        jog.aplicar_efeito(Fraqueza(2))
        efeitos = client.get(f"/game/{sid}/status").json()["jogador"]["efeitos"]
        por_tipo = {e["tipo"]: e["turnos"] for e in efeitos}
        assert por_tipo == {"veneno": 3, "fraqueza": 2}

    def test_dom_e_passivos_expostos(self):
        r = client.post("/game/new", json={"nome": "H", "modo": "story", "dom": "sanguessuga"}).json()
        j = client.get(f"/game/{r['session_id']}/status").json()["jogador"]
        assert j["dom"] == "sanguessuga"
        assert j["lifesteal"] == 0.10


# ── Feedback de level-up (mensagem + barra de XP correta) ──────────────────────

class TestLevelUpFeedback:
    def test_status_inclui_progresso_de_nivel(self):
        sid = _nova_sessao("story")["session_id"]
        j = client.get(f"/game/{sid}/status").json()["jogador"]
        assert j["xp_nivel_atual"] == 0
        assert j["xp_nivel_total"] == 20      # nível 1 → 2 custa 20 XP (curva real)

    def test_combate_que_sobe_nivel_anuncia_parabens(self):
        from unittest.mock import patch
        sid = _nova_sessao("story")["session_id"]
        state = session_mod.get_session(sid)
        jog = state.masmorra.jogador
        jog.atk = 1000                        # one-shot
        inimigo = Inimigo("Goblin", hp=1, atk=1, dificuldade=1, xp=25, moedas=0)
        state.inimigo_ativo = inimigo

        # random alto → jogador não erra o golpe (evita o miss de 10%).
        with patch("main.random.random", return_value=0.99):
            r = client.post(f"/game/{sid}/combat/attack").json()
        assert r["resultado"] == "vitoria"
        assert "PARABÉNS" in r["mensagem"]    # anunciou o level-up
        assert r["jogador"]["nivel"] == 2     # 25 XP → nível 2
