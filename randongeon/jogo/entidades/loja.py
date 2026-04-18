# randongeon/jogo/entidades/loja.py

import random
from jogo.entidades.item import Item


class Loja:
    def __init__(self):
        self.estoque = [
            {"item": Item("Grande Poção de Força", bonus_atk=2),                          "preco": 5},
            {"item": Item("Elixir Vital",          bonus_hp=8),                            "preco": 6},
            {"item": Item("Elixir do Mestre Mosca", bonus_esq=0.1),                        "preco": 10},
            {"item": Item("Tônico Supremo", bonus_atk=2, bonus_hp=5, bonus_esq=0.1),      "preco": 20},
        ]
        self.ofertas = random.sample(self.estoque, 2)

    # ── Lógica pura (testável) ────────────────────────────────────────────────

    def comprar(self, indice: int, jogador) -> dict:
        """
        Realiza a compra de um item da lista de ofertas pelo índice informado.

        Este método contém apenas lógica pura — sem input() ou print() —
        o que o torna completamente testável por testes unitários.

        Parâmetros:
            indice  (int):    Posição do item em self.ofertas (0-based).
            jogador (Jogador): Instância do jogador que realiza a compra.

        Retorna:
            dict: {'sucesso': bool, 'mensagem': str}
                  sucesso=True  → transação efetuada, item aplicado.
                  sucesso=False → moedas insuficientes ou índice inválido.
        """
        if indice < 0 or indice >= len(self.ofertas):
            return {"sucesso": False, "mensagem": "Índice inválido."}

        escolha = self.ofertas[indice]

        if jogador.moedas < escolha["preco"]:
            return {"sucesso": False, "mensagem": "Moedas insuficientes."}

        jogador.moedas -= escolha["preco"]
        escolha["item"].usar(jogador)
        self.ofertas.pop(indice)

        return {"sucesso": True, "mensagem": f"Comprou {escolha['item'].nome}!"}

    # ── Apresentação (não testada unitariamente) ──────────────────────────────

    def menu(self, jogador):
        """Loop interativo da loja. Usa input() — não é testado diretamente."""
        while self.ofertas:
            print(f"\n--- MERCADO (Moedas: {jogador.moedas}) ---")
            for i, oferta in enumerate(self.ofertas):
                print(f"{i + 1}. {oferta['item'].nome} - {oferta['preco']} moedas")
            print("0. Sair")

            op = input("\nO que deseja comprar? > ")

            if op == "0":
                break

            if op.isdigit() and 0 < int(op) <= len(self.ofertas):
                resultado = self.comprar(int(op) - 1, jogador)
                print(f"\n{resultado['mensagem']}")
            else:
                print("\nOpção inválida.")

        print("\nO mercador recolhe as coisas e acena um adeus.")
