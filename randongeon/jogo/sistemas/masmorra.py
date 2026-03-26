import random
import time
from jogo.sistemas.gerador import GeradorSala


class Masmorra:
    def __init__(self, jogador):
        self.jogador = jogador
        self.desistiu = False
        self.andar = 0
        self.gerador = GeradorSala() 

        self.lore = [
            "Ninguém sabe quando ela surgiu,",
            "do nada no mundo, um abismo se abriu.",
            "",
            "Uns dizem: foi obra de antiga ambição,",
            "outros: sempre existiu, além da razão.",
            "",
            "Chamam-na de Masmorra Sem Fim,",
            "onde poucos voltaram para contar o que viram ali.",
            "",
            "A entrada rasgou o chão sem aviso,",
            "um convite sombrio, um estranho paraíso.",
            "",
            "Muitos entraram buscando poder,",
            "mas poucos viveram pra sobreviver.",
            "",
            "Os que voltaram não falam de ouro,",
            "mas de horrores guardados no escuro tesouro.",
            "",
            "Corredores mudam, sem explicação,",
            "criaturas surgem da própria escuridão.",
            "",
            "Sussurros te chamam, parecem te conhecer,",
            "como se a masmorra pudesse te ver.",
            "",
            "Mas algo te trouxe, não foi por acaso,",
            "talvez redenção… ou poder em atraso.",
            "",
            "Ao cruzar a entrada, você sente o olhar,",
            "algo lá dentro começou a te notar.",
            "",
            "E no fundo eterno, além da razão…",
            "algo te espera na escuridão."
        ]
        
    def mostrar_lore(self):
        for linha in self.lore:
            print(linha)
            time.sleep(0.75)
        print("\n" * 2)

    def mostrar_status(self):
        print("--- STATUS ---\n")
        print(f"Nome: {self.jogador.nome}")
        print(f"HP: {self.jogador.hp}")
        print(f"ATK: {self.jogador.atk}")
        print(f"XP: {self.jogador.xp}")
        print(f"Andar: {self.andar}\n")

    def avancar(self):
        self.andar += 1
        print(f"Você avançou para o andar {self.andar}...\n")

        time.sleep(0.25)

      
        tipo, conteudo = self.gerador.gerar_sala()

        if tipo == "item":
            conteudo.usar(self.jogador)

        elif tipo == "inimigo":
            inimigo = conteudo

            print(f"Um {inimigo.nome} apareceu!\n")
            time.sleep(0.25)

            while self.jogador.hp > 0 and inimigo.hp > 0:
                print("--- COMBATE ---\n")
                print("1 - Atacar")
                print("2 - Fugir\n")

                acao = input("> ")
                print()

                if acao == "1":
                    inimigo.hp -= self.jogador.atk
                    print(f"Você causou {self.jogador.atk} de dano.\n")
                    time.sleep(0.25)

                    if inimigo.hp > 0:
                        self.jogador.hp -= inimigo.atk
                        print(f"O inimigo atacou! Você perdeu {inimigo.atk} de HP.\n")
                        time.sleep(0.25)

                elif acao == "2":
                    print("Você fugiu...\n")
                    time.sleep(0.25)
                    break

            if inimigo.hp <= 0:
                print(f"Você derrotou {inimigo.nome}!\n")
                time.sleep(0.25)

                self.jogador.xp += inimigo.xp
                print(f"Você ganhou {inimigo.xp} XP!\n")
                time.sleep(0.25)

    def menu(self):
        print("\n--- O QUE DESEJA FAZER? ---\n")
        time.sleep(0.25)
        print("1 - Avançar")
        print("2 - Ver status")
        print("3 - Desistir\n")

        return input("> ")
        

    def jogar(self):
        while self.jogador.hp > 0 and not self.desistiu:
            escolha = self.menu()
            print("\n")

            if escolha == "3":
                time.sleep(0.25)
                print(f"{self.jogador.nome} desistiu da jornada...\n")
                print(f"XP obtido: {self.jogador.xp}\n")
                self.desistiu = True

            elif escolha == "2":
                time.sleep(0.25)
                self.mostrar_status()

            elif escolha == "1":
                time.sleep(0.25)
                self.avancar()

            else:
                print("Opção inválida!\n")

        if self.jogador.hp <= 0:
            print(f"{self.jogador.nome} foi consumido pela masmorra...\n")
            print(f"XP total obtido: {self.jogador.xp}\n")