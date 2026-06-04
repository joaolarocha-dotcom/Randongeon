# Lote 6 — Tutorial atualizado

## Objetivo

O tutorial (`TutorialsScreen` + `data/tutorials.ts`) tinha só 4 páginas e estava
**desatualizado/incorreto** frente a tudo que o jogo ganhou (crítico, doms,
efeitos de status, elites/especiais, boss de 2 fases, level-up, save .txt,
placar). Este lote reescreve o conteúdo para refletir o estado final do jogo,
com **precisão** (cada mecânica conferida no código).

## Correções de informação (estava errado)

- **Esquivar:** dizia "falha causa dano dobrado". O real (combat/dodge): se
  esquivar, evita o golpe e **contra-ataca**; se falhar, sofre o ataque **normal**
  (não dobrado).
- **Cura:** dizia "vencer um boss restaura 40% do HP". Não existe cura ao vencer
  boss — a cura é no **level-up** (60% do HP máx, `CURA_NIVEL_FRACAO=0.60`), que
  também purga veneno.
- **Itens iniciais:** dizia "Erva Medicinal (HP+3) / Poção de Força (ATK+1)". O
  real (`_itens_iniciais`): **Poção de Cura Pequena (HP+4)** e **Punhal Gasto
  (ATK+1)**.

## Conteúdo novo (9 páginas)

1. Bem-vindo (salas, modos story/infinito).
2. Herói e DOM (stats iniciais + os 5 doms e trade-offs).
3. Combate (LUTAR com miss ~10% e **crítico** ~10%/1,5×; ESQUIVAR correto; ITEM;
   FUGIR; evasão do inimigo).
4. Subir de nível (XP, ganhos por nível, **cura 60%**, purga veneno, barra de XP).
5. Status/badges (☠️ veneno, 💪 fraqueza, 💫 zonzo, ⭐ dom).
6. Inimigos especiais (armadura Golem, lifesteal Nosferatu, atordoar+evasão
   Banshee, fraqueza+evasão Orc, tanque+maça Troll, veneno Goblin/Rato, Bando).
7. Bosses (cadência story/infinito + **2ª fase do Coração da Masmorra**).
8. Itens, loja e baús (chances 15/15/70; mímico).
9. Salvar (.txt) e placar.

## Implementação

Só **dados** (`data/tutorials.ts`) — a `TutorialsScreen` já renderiza
genericamente qualquer número de páginas/parágrafos (paginação + scroll), então
nenhuma mudança de componente foi necessária. Sem backend.

## Verificação

- `npx tsc --noEmit` → **0 erros** (estrutura `TutorialPage[]` validada).

## Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `frontend/src/data/tutorials.ts` | reescrita completa: 4 → 9 páginas, conteúdo atual e correções. |

## Estado de testes

```
randongeon/tests/ → 656 passed (inalterado — lote só de conteúdo)
api/test_api.py   → 35 passed (inalterado)
frontend          → tsc --noEmit: 0 erros
```
