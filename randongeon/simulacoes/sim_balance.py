"""
sim_balance.py — Validação Monte Carlo do balanceamento (ANÁLISE, fora do jogo).

Diferente da versão de calibração, este script roda 100% sobre o CÓDIGO REAL já
implementado (Jogador com sistema de nível + Masmorra.gerar_boss progressivo).
Serve para confirmar que a config aprovada ("config I") entrega as taxas de
vitória previstas. NÃO modifica nenhum arquivo do jogo.

Política de combate: Masmorra.resolver_combate() (combate automático real, só
ataque, miss de 10%). Estimativa PESSIMISTA — o jogador web ainda tem a ação
Esquivar, que só melhora os números.
"""

# --- bootstrap de path: acha o pacote 'jogo' (randongeon/, uma pasta acima). ---
# Ferramentas de calibracao Monte Carlo: NAO sao testes nem parte do jogo.
# Ver simulacoes/README.md.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
import statistics

from jogo.entidades.jogador  import Jogador
from jogo.entidades.loja     import Loja
from jogo.sistemas.masmorra  import Masmorra

ANDAR_MAX    = 20
ANDARES_BOSS = [5, 10, 15, 20]


def comprar_na_loja(jog: Jogador) -> None:
    """Política simples: compra gulosa priorizando ATK, depois o que couber."""
    loja = Loja()
    comprou = True
    while comprou and loja.ofertas:
        comprou = False
        ordem = sorted(range(len(loja.ofertas)),
                       key=lambda i: -loja.ofertas[i]["item"].bonus_atk)
        for i in ordem:
            if jog.moedas >= loja.ofertas[i]["preco"]:
                loja.comprar(i, jog)
                comprou = True
                break


def simular_run(registro: dict) -> str:
    jog = Jogador("Sim", hp=20, atk=5, esq=0.3)   # nível vem do código real
    masmorra = Masmorra(jog, modo="story")

    for andar in range(1, ANDAR_MAX + 1):
        masmorra.andar = andar

        if andar in ANDARES_BOSS:
            r = registro[andar]
            r["chegou"] += 1
            r["nivel"].append(jog.nivel)
            r["atk"].append(jog.atk)
            r["hp_max"].append(jog.hp_max)
            if masmorra.resolver_combate(masmorra.gerar_boss()) == "derrota":
                return f"morte_andar_{andar}"
            r["venceu"] += 1
        else:
            tipo, conteudo, _ = masmorra.gerador.gerar_sala(andar)
            if tipo == "inimigo":
                inimigo = masmorra.gerar_mimico() if random.random() < 0.05 else conteudo
                if masmorra.resolver_combate(inimigo) == "derrota":
                    return f"morte_andar_{andar}"
            elif tipo == "item":
                masmorra.aplicar_item(conteudo)
            elif tipo == "loja":
                comprar_na_loja(jog)

    return "vitoria"


def validar(n: int) -> None:
    registro = {a: {"chegou": 0, "venceu": 0, "nivel": [], "atk": [], "hp_max": []}
                for a in ANDARES_BOSS}
    vitorias = 0
    for _ in range(n):
        if simular_run(registro) == "vitoria":
            vitorias += 1

    print("=" * 70)
    print(f"VALIDAÇÃO DO CÓDIGO REAL — config I (N={n} runs, modo story)")
    print("  nível: +2 ATK / +12 HP por nível, custo 10*N*(N+1) | boss: 20+f*20, 5+f*3")
    print("=" * 70)
    print(f"  >> Vitória de campanha (bateu andar 20): {vitorias/n*100:5.1f}%")
    print(f"  {'Boss':>5} | {'chegou':>7} | {'win@boss':>9} | {'nível':>6} | {'ATK':>5} | {'HPmax':>6}")
    print("  " + "-" * 56)
    for a in ANDARES_BOSS:
        r = registro[a]
        chegou = r["chegou"]
        wr  = (r["venceu"] / chegou * 100) if chegou else 0.0
        lvl = statistics.mean(r["nivel"])  if r["nivel"]  else 0
        atk = statistics.mean(r["atk"])    if r["atk"]    else 0
        hp  = statistics.mean(r["hp_max"]) if r["hp_max"] else 0
        print(f"  {('A'+str(a)):>5} | {chegou/n*100:6.1f}% | {wr:8.1f}% | {lvl:6.1f} | {atk:5.1f} | {hp:6.1f}")


if __name__ == "__main__":
    random.seed(42)
    validar(4000)
