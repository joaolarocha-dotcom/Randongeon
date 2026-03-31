# randongeon/jogo/sistemas/loja.py

import random
from jogo.entidades.item import Item

class Loja:
    def __init__(self):
        # Definimos os itens e seus preços
        self.estoque = [
            {"item": Item("Grande Poção de Força", bonus_atk=2), "preco": 15},
            {"item": Item("Elixir Vital",          bonus_hp=8),  "preco": 10},
            {"item": Item("Elixir do Mestre Mosca", bonus_esq=0.1), "preco": 20},
            {"item": Item("Tônico Supremo", bonus_atk=2, bonus_hp=5, bonus_esq=0.1), "preco": 40},
        ]
        # O mercador escolhe 2 itens aleatórios para vender nesta visita
        self.ofertas = random.sample(self.estoque, 2)

    def menu(self, jogador):
        """Este é o método que a masmorra.py está chamando"""
        while self.ofertas:
            print(f"\n--- MERCADO (Moedas: {jogador.moedas}) ---")
            for i, oferta in enumerate(self.ofertas):
                print(f"{i+1}. {oferta['item'].nome} - {oferta['preco']} moedas")
            print("0. Sair")

            op = input("\nO que deseja comprar? > ")
            
            if op == "0":
                break
            
            if op.isdigit() and 0 < int(op) <= len(self.ofertas):
                indice = int(op) - 1
                escolha = self.ofertas[indice]
                
                if jogador.moedas >= escolha["preco"]:
                    # Realiza a transação
                    jogador.moedas -= escolha["preco"]
                    escolha["item"].usar(jogador)
                    self.ofertas.pop(indice)
                    print(f"\n[COMPRA] Você obteve {escolha['item'].nome}!")
                else:
                    print("\n[ERRO] Moedas insuficientes!")
            else:
                print("\nOpção inválida.")
        
        print("\nO mercador recolhe as coisas e acena um adeus.")
