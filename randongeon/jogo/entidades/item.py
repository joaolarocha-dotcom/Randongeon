# randongeon/jogo/entidades/item.py

"""
Módulo responsável pela entidade Item.
Define a classe Item, que representa qualquer objeto coletável da masmorra:
itens de cura (bonus_hp) e equipamentos (bonus_atk).
Toda saída para o terminal é responsabilidade de quem chama usar(),
mantendo a lógica pura e completamente testável.
"""


class Item:
    """
    Representa um item encontrado numa sala da masmorra.

    Um item pode conceder bônus de ATK, bônus de HP, ou ambos ao mesmo tempo.
    O método usar() aplica os efeitos no jogador e retorna um dicionário
    com os valores efetivamente aplicados — sem realizar nenhum print.

    Atributos:
        nome      (str): Nome exibível do item.
        bonus_atk (int): Bônus de ataque concedido ao usar. Padrão 0.
        bonus_hp  (int): Bônus de HP concedido ao usar. Padrão 0.
    """

    def __init__(self, nome: str, bonus_atk: int = 0, bonus_hp: int = 0) -> None:
        """
        Inicializa um Item com os atributos fornecidos.

        Parâmetros:
            nome      (str): Nome do item. Não pode ser vazio ou None.
            bonus_atk (int): Bônus de ataque. Deve ser >= 0.
            bonus_hp  (int): Bônus de HP. Deve ser >= 0.

        Levanta:
            ValueError: Se nome for inválido ou qualquer bônus for negativo.
            ValueError: Se ambos bonus_atk e bonus_hp forem zero
                        (item sem efeito algum não é permitido).
        """
        if not nome or not isinstance(nome, str):
            raise ValueError("Nome do item deve ser uma string não vazia.")
        if bonus_atk < 0:
            raise ValueError("bonus_atk não pode ser negativo.")
        if bonus_hp < 0:
            raise ValueError("bonus_hp não pode ser negativo.")
        if bonus_atk == 0 and bonus_hp == 0:
            raise ValueError("Um item deve ter pelo menos um bônus (atk ou hp) maior que zero.")

        self.nome      = nome
        self.bonus_atk = bonus_atk
        self.bonus_hp  = bonus_hp

    # ── Uso ───────────────────────────────────────────────────────────────────

    def usar(self, jogador) -> dict:
        """
        Aplica os efeitos do item no jogador fornecido.

        - bonus_atk: somado diretamente ao atk do jogador.
        - bonus_hp: curado via jogador.curar(), respeitando o hp_max.

        Não realiza nenhuma saída no terminal. Quem exibe a mensagem
        ao jogador é a camada de apresentação (Masmorra / main.py).

        Parâmetros:
            jogador: Instância de Jogador que receberá os efeitos.

        Retorna:
            dict: Dicionário com as chaves presentes apenas se o bônus
                  correspondente for > 0. Exemplos:
                  {"atk": 2}            → só bônus de ataque aplicado
                  {"hp": 5}             → só cura aplicada (valor efetivo)
                  {"atk": 1, "hp": 3}   → ambos aplicados

        Levanta:
            ValueError: Se jogador for None.
        """
        if jogador is None:
            raise ValueError("Jogador não pode ser None.")

        resultado = {}

        if self.bonus_atk > 0:
            jogador.atk      += self.bonus_atk
            resultado["atk"]  = self.bonus_atk

        if self.bonus_hp > 0:
            hp_recuperado    = jogador.curar(self.bonus_hp)
            resultado["hp"]  = hp_recuperado

        return resultado

    # ── Representação ─────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        """Retorna representação legível do item para debug."""
        return (
            f"Item(nome={self.nome!r}, "
            f"bonus_atk={self.bonus_atk}, bonus_hp={self.bonus_hp})"
        )