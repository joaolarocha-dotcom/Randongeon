# Lote 1 — Dano crítico do jogador

## Objetivo

Dar ao jogador uma chance de acerto **crítico** (dano extra), tornando o combate
menos previsível. É o atributo que o **dom "Sortudo"** (Lote 3) vai turbinar.

## O que mudou

`Jogador` ganhou:
- `CHANCE_CRITICO_BASE = 0.10` e `MULTIPLICADOR_CRITICO = 1.5` (constantes
  tunáveis) e o atributo de instância `chance_critico` (começa na base).
- `rolar_dano() -> (dano, foi_critico)`: parte do `atk_efetivo()` (já com
  Fraqueza etc.) e, na sorte, aplica o multiplicador. **Encapsula a regra num só
  lugar**, usado pela API, pela CLI e pelo combate automático.

O combate passou a usar `rolar_dano()` no lugar de `atk_efetivo()` direto, e o
log avisa o crítico:
- API: *"💥 Acerto CRÍTICO! Você causou X de dano."* (e no contra-ataque da
  esquiva).
- CLI: imprime *"💥 Acerto CRÍTICO!"* antes do dano.

`chance_critico` entra no **save/load** (importante para o dom Sortudo
sobreviver ao salvar).

## Pilares de POO

- **Encapsulamento:** a regra do crítico vive em `Jogador.rolar_dano()`; os três
  laços de combate só consomem o resultado.
- **Reuso:** parte do `atk_efetivo()` (Lote B2), então Fraqueza e crítico se
  compõem naturalmente.

## Balanceamento

`0.10 / 1.5×` são valores **iniciais e tunáveis**. Serão calibrados na rodada de
**recalibração por simulação** (após o lote de evasão e o boss), junto com a
presença de elites e os debuffs — crítico encurta lutas, evasão alonga; o
equilíbrio é medido com dados.

## Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `randongeon/jogo/entidades/jogador.py` | `chance_critico`, constantes, `rolar_dano()`. |
| `randongeon/jogo/sistemas/masmorra.py` | combate automático e CLI usam `rolar_dano()`. |
| `api/main.py` | ataque/contra-ataque usam `rolar_dano()`; save/load do `chance_critico`. |
| `randongeon/tests/test_jogador.py` | **+4** testes (`TestCritico`). |
| `api/test_api.py` | **+1** teste (round-trip do `chance_critico`). |

## Estado de testes

```
randongeon/tests/ → 608 passed, 5 skipped   (604 + 4)
api/test_api.py   → 27 passed                (26 + 1)
```
