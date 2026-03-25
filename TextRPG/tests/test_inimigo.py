from src.jogo.inimigo import Inimigo

def test_inimigo_criacao():
    i = Inimigo("Goblin", 10, 3)
    assert i.nome == "Goblin"
    assert i.vida == 10