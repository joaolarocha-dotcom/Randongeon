from jogo.jogador import Jogador

class Jogo:
    def __init__(self, gerador):
        self.jogador = Jogador()
        self.gerador = gerador
        self.sala_atual = 0

    def jogar_turno(self):
        self.sala_atual += 1
        print(f"\n--- Sala {self.sala_atual} ---")

        print(self.gerador.gerar_sala())
        inimigo = self.gerador.gerar_inimigo()

        print(f"Um {inimigo.nome} apareceu! (Vida: {inimigo.vida})")

        while inimigo.vida > 0 and self.jogador.vida > 0:
            acao = input("[A]tacar ou [F]ugir: ").lower()

            if acao == 'a':
                dano = self.jogador.atacar(inimigo)
                print(f"Você causou {dano} de dano.")

                if inimigo.vida > 0:
                    dano = inimigo.atacar(self.jogador)
                    print(f"O {inimigo.nome} causou {dano} de dano.")

            elif acao == 'f':
                print("Você fugiu!")
                return True

        if self.jogador.vida <= 0:
            print("Você morreu! Fim de jogo.")
            return False

        print(f"Você derrotou o {inimigo.nome}!")
        return True