from jogo.entidades import Jogador
from jogo.sistemas import Masmorra

historico = []

while True:
    dungeon = Masmorra(None)
    dungeon.mostrar_lore()

    nome = input("Qual o seu nome, aventureiro?\n\n> ")
    jogador = Jogador(nome)

    dungeon.jogador = jogador
    dungeon.jogar()

    # salva no histórico
    historico.append({
        "nome": jogador.nome,
        "xp": jogador.xp
    })

    # loop menu
    while True:
        print("\n--- FIM DA RUN ---\n")
        print("1 - Jogar novamente")
        print("2 - Ver aventureiros passados")
        print("3 - Sair\n")

        escolha = input("> ")
        print()

        if escolha == "1":
            break  # volta pro loop principal (nova run)

        elif escolha == "2":
            if not historico:
                print("Nenhum aventureiro ainda.\n")
            else:
                print("--- AVENTUREIROS ---\n")

                ranking = sorted(historico, key=lambda x: x["xp"], reverse=True)

                for i, p in enumerate(ranking, 1):
                    print(f"{i}. {p['nome']} - {p['xp']} XP")

                print()

            # volta pro menu

        elif escolha == "3":
            print("Encerrando jogo...")
            exit()

        else:
            print("Opção inválida!\n")