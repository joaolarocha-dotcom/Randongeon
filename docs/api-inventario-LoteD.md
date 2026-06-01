# 📘 Lote D — Ressincronização da API + Recuperação do Inventário

> Documento de estudo/revisão. Branch: `api-inventario-LoteD`.
> Natureza: **integração/reconciliação** (menos POO novo, mais contrato e serialização).

---

## 1. O problema

O **frontend** (`client.ts`) estava no contrato novo ("Lote 2A"), mas o **backend
da API** havia ficado no contrato antigo ("Lote 1"). Resultado: o jogo web quebrava.

| Aspecto | Frontend espera | Backend entregava | Efeito |
|---|---|---|---|
| Modo | `modo: story\|infinite` | `game_mode: campaign\|infinite` | modo ignorado |
| Loja | `ofertas` flat | lia `loja.itens` (inexistente) | **crash 500** |
| Compra | `sucesso: bool` | `resultado: str` | quebrado |
| Inventário | `/inventory/use` | **não existia** | **feature perdida** |
| Save/Load | `/save`, `/load` | **não existiam** | quebrado |

Causa: um merge anterior trouxe a versão antiga de `api/main.py` (o "inventário
perdido" estava no commit **`7fb53bc`**), e o `session.py` nem passava `modo=` à
Masmorra (o modo infinito não usava boss-a-cada-3).

## 2. A solução

Recuperei os 3 arquivos da API direto do commit que os tinha:
```
git checkout 7fb53bc -- api/schemas.py api/session.py api/main.py
```
e **adaptei ao game logic atual** (Lotes A/B/C):

| Adaptação | Onde | Porquê |
|---|---|---|
| `nivel` no `JogadorStatus` | `schemas.py` + `_jogador_status` | o `7fb53bc` é pré-Lote A; o `client.ts` exige `nivel` |
| `_rolar_loot` usa `tabela_loot()` | `main.py` | loot por tipo do Lote C chega ao jogo web |
| save/load preservam `nivel` | `save_game` / `load_game` | evita o nível voltar a 1 e causar **level-up duplicado** no próximo XP |

### Endpoints recuperados/corrigidos
- `POST /game/{id}/inventory/use` — **usar item do inventário** (a feature perdida)
- `POST /game/{id}/shop/buy` — `loja.comprar()` → `sucesso: bool`, loja `ofertas` flat
- `POST /game/new` / `GET /status` — `modo` em vez de `game_mode`
- `GET /game/{id}/save` + `POST /game/load` — salvar/carregar run
- `session.create_session(modo)` passa `modo=` à Masmorra (corrige o modo infinito)

## 3. Testes de API (novos)

Como **não havia nenhum teste de API**, criei `api/test_api.py` com **FastAPI
TestClient** (13 testes):
- contrato do `JogadorStatus` (inclui `nivel`, `andar`, `inventario`)
- `modo` propagado à Masmorra (story/infinite)
- loja: `sucesso` bool + `ofertas` flat; compra sem moedas falha
- combate: ataque derrota inimigo e concede recompensa
- **inventário: usar item aplica efeito e remove** (a feature recuperada)
- **save/load: round-trip preserva o nível** sem level-up duplicado

```
cd api && ../randongeon/.venv/Scripts/python.exe -m pytest test_api.py -q
→ 13 passed
```

## 4. POO neste lote

Lote de **integração**, então o destaque não é um pilar novo, mas:
- **Encapsulamento / Abstração:** os endpoints conversam com o domínio apenas pela
  interface pública (`jogador.usar_item`, `loja.comprar`, `inimigo.tabela_loot`) —
  a API não conhece os detalhes internos.
- **Serialização:** o save converte o objeto `Jogador` em dict e o reconstrói no
  load (round-trip), sem vazar a implementação.

Nenhum conteúdo fora dos slides.

## 5. Resultado e arquivos

```
game logic:  pytest tests/ -q      → 552 passed, 5 skipped
API:         pytest api/test_api.py → 13 passed
```

```
M  api/schemas.py        (ofertas, sucesso, modo, UseItem/Save/Load, +nivel)
M  api/session.py        (modo, load_session, Masmorra(modo=))
M  api/main.py           (endpoints recuperados + nivel + tabela_loot + save/load nivel)
M  api/requirements.txt  (+httpx para o TestClient)
A  api/test_api.py       (13 testes de API)
A  docs/api-inventario-LoteD.md
```

> Próximo: **Lote E** (Bando de Goblins sequencial) e **Lote F** (score infinito),
> que agora têm a API sã como base. **Lote G** = validação ponta-a-ponta da campanha.

---
*Lote D — pendente de merge na `main`.*
