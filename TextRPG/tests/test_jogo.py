from src.jogo.jogo import Jogo
from src.jogo.inimigo import Inimigo

class FakeGerador:
    def gerar_sala(self):
        return "Sala fake"

    def gerar_inimigo(self):
        return Inimigo("Fake", 5, 1)

def test_jogo_inicializacao():
    jogo = Jogo(FakeGerador())
    assert jogo.jogador.vida > 0