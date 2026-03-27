# randongeon/main.py

"""
Ponto de entrada do RPG de Masmorra.

Responsabilidades deste módulo:
  - Exibir a lore de introdução
  - Coletar o nome do jogador
  - Instanciar Jogador e Masmorra
  - Gerenciar o histórico de runs
  - Exibir o menu pós-run (jogar novamente, ranking, sair)

Este arquivo NÃO contém lógica de jogo — apenas orquestração de fluxo.
Toda lógica testável está em jogo/entidades/ e jogo/sistemas/.
"""

import sys
import os

# Garante que a raiz do projeto esteja no path ao executar diretamente
sys.path.insert(0, os.path.dirname(__file__))

from jogo.entidades.jogador import Jogador
from jogo.sistemas.masmorra import Masmorra
from jogo.sistemas.gerador  import GeradorSala


def exibir_ranking(historico: list) -> None:
    """
    Exibe o ranking de aventureiros ordenado por XP decrescente.

    Parâmetros:
        historico (list): Lista de dicts com chaves 'nome' e 'xp'.
    """
    if not historico:
        print("Nenhum aventureiro registrado ainda.\n")
        return

    print("--- RANKING DE AVENTUREIROS ---\n")
    ranking = sorted(historico, key=lambda x: x["xp"], reverse=True)

    for i, entrada in enumerate(ranking, start=1):
        print(f"  {i}. {entrada['nome']} — {entrada['xp']} XP")

    print()


def menu_pos_run() -> str:
    """
    Exibe o menu pós-run e retorna a escolha do jogador.

    Retorna:
        str: Opção escolhida pelo jogador ('1', '2' ou '3').
    """
    print("\n--- FIM DA RUN ---\n")
    print("1 - Jogar novamente")
    print("2 - Ver ranking de aventureiros")
    print("3 - Sair\n")
    return input("> ")


def iniciar_run(historico: list) -> None:
    """
    Executa uma run completa do jogo: lore → criação do personagem → loop.

    Ao final da run, salva nome e xp do jogador no histórico.

    Parâmetros:
        historico (list): Lista compartilhada de runs anteriores.
                          Modificada in-place ao final da run.
    """
    gerador  = GeradorSala()
    masmorra = Masmorra(jogador=None, gerador=gerador)

    # Introdução
    masmorra.mostrar_lore()

    # Coleta o nome
    nome    = input("Qual o seu nome, aventureiro?\n\n> ").strip()
    if not nome:
        nome = "Desconhecido"

    print("\n" * 2)

    # Cria o personagem e associa à masmorra
    jogador          = Jogador(nome=nome, hp=20, atk=5)
    masmorra.jogador = jogador

    # Loop principal da run
    masmorra.jogar()

    # Registra no histórico
    historico.append({
        "nome": jogador.nome,
        "xp":   jogador.xp,
    })


def main() -> None:
    """
    Loop principal do programa.

    Gerencia o ciclo de runs e o menu pós-jogo, mantendo o histórico
    de aventureiros em memória durante a sessão.
    """
    historico: list = []

    while True:
        # Inicia uma nova run
        iniciar_run(historico)

        # Menu pós-run
        while True:
            escolha = menu_pos_run()
            print()

            if escolha == "1":
                break  # volta ao loop principal para nova run

            elif escolha == "2":
                exibir_ranking(historico)

            elif escolha == "3":
                print("Encerrando o jogo. Até a próxima, aventureiro!\n")
                sys.exit(0)

            else:
                print("Opção inválida. Tente novamente.\n")


if __name__ == "__main__":
    main()