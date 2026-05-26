# randongeon/jogo/entidades/inimigo.py

"""
Módulo responsável pela entidade Inimigo.
Define a classe Inimigo com atributos, comportamentos de combate e
um método estático de geração aleatória com dificuldade escalável.
"""

import random


# Pool de nomes por dificuldade — separado da lógica para facilitar testes
NOMES_DIFICULDADE_1 = ["Goblin", "Rato Gigante", "Nosferatu"]
NOMES_DIFICULDADE_2 = ["Esqueleto Guerreiro", "Orc", "Troll das Cavernas"]


class Inimigo:
    """
    Representa um inimigo encontrado nas salas da masmorra.

    Atributos:
        nome        (str): Nome do inimigo.
        hp          (int): Pontos de vida atuais.
        atk         (int): Poder de ataque.
        dificuldade (int): Nível de dificuldade (1 = comum, 2 = elite, 3 = boss).
        xp          (int): Experiência concedida ao jogador ao ser derrotado.
    """

    def __init__(
        self,
        nome: str,
        hp: int,
        atk: int,
        dificuldade: int,
        xp: int,
        moedas: int
    ) -> None:
        """
        Inicializa um Inimigo com os atributos fornecidos.

        Parâmetros:
            nome        (str): Nome do inimigo. Não pode ser vazio.
            hp          (int): Pontos de vida. Deve ser > 0.
            atk         (int): Poder de ataque. Deve ser > 0.
            dificuldade (int): Nível de dificuldade. Deve ser >= 1.
            xp          (int): XP concedido. Deve ser >= 0.

        Levanta:
            ValueError: Se qualquer atributo violar as restrições acima.
        """
        if not nome or not isinstance(nome, str):
            raise ValueError("Nome do inimigo deve ser uma string não vazia.")
        if hp <= 0:
            raise ValueError("HP do inimigo deve ser maior que zero.")
        if atk <= 0:
            raise ValueError("ATK do inimigo deve ser maior que zero.")
        if dificuldade < 1:
            raise ValueError("Dificuldade deve ser >= 1.")
        if xp < 0:
            raise ValueError("XP concedido não pode ser negativo.")
        if moedas < 0:
            raise ValueError("moedas concedidas não podem ser negativas.")

        self.nome        = nome
        self.hp          = hp
        self.atk         = atk
        self.dificuldade = dificuldade
        self.xp          = xp
        self.moedas      = moedas

    # ── Estado ────────────────────────────────────────────────────────────────

    def esta_vivo(self) -> bool:
        """
        Verifica se o inimigo ainda está vivo.

        Retorna:
            bool: True se hp > 0, False caso contrário.
        """
        return self.hp > 0

    def receber_dano(self, dano: int) -> int:
        """
        Aplica dano ao inimigo. O HP nunca fica negativo.

        Parâmetros:
            dano (int): Valor de dano a aplicar. Deve ser >= 0.

        Retorna:
            int: Dano efetivamente sofrido.

        Levanta:
            ValueError: Se dano for negativo.
        """
        if dano < 0:
            raise ValueError("Dano não pode ser negativo.")

        dano_efetivo = min(dano, self.hp)
        self.hp -= dano_efetivo
        return dano_efetivo

    # ── Geração ───────────────────────────────────────────────────────────────

    @staticmethod
    def gerar(andar: int = 1) -> "Inimigo":
        """
        Gera um inimigo aleatório com dificuldade baseada no andar atual.

        A dificuldade 2 (elite) tem 30% de chance de aparecer a partir
        do andar 3. Abaixo disso, apenas dificuldade 1 é gerada.

        Parâmetros:
            andar (int): Andar atual da masmorra. Usado para escalar dificuldade.
                         Deve ser >= 1.

        Retorna:
            Inimigo: Nova instância com atributos gerados aleatoriamente.

        Levanta:
            ValueError: Se andar for menor que 1.
        """
        if andar < 1:
            raise ValueError("O andar deve ser >= 1.")

        pode_ser_elite = andar >= 3 and random.random() < 0.3

        if pode_ser_elite:
            dificuldade = 2
            nome        = random.choice(NOMES_DIFICULDADE_2)
            hp          = random.randint(8, 15)
            atk         = random.randint(3, 5)
            xp          = random.randint(25, 50)
            moedas      = random.randint(6,11)
        else:
            dificuldade = 1
            nome        = random.choice(NOMES_DIFICULDADE_1)
            hp          = random.randint(3, 8)
            atk         = random.randint(1, 3)
            xp          = random.randint(10, 20)
            moedas      = random.randint(0,5)

        return Inimigo(nome, hp, atk, dificuldade, xp, moedas)

    # ── Representação ─────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        """Retorna representação legível do inimigo para debug."""
        return (
            f"Inimigo(nome={self.nome!r}, hp={self.hp}, "
            f"atk={self.atk}, dificuldade={self.dificuldade}, xp={self.xp})"
        )
