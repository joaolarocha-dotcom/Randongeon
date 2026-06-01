"""
sim_status.py — Validação do tuning dos status especiais (ANÁLISE, fora do jogo).

Mede o quão AMEAÇADOR cada inimigo especial é, no nível em que ele costuma
aparecer (perfis de herói tirados da validação de campanha do Lote A). Compara
os valores atuais com os propostos para o Lote C, para decidirmos os números
com dados.

Métrica principal: HP médio perdido pelo herói no encontro (a win-rate nesses
níveis é ~100%, então o "custo em HP" é o que mede a ameaça real).

NÃO modifica o jogo. Usa um laço de combate que espelha resolver_combate()
SEM aplicar XP/loot ao final (para o ganho de nível não curar o herói e
distorcer a medição de HP perdido).
"""

import random
import statistics

from jogo.entidades.jogador import Jogador
from jogo.entidades.inimigo import GolemDePedra, Nosferatu, Banshee, HordaDeGoblins

CHANCE_MISS_JOGADOR = 0.10


def combate(jog: Jogador, ini) -> str:
    """Espelha o combate de resolver_combate(), mas sem XP/loot no fim."""
    atordoado = False
    while jog.esta_vivo() and ini.esta_vivo():
        if not atordoado:
            if random.random() >= CHANCE_MISS_JOGADOR:
                ini.receber_dano(jog.atk)          # absorcao_dano aplicada aqui
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

    return "vitoria" if jog.esta_vivo() else "derrota"


def medir(nome, jog_atk, jog_hp, fabrica, override=None, n=4000):
    vit = 0
    hp_perdido = []
    for _ in range(n):
        jog = Jogador("Heroi", hp=jog_hp, atk=jog_atk)
        ini = fabrica()
        if override:
            override(ini)
        hp0 = jog.hp
        if combate(jog, ini) == "vitoria":
            vit += 1
            hp_perdido.append(hp0 - jog.hp)
    wr  = vit / n * 100
    hpl = statistics.mean(hp_perdido) if hp_perdido else 0
    print(f"  {nome:<34} win {wr:5.1f}%  |  HP perdido medio {hpl:5.1f}  "
          f"({hpl/jog_hp*100:4.1f}% do HP)")


if __name__ == "__main__":
    N = 4000

    # Perfis de heroi (medias da validacao de campanha do Lote A)
    #   Golem aparece andar>=8  -> ~level 4-5
    #   Nosferatu andar>=15     -> ~level 7
    #   Banshee andar>=17       -> ~level 7-8
    P_GOLEM     = dict(jog_atk=13, jog_hp=60)
    P_NOSFERATU = dict(jog_atk=18, jog_hp=90)
    P_BANSHEE   = dict(jog_atk=20, jog_hp=100)

    print("=" * 70)
    print(f"VALIDACAO DE TUNING DOS STATUS ESPECIAIS (N={N} por encontro)")
    print("=" * 70)

    print("\nGOLEM (perfil heroi andar ~8-12: atk 13, hp 60)")
    random.seed(1); medir("Golem absorcao=2 (atual)", fabrica=GolemDePedra, **P_GOLEM)
    random.seed(1); medir("Golem absorcao=3 (proposto)", fabrica=GolemDePedra,
                          override=lambda g: setattr(g, "absorcao_dano", 3), **P_GOLEM)
    random.seed(1); medir("Golem absorcao=0 (referencia)", fabrica=GolemDePedra,
                          override=lambda g: setattr(g, "absorcao_dano", 0), **P_GOLEM)

    print("\nNOSFERATU (perfil heroi andar ~15: atk 18, hp 90)")
    random.seed(2); medir("Nosferatu cura=0.20 (atual)", fabrica=Nosferatu, **P_NOSFERATU)
    random.seed(2); medir("Nosferatu cura=0.40 (mais forte)", fabrica=Nosferatu,
                          override=lambda v: setattr(v, "cura_percentual", 0.40), **P_NOSFERATU)
    random.seed(2); medir("Nosferatu cura=0.0 (referencia)", fabrica=Nosferatu,
                          override=lambda v: setattr(v, "cura_percentual", 0.0), **P_NOSFERATU)

    print("\nBANSHEE (perfil heroi andar ~17: atk 20, hp 100)")
    random.seed(3); medir("Banshee atordoar=0.30 (atual)", fabrica=Banshee, **P_BANSHEE)
    random.seed(3); medir("Banshee atordoar=0.0 (referencia)", fabrica=Banshee,
                          override=lambda b: setattr(b, "chance_atordoar", 0.0), **P_BANSHEE)

    print("\nHORDA / BANDO DE GOBLINS (perfil heroi andar ~3: atk 6, hp 26)")
    random.seed(4); medir("Horda (atual, stat-based)", fabrica=HordaDeGoblins, jog_atk=6, jog_hp=26)

    # ── E se os especiais aparecessem CEDO (heroi fraco)? Testa o potencial ──
    print("\n" + "=" * 70)
    print("HIPOTESE: especiais contra heroi FRACO (atk 7, hp 35 ~ nivel de andar 5)")
    print("=" * 70)
    FRACO = dict(jog_atk=7, jog_hp=35)
    print("\nGolem (defesa importaria?):")
    random.seed(5); medir("Golem absorcao=2", fabrica=GolemDePedra, **FRACO)
    random.seed(5); medir("Golem absorcao=3", fabrica=GolemDePedra,
                          override=lambda g: setattr(g, "absorcao_dano", 3), **FRACO)
    random.seed(5); medir("Golem absorcao=0", fabrica=GolemDePedra,
                          override=lambda g: setattr(g, "absorcao_dano", 0), **FRACO)
    print("\nNosferatu (cura importaria?):")
    random.seed(6); medir("Nosferatu cura=0.20", fabrica=Nosferatu, **FRACO)
    random.seed(6); medir("Nosferatu cura=0.40", fabrica=Nosferatu,
                          override=lambda v: setattr(v, "cura_percentual", 0.40), **FRACO)
    random.seed(6); medir("Nosferatu cura=0.0", fabrica=Nosferatu,
                          override=lambda v: setattr(v, "cura_percentual", 0.0), **FRACO)
    print("\nBanshee (atordoar importaria?):")
    random.seed(7); medir("Banshee atordoar=0.30", fabrica=Banshee, **FRACO)
    random.seed(7); medir("Banshee atordoar=0.0", fabrica=Banshee,
                          override=lambda b: setattr(b, "chance_atordoar", 0.0), **FRACO)
