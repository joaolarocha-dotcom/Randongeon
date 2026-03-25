from openai import OpenAI
from src.jogo.inimigo import Inimigo
from src.geradores.gerador_base import GeradorBase

class GeradorIA(GeradorBase):
    def __init__(self):
        self.client = OpenAI()

    def gerar_sala(self):
        response = self.client.responses.create(
            model="gpt-5-mini",
            input="Descreva uma sala de RPG sombria em no máximo 2 linhas."
        )
        return response.output[0].content[0].text

    def gerar_inimigo(self):
        response = self.client.responses.create(
            model="gpt-5-mini",
            input="Crie um inimigo no formato: nome,vida,ataque (apenas isso, sem explicação)"
        )

        texto = response.output[0].content[0].text
        nome, vida, ataque = texto.split(",")

        return Inimigo(nome.strip(), int(vida), int(ataque))