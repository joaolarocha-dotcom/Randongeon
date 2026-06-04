"""
sim_elites_tank.py — Diagnóstico/calibração de tankiness dos elites (lote balance).

Mede, por andar, o nº médio de GOLPES do herói para matar cada tipo de inimigo
(TTK = time-to-kill), refletindo a lógica real de Inimigo.gerar(andar) e a
armadura (absorcao_dano). Mostra a inversão atual: por não escalarem com o andar,
os ESPECIAIS (Golem/Nosferatu/Banshee) morrem mais rápido que um comum no fim.

NÃO modifica o jogo. Reflete o código vigente em inimigo.py — rode antes e
depois do ajuste para comparar.

Uso:
    cd randongeon ; ./.venv/Scripts/Activate.ps1
    python simulacoes/sim_elites_tank.py
"""

# --- bootstrap de path: acha o pacote 'jogo' (randongeon/, uma pasta acima). ---
# Ferramentas de calibracao Monte Carlo: NAO sao testes nem parte do jogo.
# Ver simulacoes/README.md.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import math
import random
from collections import defaultdict

from jogo.entidades.inimigo import Inimigo

# ATK típico do herói ao chegar em cada andar (curva de campanha; espelha PERFIS
# do sim_balance_v4, interpolado). É o "machado" que bate no inimigo.
HERO_ATK = {5: 8, 8: 12, 10: 14, 13: 17, 16: 19, 20: 22}


def ttk(inimigo, atk: int) -> int:
    """Golpes para derrubar: cada golpe causa max(1, atk - armadura)."""
    dano = max(1, atk - inimigo.absorcao_dano)
    return math.ceil(inimigo.hp / dano)


def medir(andar: int, n: int = 20000):
    atk = HERO_ATK[andar]
    ttks = defaultdict(list)
    hps  = defaultdict(list)
    for _ in range(n):
        e = Inimigo.gerar(andar)
        if e.tipo_especial in ("nosferatu", "golem", "banshee"):
            chave = e.tipo_especial
        elif e.tipo_especial == "horda":
            chave = "horda"
        elif e.dificuldade == 2:
            chave = "elite"
        else:
            chave = "comum"
        ttks[chave].append(ttk(e, atk))
        hps[chave].append(e.hp)
    return atk, ttks, hps


ORDEM = ["comum", "elite", "golem", "nosferatu", "banshee", "horda"]

if __name__ == "__main__":
    print("TTK = golpes medios do heroi para matar | HP medio | (armadura) — n=20000\n")
    for andar in (5, 8, 10, 13, 16, 20):
        random.seed(42)
        atk, ttks, hps = medir(andar)
        print(f"--- Andar {andar}  (heroi ATK={atk}) ---")
        for chave in ORDEM:
            if chave not in ttks:
                continue
            ttk_med = sum(ttks[chave]) / len(ttks[chave])
            hp_med  = sum(hps[chave]) / len(hps[chave])
            print(f"  {chave:10s} TTK={ttk_med:4.1f}  HP={hp_med:5.1f}")
        print()
