from src.jogo.jogador import Jogador

def test_jogador_vida_inicial():
    j = Jogador()
    assert j.vida == 20