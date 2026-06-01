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
        xp      (int): Experiência TOTAL acumulada (nunca diminui).
        nivel   (int): Nível atual do herói. Sobe conforme o XP acumulado.
    """

    # ── Atributos de CLASSE (constantes de balanceamento, compartilhadas) ──────
    # Slide "Atributos de Instância e de Classe": valores fixos que valem para
    # TODOS os jogadores ficam na classe, não na instância.
    ATK_POR_NIVEL = 2     # ganho de ATK a cada nível
    HP_POR_NIVEL  = 12    # ganho de HP_max a cada nível
    XP_BASE_NIVEL = 10    # fator-base do custo de XP (fórmula triangular)
    ESQ_POR_NIVEL = 0.005 # pequeno ganho de esquiva por nível
    ESQ_MAXIMA    = 0.6   # teto de esquiva por progressão de nível

    def __init__(self, nome: str, hp: int = 20, atk: int = 5, xp: int = 0, esq: float= 0.3, moedas: int = 0) -> None:
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
        if esq < 0:
            raise ValueError("ESQUIVA inicial não pode ser negativa")

        self.nome   = nome
        self.hp_max = hp
        self.hp     = hp
        self.atk    = atk
        self.xp     = xp
        self.nivel  = 1          # todo herói começa no nível 1
        self.esq = esq
        self.esq_max = 1
        self.moedas = moedas
        self.inventario: list = []

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
    
    def aumenta_esq(self, quantidade: int) -> int:
        """
        Restaura ESQ do jogador sem ultrapassar a ESQ máxima.

        Parâmetros:
            quantidade (int): Quantidade de ESQ a restaurar. Deve ser >= 0.

        Retorna:
            int: ESQ efetivamente recuperado.

        Levanta:
            ValueError: Se quantidade for negativa.
        """
        if quantidade < 0:
            raise ValueError("Aumento de esquiva não pode ser negativo.")

        esq_antes = self.esq
        self.esq  = min(self.esq_max, self.esq + quantidade)
        return self.esq - esq_antes
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
        self._atualizar_nivel()

    # ── Progressão de nível ───────────────────────────────────────────────────

    def xp_para_proximo_nivel(self) -> int:
        """
        XP TOTAL acumulado necessário para alcançar o próximo nível.

        Usa uma curva triangular: custo = XP_BASE_NIVEL * nivel * (nivel + 1).
        Assim os primeiros níveis chegam rápido (sensação de progresso) e os
        níveis altos exigem cada vez mais XP.
        """
        return self.XP_BASE_NIVEL * self.nivel * (self.nivel + 1)

    def _atualizar_nivel(self) -> int:
        """
        Sobe o herói de nível enquanto houver XP suficiente.

        Encapsulamento: método _protegido (convenção do slide "Encapsulamento —
        3 níveis de visibilidade"). É detalhe interno chamado por ganhar_xp();
        não faz parte da interface pública usada pelas telas/API.

        A cada nível: +ATK, +HP_max, pequeno +ESQ e CURA TOTAL (recompensa).

        Retorna:
            int: quantos níveis subiu nesta chamada (0 se não subiu).
        """
        niveis_ganhos = 0
        while self.xp >= self.xp_para_proximo_nivel():
            self.nivel  += 1
            self.atk    += self.ATK_POR_NIVEL
            self.hp_max += self.HP_POR_NIVEL
            self.hp      = self.hp_max                       # cura total ao subir
            self.esq     = min(self.ESQ_MAXIMA, self.esq + self.ESQ_POR_NIVEL)
            niveis_ganhos += 1
        return niveis_ganhos

    # ── Pontuação (comparativo de competição) ─────────────────────────────────

    @property
    def pontuacao(self) -> int:
        """
        Pontuação simples do herói, para comparar runs entre jogadores.

        Encapsulamento via @property (slide "@property — Getter e Setter"):
        o valor é CALCULADO sob demanda a partir do estado, exposto como se
        fosse um atributo (`jogador.pontuacao`), sem permitir escrita direta.

        Fórmula (proposital de simples): XP acumulado + bônus por nível
        alcançado + moedas guardadas.
        """
        return self.xp + (self.nivel - 1) * 50 + self.moedas

    def ganhar_moedas(self, quantidade: int) -> None:
        """
        Adiciona moedas ao jogador.

        Parâmetros:
            quantidade (int): Quantidade de moedas a ganhar. Deve ser >= 0.

        Levanta:
            ValueError: Se quantidade for negativa.
        """
        if quantidade < 0:
            raise ValueError("moedas ganhas não podem ser negativas.")
        self.moedas += quantidade

    # ── Inventário ────────────────────────────────────────────────────────────

    def adicionar_item(self, item) -> None:
        """
        Adiciona um Item ao inventário do jogador.

        Parâmetros:
            item: Instância de Item. Não pode ser None.

        Levanta:
            ValueError: Se item for None.
        """
        if item is None:
            raise ValueError("Item não pode ser None.")
        self.inventario.append(item)

    def usar_item(self, indice: int) -> dict:
        """
        Usa o item do inventário no índice fornecido e o remove da lista.

        Parâmetros:
            indice (int): Posição do item no inventário (0-based).

        Retorna:
            dict: Resultado do efeito aplicado (mesmo formato de Item.usar()).

        Levanta:
            IndexError: Se o índice for inválido.
        """
        if indice < 0 or indice >= len(self.inventario):
            raise IndexError("Índice de inventário inválido.")
        item = self.inventario.pop(indice)
        return item.usar(self)

    def inventario_resumo(self) -> list[dict]:
        """
        Retorna uma representação serializável do inventário.

        Retorna:
            list[dict]: Cada elemento contém nome e bônus do item.
        """
        return [
            {
                "nome": it.nome,
                "bonus_atk": it.bonus_atk,
                "bonus_hp": it.bonus_hp,
                "bonus_esq": it.bonus_esq,
            }
            for it in self.inventario
        ]

    # ── Representação ─────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        """Retorna representação legível do jogador para debug."""
        return (
            f"Jogador(nome={self.nome!r}, nivel={self.nivel}, "
            f"hp={self.hp}/{self.hp_max}, atk={self.atk}, xp={self.xp})"
        )
