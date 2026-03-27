# randongeon/jogo/entidades/jogador.py

"""
Módulo responsável pela entidade do jogador.
Define a classe Jogador com todos os atributos, validações e comportamentos
necessários para o funcionamento do RPG e para a cobertura de testes unitários.
"""


class Jogador:
    """
    Representa o personagem controlado pelo jogador.

    Atributos:
        nome    (str): Nome do personagem.
        hp      (int): Pontos de vida atuais.
        hp_max  (int): Pontos de vida máximos (definido no momento da criação).
        atk     (int): Poder de ataque base.
        xp      (int): Experiência acumulada ao longo das runs.
    """

    def __init__(self, nome: str, hp: int = 20, atk: int = 5, xp: int = 0) -> None:
        """
        Inicializa um Jogador com os atributos fornecidos.

        Parâmetros:
            nome (str): Nome do personagem. Não pode ser vazio ou None.
            hp   (int): Pontos de vida iniciais e máximos. Deve ser > 0.
            atk  (int): Poder de ataque inicial. Deve ser > 0.
            xp   (int): XP inicial (útil para testes e saves futuros). Deve ser >= 0.

        Levanta:
            ValueError: Se nome for vazio/None, hp <= 0, atk <= 0 ou xp < 0.
        """
        if not isinstance(nome, str) or not nome.strip():
            raise ValueError("Nome do jogador deve ser uma string não vazia.")
        if hp <= 0:
            raise ValueError("HP inicial deve ser maior que zero.")
        if atk <= 0:
            raise ValueError("ATK inicial deve ser maior que zero.")
        if xp < 0:
            raise ValueError("XP inicial não pode ser negativo.")

        self.nome   = nome
        self.hp_max = hp
        self.hp     = hp
        self.atk    = atk
        self.xp     = xp

    # ── Vida ──────────────────────────────────────────────────────────────────

    def esta_vivo(self) -> bool:
        """
        Verifica se o jogador ainda está vivo.

        Retorna:
            bool: True se hp > 0, False caso contrário.
        """
        return self.hp > 0

    def receber_dano(self, dano: int) -> int:
        """
        Aplica dano ao jogador. O HP nunca fica negativo.

        Parâmetros:
            dano (int): Valor bruto de dano a ser aplicado. Deve ser >= 0.

        Retorna:
            int: Dano efetivamente sofrido (pode ser menor se HP restante for menor).

        Levanta:
            ValueError: Se dano for negativo.
        """
        if dano < 0:
            raise ValueError("Dano não pode ser negativo.")

        dano_efetivo = min(dano, self.hp)
        self.hp -= dano_efetivo
        return dano_efetivo

    def curar(self, quantidade: int) -> int:
        """
        Restaura HP do jogador sem ultrapassar o HP máximo.

        Parâmetros:
            quantidade (int): Quantidade de HP a restaurar. Deve ser >= 0.

        Retorna:
            int: HP efetivamente recuperado.

        Levanta:
            ValueError: Se quantidade for negativa.
        """
        if quantidade < 0:
            raise ValueError("Quantidade de cura não pode ser negativa.")

        hp_antes = self.hp
        self.hp  = min(self.hp_max, self.hp + quantidade)
        return self.hp - hp_antes

    # ── Progressão ────────────────────────────────────────────────────────────

    def ganhar_xp(self, quantidade: int) -> None:
        """
        Adiciona XP ao jogador.

        Parâmetros:
            quantidade (int): Quantidade de XP a ganhar. Deve ser >= 0.

        Levanta:
            ValueError: Se quantidade for negativa.
        """
        if quantidade < 0:
            raise ValueError("XP ganho não pode ser negativo.")
        self.xp += quantidade

    # ── Representação ─────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        """Retorna representação legível do jogador para debug."""
        return (
            f"Jogador(nome={self.nome!r}, hp={self.hp}/{self.hp_max}, "
            f"atk={self.atk}, xp={self.xp})"
        )