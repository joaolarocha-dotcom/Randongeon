# Lote L — Reescrita de textos & flavor (tom sombrio com humor)

## Objetivo

Tirar o tom "Pokémon antigo" que quebrava a imersão (ex.: *"Um Nosferatu selvagem
apareceu! / Vai, fulano!"*) e dar identidade própria às entradas de combate,
descrições de sala e entradas de boss. Tom definido: **sombrio com toques de
humor**.

## O que mudou

### 1. Introduções de combate (frontend) — o ponto principal
`frontend/src/store/gameStore.ts`
- Novo gerador `buildEnemyIntro(inimigo, jogador, tipo)`: monta as falas de
  abertura **por tipo de inimigo** e escolhe ao acaso entre várias opções, para
  a entrada não repetir.
- Cada tipo tem voz própria: **boss** (entrada pesada, sem fuga), **nosferatu**
  (sede de sangue), **golem** (rocha/armadura), **banshee** (lamento), **horda**
  (goblins cercando), e **comuns** com linhas atmosféricas variadas.
- Removidas as linhas `"Um X selvagem apareceu!"` e `"Vai, fulano!"`.
- Reveal do **Mímico** reescrito ("O baú tinha dentes — e fome.").

### 2. Descrições de sala (backend, compartilhado CLI + API)
`randongeon/jogo/sistemas/gerador.py`
- `DESCRICOES_SALA` passou de 5 frases genéricas para **12** descrições mais
  ricas e variadas, com atmosfera e humor negro.

### 3. Entradas de boss (API)
`api/main.py`
- Mensagens de aparição de boss reescritas (guardião intermediário e o
  re-spawn do Coração da Masmorra), mantendo os **nomes** dos bosses.

### 4. Exposição de `tipo_especial` no frontend
`frontend/src/api/client.ts`
- `InimigoInfo` passou a declarar `tipo_especial` (a API já enviava o campo;
  só não estava tipado no client). É o que permite as intros por tipo.

## Restrições respeitadas (travadas por teste)

- **Nomes de boss** (`Arauto das Sombras`, `Senhor dos Corredores`,
  `Ceifador Eterno`, `Coração da Masmorra`) — preservados.
- **Itens da loja** (`Elixir Vital`, `Grande Poção de Força`,
  `Elixir do Mestre Mosca`) e nomes de itens checados por testes — preservados.
- `DESCRICOES_SALA` foi reescrita à vontade porque os testes verificam
  **pertencimento** (`descricao in DESCRICOES_SALA`), não strings fixas.

## Itens (flavor) — fica para um lote futuro

Dar descrição/flavor próprio aos **itens** exige um campo novo `descricao` em
`Item` (+ `schemas`, tipos do frontend e UI de loja/baú). Como os **nomes** de
vários itens estão travados por teste e não há campo de descrição hoje, isto é
melhor entregue como um lote dedicado, sem inflar este. Sugestão: **Lote L-bis —
descrição de itens**.

## Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `frontend/src/store/gameStore.ts` | `buildEnemyIntro()` + uso na entrada de combate e no Mímico. |
| `frontend/src/api/client.ts` | `InimigoInfo.tipo_especial`. |
| `randongeon/jogo/sistemas/gerador.py` | `DESCRICOES_SALA` reescrita (12 entradas). |
| `api/main.py` | entradas de boss reescritas. |

## Estado de testes

```
frontend → npx tsc --noEmit: 0 erros
randongeon/tests/ → 572 passed, 5 skipped
api/test_api.py   → 24 passed
```
