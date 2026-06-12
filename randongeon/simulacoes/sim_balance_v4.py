"""
sim_balance_v4.py — Calibração do balanceamento profundo (ANÁLISE, fora do jogo).

Acha a escala de inimigos comuns/elite POR ANDAR (+ economia de moedas) que torne
cada andar um desafio, mirando "desafio consistente" (campanha ~25-35%; comuns
mordendo ~5-12% do HP no fim). NÃO mexe em HP/nível nem na curva de boss.

Não modifica o jogo. Usa o Jogador real (com nível) e a Masmorra real (boss/loot).
Comuns/elite vêm de uma versão ESCALADA local (gerar_escalado).
"""

# --- bootstrap de path: acha o pacote 'jogo' (randongeon/, uma pasta acima). ---
# Ferramentas de calibracao Monte Carlo: NAO sao testes nem parte do jogo.
# Ver simulacoes/README.md.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
import statistics

from jogo.entidades.jogador import Jogador
from jogo.entidades.inimigo import (
    Inimigo, NOMES_DIFICULDADE_1, NOMES_DIFICULDADE_2,
    GolemDePedra, Nosferatu, Banshee, HordaDeGoblins,
)
from jogo.entidades.loja    import Loja
from jogo.sistemas.masmorra import Masmorra

CHANCE_MISS_JOGADOR = 0.10
ANDARES_BOSS = [5, 10, 15, 20]


class Cfg:
    def __init__(self, hp_k, atk_div, moedas_div, ativo=True):
        self.hp_k, self.atk_div, self.moedas_div, self.ativo = hp_k, atk_div, moedas_div, ativo


def _bonus(andar, cfg):
    if not cfg.ativo:
        return 0, 0, 0
    return round(andar * cfg.hp_k), andar // cfg.atk_div, andar // cfg.moedas_div


def gerar_escalado(andar: int, cfg: Cfg) -> Inimigo:
    """Espelha Inimigo.gerar() mas escala comuns/elite por andar."""
    if random.random() < 0.10:
        return HordaDeGoblins()
    b_hp, b_atk, b_moedas = _bonus(andar, cfg)
    if andar >= 5 and random.random() < 0.25:
        pool = [GolemDePedra]
        if andar >= 8:  pool.append(Nosferatu)
        if andar >= 10: pool.append(Banshee)
        if random.random() < 0.40:
            return random.choice(pool)()
        nome = random.choice(NOMES_DIFICULDADE_2)
        return Inimigo(nome, random.randint(8, 15) + round(b_hp * 1.4),
                       random.randint(3, 5) + b_atk + 1, 2,
                       random.randint(25, 50), random.randint(5, 10) + b_moedas)
    nome = random.choice(NOMES_DIFICULDADE_1)
    return Inimigo(nome, random.randint(3, 8) + b_hp, random.randint(1, 3) + b_atk, 1,
                   random.randint(10, 20), random.randint(0, 4) + b_moedas)


def combate(jog: Jogador, ini) -> bool:
    """Combate puro (sem XP/loot). Retorna True se o jogador venceu."""
    atordoado = False
    while jog.esta_vivo() and ini.esta_vivo():
        if not atordoado:
            if random.random() >= CHANCE_MISS_JOGADOR:
                ini.receber_dano(jog.atk)
        else:
            atordoado = False
        if ini.esta_vivo():
            if getattr(ini, "bonus_atk_por_turno", 0) > 0:
                ini.atk += ini.bonus_atk_por_turno
            if random.random() >= getattr(ini, "chance_miss", 0.0):
                dano = jog.receber_dano(ini.atk)
            else:
                dano = 0
            if getattr(ini, "cura_percentual", 0) > 0 and dano > 0:
                ini.curar(max(1, int(dano * ini.cura_percentual)))
            if getattr(ini, "chance_atordoar", 0) > 0 and random.random() < ini.chance_atordoar:
                atordoado = True
    return jog.esta_vivo()


def comprar_na_loja(jog):
    loja = Loja()
    comprou = True
    while comprou and loja.ofertas:
        comprou = False
        for i in sorted(range(len(loja.ofertas)), key=lambda i: -loja.ofertas[i]["item"].bonus_atk):
            if jog.moedas >= loja.ofertas[i]["preco"]:
                loja.comprar(i, jog); comprou = True; break


def simular_run(cfg) -> bool:
    jog = Jogador("Sim", hp=20, atk=5, esq=0.3)
    masmorra = Masmorra(jog, modo="story")
    for andar in range(1, 21):
        masmorra.andar = andar
        if andar in ANDARES_BOSS:
            boss = masmorra.gerar_boss()
            if not combate(jog, boss):
                return False
            jog.ganhar_xp(boss.xp); jog.ganhar_moedas(boss.moedas)
        else:
            tipo, conteudo, _ = masmorra.gerador.gerar_sala(andar)
            if tipo == "inimigo":
                ini = gerar_escalado(andar, cfg)
                if not combate(jog, ini):
                    return False
                jog.ganhar_xp(ini.xp); jog.ganhar_moedas(ini.moedas)
                loot = masmorra._rolar_loot(ini)
                if loot:
                    masmorra.aplicar_item(loot)
            elif tipo == "item":
                masmorra.aplicar_item(conteudo)
            elif tipo == "loja":
                comprar_na_loja(jog)
    return True


# ── Ameaça dos comuns: perfis típicos do herói por andar (curva de campanha) ──
PERFIS = {5: (8, 35), 10: (14, 69), 15: (18, 92), 20: (22, 112)}

def medir_ameaca_comum(cfg, n=3000):
    res = {}
    for andar, (atk, hp) in PERFIS.items():
        perdas = []
        for _ in range(n):
            ini = gerar_escalado(andar, cfg)
            while ini.dificuldade != 1:          # só comuns
                ini = gerar_escalado(andar, cfg)
            jog = Jogador("H", hp=hp, atk=atk)
            hp0 = jog.hp
            if combate(jog, ini):
                perdas.append(hp0 - jog.hp)
        res[andar] = statistics.mean(perdas) if perdas else 0
    return res


def rodar(nome, cfg, n=4000):
    vit = sum(simular_run(cfg) for _ in range(n))
    am = medir_ameaca_comum(cfg)
    print(f"\n{nome}")
    print(f"  vitoria campanha: {vit/n*100:5.1f}%")
    print("  HP perdido vs COMUM:  " +
          "  ".join(f"A{a}={am[a]:4.1f} ({am[a]/PERFIS[a][1]*100:4.1f}%)" for a in (5, 10, 15, 20)))


if __name__ == "__main__":
    configs = [
        ("BASELINE (sem escala)",        Cfg(0, 99, 99, ativo=False)),
        ("A   hp*2.0 atk//5 moedas//3",  Cfg(2.0, 5, 3)),
        ("A2  hp*2.0 atk//5 moedas//2",  Cfg(2.0, 5, 2)),   # +moedas
        ("A3  hp*2.0 atk//6 moedas//2",  Cfg(2.0, 6, 2)),   # +moedas, atk mais suave
        ("E   hp*1.8 atk//6 moedas//2",  Cfg(1.8, 6, 2)),
        ("F   hp*1.8 atk//5 moedas//2",  Cfg(1.8, 5, 2)),
    ]
    for nome, cfg in configs:
        random.seed(42)
        rodar(nome, cfg)
