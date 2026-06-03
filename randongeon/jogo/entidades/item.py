# randongeon/jogo/entidades/item.py

"""
Módulo responsável pela entidade Item.
"""


class Item:
    """
    Representa um item encontrado numa sala da masmorra.

    Atributos:
        nome      (str):   Nome exibível do item.
        bonus_atk (int):   Bônus de ataque. Padrão 0.
        bonus_hp  (int):   Bônus de HP. Padrão 0.
        bonus_esq (float): Bônus de esquiva. Padrão 0.
    """

    def __init__(
        self,
        nome: str,
        bonus_atk: int   = 0,
        bonus_hp:  int   = 0,
        bonus_esq: float = 0,
    ) -> None:
        """
        Inicializa um Item com os atributos fornecidos.

        Levanta:
            ValueError: Se nome for inválido, qualquer bônus for negativo,
                        ou todos os três bônus forem zero (item inútil).
        """
        if not nome or not isinstance(nome, str):
            raise ValueError("Nome do item deve ser uma string não vazia.")
        if bonus_atk < 0:
            raise ValueError("bonus_atk não pode ser negativo.")
        if bonus_hp < 0:
            raise ValueError("bonus_hp não pode ser negativo.")
        if bonus_esq < 0:
            raise ValueError("bonus_esq não pode ser negativo.")
        if bonus_atk == 0 and bonus_hp == 0 and bonus_esq == 0:
            raise ValueError(
                "Um item deve ter pelo menos um bônus (atk, hp ou esq) maior que zero."
            )

        self.nome      = nome
        self.bonus_atk = bonus_atk
        self.bonus_hp  = bonus_hp
        self.bonus_esq = bonus_esq

    # ── Uso ───────────────────────────────────────────────────────────────────

    def usar(self, jogador) -> dict:
        """
        Aplica os efeitos do item no jogador fornecido.

        Regras de aplicação:
          - bonus_atk: somado diretamente ao atk do jogador.
          - bonus_hp:  curado via jogador.curar(), respeitando o hp_max.
          - bonus_esq: aumentado via jogador.aumenta_esq(), respeitando esq_max.

        IMPORTANTE: bonus_esq é aplicado via jogador.aumenta_esq() e NÃO por
        atribuição direta. Isso garante que o teto de esq_max seja respeitado
        e que os testes de mock possam verificar a chamada do método.

        Parâmetros:
            jogador: Instância de Jogador que receberá os efeitos.

        Retorna:
            dict: Chaves presentes apenas se o bônus correspondente for > 0.
                  {"atk": 2}              → só ataque
                  {"hp": 5}               → só cura (valor efetivo)
                  {"esq": 0.1}            → só esquiva (valor efetivo)
                  {"atk": 1, "hp": 3}     → combinado
                  {"atk": 2, "hp": 5, "esq": 0.1} → triplo

        Levanta:
            ValueError: Se jogador for None.
        """
        if jogador is None:
            raise ValueError("Jogador não pode ser None.")

        resultado = {}

        if self.bonus_atk > 0:
            jogador.atk     += self.bonus_atk
            resultado["atk"] = self.bonus_atk

        if self.bonus_hp > 0:
            hp_recuperado   = jogador.curar(self.bonus_hp)
            resultado["hp"] = hp_recuperado
            # Lote M: poções de cura também purgam o veneno. Guard para suportar
            # jogadores mockados nos testes que não implementam curar_veneno.
            curar_veneno = getattr(jogador, "curar_veneno", None)
            if callable(curar_veneno):
                curar_veneno()

        if self.bonus_esq > 0:
            # CORRETO: delega para aumenta_esq() para respeitar esq_max
            # e para que os testes de mock possam verificar a chamada.
            esq_recuperada   = jogador.aumenta_esq(self.bonus_esq)
            resultado["esq"] = esq_recuperada

        return resultado

    # ── Representação ─────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"Item(nome={self.nome!r}, "
            f"bonus_atk={self.bonus_atk}, "
            f"bonus_hp={self.bonus_hp}, "
            f"bonus_esq={self.bonus_esq})"
        )