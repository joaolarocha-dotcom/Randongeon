# randongeon/jogo/sistemas/gerador.py

"""
Módulo responsável pela geração procedural de salas da masmorra.
A classe GeradorSala é responsável exclusivamente por produzir dados —
não realiza nenhuma saída no terminal. A camada de apresentação (Masmorra)
é quem decide o que exibir com base no retorno deste módulo.
"""

import random

from jogo.entidades.inimigo import Inimigo, NOMES_DIFICULDADE_1, NOMES_DIFICULDADE_2
from jogo.entidades.item import Item
from jogo.entidades.loja import Loja

# ── Dados estáticos das salas ─────────────────────────────────────────────────

DESCRICOES_SALA = [
    "Uma sala úmida que fede a mofo e a coisas que era melhor não identificar.",
    "Cristais pálidos pulsam nas paredes, como se a caverna respirasse junto com você.",
    "Ossos cobrem o chão. Alguns ainda parecem surpresos.",
    "Musgo engole as paredes; o silêncio aqui tem peso próprio.",
    "Um salão vazio onde seus passos voltam como ecos que não são bem os seus.",
    "Marcas de garras sobem pelas paredes até o teto. Subindo. Sempre subindo.",
    "Velas acesas há séculos teimam em não apagar. Ninguém pediu companhia.",
    "Uma poça escura reflete um teto que não está lá.",
    "O ar é frio e parado, como o de um lugar acostumado a esperar.",
    "Inscrições gastas cobrem a parede. A única legível diz: 'volte'.",
    "Correntes enferrujadas pendem do nada, balançando sem vento.",
    "Um cheiro doce e errado paira no ar. Melhor não procurar a fonte.",
]

CATALOGO_ITENS = [
    Item("Poção de Força",        bonus_atk=1),
    Item("Grande Poção de Força", bonus_atk=2),
    Item("Elixir Vital",          bonus_hp=5),
    Item("Erva Medicinal",        bonus_hp=3),
    Item("Poção do Mestre Gato",  bonus_esq=0.05),
    Item("Elixir do Mestre Mosca",bonus_esq=0.1),
    Item("Tônico do Guerreiro",   bonus_atk=1, bonus_hp=2),
]



class GeradorSala:
    """
    Gera o conteúdo de cada sala da masmorra de forma procedural.

    Cada chamada a gerar_sala() retorna uma tupla com três elementos:
        - tipo      (str):  'item' ou 'inimigo'
        - conteudo  (obj):  instância de Item ou Inimigo
        - descricao (str):  descrição textual do ambiente da sala

    A chance de uma sala conter um item é de 1 em 5 (20%).
    Caso contrário, um inimigo é gerado com dificuldade baseada no andar.

    Atributos:
        _chance_item (int): Denominador da chance de item aparecer (padrão 5).
                            Exposto para facilitar testes determinísticos.
    """

    def __init__(self, chance_item: int = 20) -> None:
        """
        Inicializa o GeradorSala.

        Parâmetros:
            chance_item (int): 1 em cada N salas terá um item. Padrão 5.
                               Deve ser >= 2.

        Levanta:
            ValueError: Se chance_item for menor que 2.
        """
        if chance_item < 2:
            raise ValueError("chance_item deve ser >= 2.")
        self._chance_item = chance_item

    # ── Interface pública ─────────────────────────────────────────────────────

    def gerar_sala(self, andar: int = 1) -> tuple:
        if andar < 1:
            raise ValueError("O andar deve ser >= 1.")

        descricao = random.choice(DESCRICOES_SALA)
        
        # Sorteio (1 a 20)
        sorte = random.randint(1, 20)

        if sorte <= 3:  # 15% chance de Loja
            return self.gerar_loja()

        elif sorte <= 5:  # 10% chance de Item (sorte 4 ou 5)
            return self.gerar_item(descricao)

        else:  # 75% chance de Inimigo
            return self.gerar_inimigo(andar, descricao)

    def gerar_loja(self) -> tuple:
        """Retorna a tupla correta para a Masmorra não dar erro de desempacotamento."""
        desc = "Um mercador encapuzado brilha uma lanterna em sua direção."
        # IMPORTANTE: Retornar exatamente 3 itens
        return ("loja", None, desc)

    def gerar_item(self, descricao: str = "") -> tuple:
        """
        Sorteia um item aleatório do catálogo de itens disponíveis.

        Parâmetros:
            descricao (str): Descrição do ambiente da sala. Padrão string vazia.

        Retorna:
            tuple: ('item', Item, descricao)
        """
        item = random.choice(CATALOGO_ITENS)
        return ("item", item, descricao)

    def gerar_inimigo(self, andar: int = 1, descricao: str = "") -> tuple:
        """
        Gera um inimigo aleatório escalado ao andar atual.

        Parâmetros:
            andar     (int): Andar atual. Influencia a dificuldade do inimigo.
            descricao (str): Descrição do ambiente da sala. Padrão string vazia.

        Retorna:
            tuple: ('inimigo', Inimigo, descricao)

        Levanta:
            ValueError: Se andar for menor que 1.
        """
        if andar < 1:
            raise ValueError("O andar deve ser >= 1.")

        inimigo = Inimigo.gerar(andar)

        return ("inimigo", inimigo, descricao)
   # No gerador.py, adicione este método:

 
