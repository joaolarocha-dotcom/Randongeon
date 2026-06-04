"""
sim_recalibracao.py — Diagnóstico Monte Carlo da campanha story INTEIRA.

Roda campanhas completas (andares 1..20) com as ENTIDADES REAIS e a ordem de
turno da API (crítico, esquiva do inimigo, lifesteal, veneno/fraqueza/esquiva-
debuff, bando sequencial, escala de elites do Lote B, boss de 2 fases do Lote 4,
cura ao subir de nível). Mede a taxa de vitória e ONDE as runs morrem.

Estratégia do herói (aproximação de jogador competente):
  - ataca sempre (sem fugir);
  - itens de ATK/ESQ são aplicados na hora; poções de cura ficam no inventário e
    são usadas quando o HP cai abaixo de CURA_GATE do HP máx;
  - na loja, compra os itens de maior ATK que couberem no bolso.

NÃO modifica o jogo. Reflete o código vigente — rode antes e depois de ajustes.

Uso:
    cd randongeon ; ./.venv/Scripts/Activate.ps1
    python sim_recalibracao.py
"""

import random
from collections import Counter

from jogo.entidades.jogador import Jogador
from jogo.entidades.inimigo import Inimigo, BandoDeGoblins
from jogo.entidades.efeitos import Fraqueza, EsquivaReduzida
from jogo.sistemas.masmorra import Masmorra, CHANCE_MISS_JOGADOR
from jogo.entidades.loja import Loja

ANDARES_BOSS = (5, 10, 15, 20)
CURA_GATE = 0.40   # usa poção quando HP < 40% do máx


def classificar(inimigo) -> str:
    esp = getattr(inimigo, "tipo_especial", None)
    if esp in ("golem", "nosferatu", "banshee", "horda"):
        return esp
    if inimigo.dificuldade == 3:
        return "boss"
    if inimigo.dificuldade == 2:
        return "elite"
    return "comum"


def _rolar_loot(inimigo):
    chance = 0.50 if inimigo.dificuldade == 3 else getattr(inimigo, "chance_drop", 0.08)
    if random.random() < chance:
        return random.choice(inimigo.tabela_loot())
    return None


def _guardar_ou_aplicar(jog, inventario, item):
    """Poção de cura pura → inventário; bônus permanente (atk/esq) → aplica já."""
    if item is None:
        return
    if item.bonus_hp > 0 and item.bonus_atk == 0 and item.bonus_esq == 0:
        inventario.append(item)
    else:
        item.usar(jog)


def _curar_se_preciso(jog, inventario):
    if jog.hp >= CURA_GATE * jog.hp_max or not inventario:
        return
    curas = [it for it in inventario if it.bonus_hp > 0]
    if not curas:
        return
    melhor = max(curas, key=lambda it: it.bonus_hp)
    melhor.usar(jog)
    inventario.remove(melhor)


def combate(jog, inimigo, inventario) -> bool:
    """Espelha combat_attack + _processar_ataque_inimigo. True se o herói venceu."""
    atordoado = False
    while jog.esta_vivo():
        _curar_se_preciso(jog, inventario)
        # Turno do jogador (com crítico via rolar_dano). Miss 10%; inimigo pode esquivar.
        if atordoado:
            atordoado = False
        elif random.random() >= CHANCE_MISS_JOGADOR and not inimigo.tentar_esquivar():
            dano, _ = jog.rolar_dano()
            efetivo = inimigo.receber_dano(dano)
            jog.aplicar_lifesteal(efetivo)

        if not inimigo.esta_vivo():
            if inimigo.tentar_renascer():    # boss de 2 fases (Coração)
                continue
            return True

        # Turno do inimigo: veneno de turnos anteriores age primeiro, depois atacar().
        jog.processar_efeitos_turno()
        if not jog.esta_vivo():
            return False
        rel = inimigo.atacar(jog)
        if rel["atordoou"]:
            atordoado = True
        if rel["envenenou"]:
            jog.envenenar()
        if rel.get("fraqueza"):
            jog.aplicar_efeito(Fraqueza(2))
        if rel.get("esquiva_reduzida"):
            jog.aplicar_efeito(EsquivaReduzida(1))
    return False


def _comprar_na_loja(jog):
    loja = Loja()
    comprou = True
    while comprou:
        comprou = False
        ordem = sorted(range(len(loja.ofertas)), key=lambda i: -loja.ofertas[i]["item"].bonus_atk)
        for i in ordem:
            if jog.moedas >= loja.ofertas[i]["preco"]:
                loja.comprar(i, jog)
                comprou = True
                break


def simular_campanha():
    """Retorna (resultado, andar, killer): ('vitoria',20,None) ou ('morte',andar,tipo)."""
    jog = Jogador("Sim", hp=20, atk=5, esq=0.3)
    masmorra = Masmorra(jog, modo="story")
    inventario = []

    for andar in range(1, 21):
        masmorra.andar = andar
        if andar in ANDARES_BOSS:
            boss = masmorra.gerar_boss()
            if not combate(jog, boss, inventario):
                return "morte", andar, classificar(boss)
            jog.ganhar_xp(boss.xp); jog.ganhar_moedas(boss.moedas)
            continue

        tipo, conteudo, _ = masmorra.gerador.gerar_sala(andar)
        if tipo == "inimigo":
            if getattr(conteudo, "tipo_especial", None) == "horda":
                for g in BandoDeGoblins().fila():       # bando sequencial
                    if not combate(jog, g, inventario):
                        return "morte", andar, "horda"
                    jog.ganhar_xp(g.xp); jog.ganhar_moedas(g.moedas)
                    _guardar_ou_aplicar(jog, inventario, _rolar_loot(g))
            else:
                if not combate(jog, conteudo, inventario):
                    return "morte", andar, classificar(conteudo)
                jog.ganhar_xp(conteudo.xp); jog.ganhar_moedas(conteudo.moedas)
                _guardar_ou_aplicar(jog, inventario, _rolar_loot(conteudo))
        elif tipo == "item":
            _guardar_ou_aplicar(jog, inventario, conteudo)
        elif tipo == "loja":
            _comprar_na_loja(jog)

    return "vitoria", 20, None


def rodar(n=5000):
    random.seed(42)
    vitorias = 0
    mortes_por_andar = Counter()
    mortes_por_tipo = Counter()
    alcancou = Counter()           # quantas runs CHEGARAM vivas a cada boss
    venceu_boss = Counter()        # quantas BATERAM cada boss

    for _ in range(n):
        # rastreio de boss exige reproduzir a run; em vez disso, contamos no fim.
        res, andar, killer = simular_campanha()
        if res == "vitoria":
            vitorias += 1
        else:
            mortes_por_andar[andar] += 1
            mortes_por_tipo[killer] += 1

    # Reconstrói as taxas de "chegou/venceu boss" a partir de onde morreram.
    # Chegou ao boss do andar B = não morreu ANTES de B.
    for B in ANDARES_BOSS:
        morreu_antes = sum(c for a, c in mortes_por_andar.items() if a < B)
        alcancou[B] = n - morreu_antes
        morreu_no_boss = mortes_por_andar.get(B, 0)
        venceu_boss[B] = alcancou[B] - morreu_no_boss  # os que passaram do andar B

    print(f"=== Recalibração — campanha story | n={n} | seed 42 ===")
    print(f"VITÓRIA DE CAMPANHA: {vitorias/n*100:5.1f}%\n")

    print("Chegou vivo ao boss / venceu o boss (condicional a chegar):")
    for B in ANDARES_BOSS:
        ch = alcancou[B] / n * 100
        wr = (venceu_boss[B] / alcancou[B] * 100) if alcancou[B] else 0.0
        print(f"  Andar {B:2d}: chegou={ch:5.1f}%   win-rate do boss={wr:5.1f}%")

    print("\nMortes por andar (top):")
    for a, c in sorted(mortes_por_andar.items()):
        print(f"  A{a:2d}: {c/n*100:4.1f}%")

    print("\nQuem mais mata (tipo de inimigo):")
    for tipo, c in mortes_por_tipo.most_common():
        print(f"  {tipo:10s}: {c/n*100:4.1f}%")


if __name__ == "__main__":
    rodar()
