from jogo.jogo import Jogo
from geradores.gerador_simples import GeradorSimples

# from geradores.gerador_ia import GeradorIA

if __name__ == "__main__":
    jogo = Jogo(GeradorSimples())
    # jogo = Jogo(GeradorIA())

    while True:
        continuar = jogo.jogar_turno()
        if not continuar:
            break

            from src.geradores.gerador_ia import GeradorIA

            jogo = Jogo(GeradorIA())