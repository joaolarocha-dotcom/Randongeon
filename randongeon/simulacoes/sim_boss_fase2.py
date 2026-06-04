"""
sim_boss_fase2.py — Calibração da FÚRIA do Coração da Masmorra (Lote 4).

Mede como a 2ª fase do boss final (renasce 1x a 50% do HP + ATK em fúria) muda a
taxa de vitória da campanha. NÃO modifica o jogo: roda campanhas story completas
com a config real de escala (config "F" do sim_balance_v4) e, no andar 20, troca
o boss final por uma luta de 2 fases parametrizada pelo multiplicador de fúria.

A cura de renascimento (50%) está TRAVADA no roadmap; aqui varia-se só a fúria.
Roda com seed fixa por configuração para comparabilidade.

Uso:
    cd randongeon ; ./.venv/Scripts/Activate.ps1
    python simulacoes/sim_boss_fase2.py
"""

# --- bootstrap de path: acha o pacote 'jogo' (randongeon/, uma pasta acima). ---
# Ferramentas de calibracao Monte Carlo: NAO sao testes nem parte do jogo.
# Ver simulacoes/README.md.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random

from jogo.entidades.jogador import Jogador
from jogo.entidades.inimigo import Inimigo
from jogo.sistemas.masmorra import Masmorra
from sim_balance_v4 import gerar_escalado, combate, comprar_na_loja, Cfg

CHANCE_MISS_JOGADOR = 0.10
CFG_LIVE          = Cfg(1.8, 5, 2)     # config "F" — números reais de inimigo.py
ANDARES_BOSS_INTER = (5, 10, 15)       # bosses intermediários (Inimigo comum)
CURA_RENASCIMENTO = 0.50               # travado

# Stats do Coração no andar 20 (= 20 + 4*20 de HP, 5 + 4*3 de ATK) — travadas por teste.
CORACAO_HP, CORACAO_ATK, CORACAO_XP, CORACAO_MOEDAS = 100, 17, 240, 57


def luta_coracao(jog: Jogador, fury_mult: float, revive: bool = True) -> bool:
    """
    Luta contra o Coração com 2 fases (espelha a implementação real, mas com a
    fúria parametrizada). revive=False reproduz o boss ANTIGO de 1 fase (baseline).
    Retorna True se o jogador venceu.
    """
    boss = Inimigo("Coração da Masmorra", hp=CORACAO_HP, atk=CORACAO_ATK,
                   dificuldade=3, xp=CORACAO_XP, moedas=CORACAO_MOEDAS)
    ja_renasceu = False
    while jog.esta_vivo():
        while jog.esta_vivo() and boss.esta_vivo():
            if random.random() >= CHANCE_MISS_JOGADOR:       # turno do jogador (com crítico)
                dano, _ = jog.rolar_dano()
                boss.receber_dano(dano)
            if boss.esta_vivo() and random.random() >= boss.chance_miss:
                jog.receber_dano(boss.atk)                   # turno do boss
        if not jog.esta_vivo():
            return False
        if revive and not ja_renasceu:                       # 1ª morte → renasce
            ja_renasceu = True
            boss.curar(round(boss.hp_max * CURA_RENASCIMENTO))
            boss.atk = max(boss.atk + 1, round(boss.atk * fury_mult))
            continue
        return True                                          # boss morto de vez


def simular_campanha(fury_mult: float, revive: bool, cfg: Cfg = CFG_LIVE) -> str:
    """Roda uma campanha story completa. Retorna 'win' | 'lose_boss' | 'lose_early'."""
    jog = Jogador("Sim", hp=20, atk=5, esq=0.3)
    masmorra = Masmorra(jog, modo="story")
    for andar in range(1, 21):
        masmorra.andar = andar
        if andar == 20:
            return "win" if luta_coracao(jog, fury_mult, revive) else "lose_boss"
        if andar in ANDARES_BOSS_INTER:
            boss = masmorra.gerar_boss()
            if not combate(jog, boss):
                return "lose_early"
            jog.ganhar_xp(boss.xp); jog.ganhar_moedas(boss.moedas)
        else:
            tipo, conteudo, _ = masmorra.gerador.gerar_sala(andar)
            if tipo == "inimigo":
                ini = gerar_escalado(andar, cfg)
                if not combate(jog, ini):
                    return "lose_early"
                jog.ganhar_xp(ini.xp); jog.ganhar_moedas(ini.moedas)
                loot = masmorra._rolar_loot(ini)
                if loot:
                    masmorra.aplicar_item(loot)
            elif tipo == "item":
                masmorra.aplicar_item(conteudo)
            elif tipo == "loja":
                comprar_na_loja(jog)
    return "win"


def rodar(nome: str, fury_mult: float, revive: bool = True, n: int = 6000) -> None:
    random.seed(42)
    res = {"win": 0, "lose_boss": 0, "lose_early": 0}
    for _ in range(n):
        res[simular_campanha(fury_mult, revive)] += 1
    chegou = res["win"] + res["lose_boss"]                  # campanhas que chegaram no andar 20
    atk_furia = max(CORACAO_ATK + 1, round(CORACAO_ATK * fury_mult)) if revive else CORACAO_ATK
    wr_boss = res["win"] / chegou * 100 if chegou else 0.0
    print(f"{nome:32s}  ATK 2ªfase={atk_furia:>2}  | "
          f"vitória campanha={res['win']/n*100:5.1f}%  | "
          f"win-rate só do boss={wr_boss:5.1f}%  "
          f"(chegou ao boss={chegou/n*100:4.1f}%)")


if __name__ == "__main__":
    print(f"Monte Carlo - Coracao da Masmorra 2a fase | cura renascimento={int(CURA_RENASCIMENTO*100)}% | n=6000\n")
    rodar("BASELINE 1 fase (boss atual)", 1.0, revive=False)
    print("  -- com 2a fase (renasce 1x), variando a furia --")
    for mult in (1.0, 1.25, 1.5, 1.75, 2.0):
        rodar(f"2 fases  fúria x{mult:.2f}", mult, revive=True)
