# randongeon/jogo/entidades/inimigo.py

"""
Módulo responsável pela entidade Inimigo.

v3 — Novos inimigos especiais, mecânicas únicas e balanceamento.

Novidades:
  - hp_max: teto de vida (usado pela mecânica de cura do Vampiro).
  - modificador_fuga: ajusta a chance de fuga por tipo de inimigo.
  - cura_percentual: % do dano causado que cura o inimigo (Vampiro).
  - absorcao_dano: pontos de armadura que reduzem dano recebido (Golem).
  - bonus_atk_por_turno: ATK ganho por turno de combate (Caçador).
  - chance_atordoar: probabilidade de pular o ataque do jogador (Banshee).
  - tipo_especial: identificador textual para bestiário e frontend.

Balanceamento:
  - Dif 1: ATK reduzido de 1-3 para 1-2. HP reduzido de 3-8 para 3-7.
  - Dif 2: threshold sobe de andar 3 para andar 5. Chance cai de 30% para 25%.
           ATK reduzido de 3-5 para 2-4. HP reduzido de 8-15 para 8-13.
  - Fuga por tipo: dif 1 +10%, dif 2 -5%, especiais variam.
"""

import random


# ── Pools de nomes base ───────────────────────────────────────────────────────

NOMES_DIFICULDADE_1 = ["Goblin", "Rato Gigante", "Zumbi"]
NOMES_DIFICULDADE_2 = ["Esqueleto Guerreiro", "Orc", "Troll das Cavernas"]


class Inimigo:
    """
    Representa um inimigo encontrado nas salas da masmorra.

    Atributos base:
        nome        (str): Nome do inimigo.
        hp          (int): Pontos de vida atuais.
        hp_max      (int): Pontos de vida máximos (novo v3).
        atk         (int): Poder de ataque.
        dificuldade (int): Nível (1=comum, 2=elite, 3=boss).
        xp          (int): XP concedido ao ser derrotado.
        moedas      (int): Moedas dropadas ao ser derrotado.

    Atributos especiais (padrão neutro — apenas inimigos especiais os usam):
        modificador_fuga    (float): Ajusta CHANCE_FUGA. + = mais fácil fugir.
        cura_percentual     (float): % do dano causado que cura o inimigo.
        absorcao_dano       (int):   Reduz dano recebido por ataque (armadura).
        bonus_atk_por_turno (int):   ATK ganho a cada turno de combate.
        chance_atordoar     (float): Chance de atordoar o jogador por 1 turno.
        tipo_especial       (str):   Identificador para bestiário/frontend.
    """

    def __init__(
        self,
        nome: str,
        hp: int,
        atk: int,
        dificuldade: int,
        xp: int,
        moedas: int,
        modificador_fuga: float = 0.0,
        cura_percentual: float = 0.0,
        absorcao_dano: int = 0,
        bonus_atk_por_turno: int = 0,
        chance_atordoar: float = 0.0,
        tipo_especial: str = None,
        chance_miss: float = 0.10,   # v3.1 — chance de errar ataque
        chance_drop: float = 0.10,   # v3.1 — chance de dropar item ao morrer
    ) -> None:
        """
        Inicializa um Inimigo com atributos base e atributos especiais opcionais.

        Levanta:
            ValueError: Se qualquer atributo violar as restrições de validação.
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
            raise ValueError("Moedas concedidas não podem ser negativas.")
        if not (0.0 <= cura_percentual <= 1.0):
            raise ValueError("cura_percentual deve estar entre 0.0 e 1.0.")
        if absorcao_dano < 0:
            raise ValueError("absorcao_dano não pode ser negativo.")
        if bonus_atk_por_turno < 0:
            raise ValueError("bonus_atk_por_turno não pode ser negativo.")
        if not (0.0 <= chance_atordoar <= 1.0):
            raise ValueError("chance_atordoar deve estar entre 0.0 e 1.0.")
        if not (0.0 <= chance_miss <= 1.0):
            raise ValueError("chance_miss deve estar entre 0.0 e 1.0.")
        if not (0.0 <= chance_drop <= 1.0):
            raise ValueError("chance_drop deve estar entre 0.0 e 1.0.")

        self.nome                = nome
        self.hp                  = hp
        self.hp_max              = hp           # novo v3
        self.atk                 = atk
        self.dificuldade         = dificuldade
        self.xp                  = xp
        self.moedas              = moedas
        self.modificador_fuga    = modificador_fuga
        self.cura_percentual     = cura_percentual
        self.absorcao_dano       = absorcao_dano
        self.bonus_atk_por_turno = bonus_atk_por_turno
        self.chance_atordoar     = chance_atordoar
        self.tipo_especial       = tipo_especial
        self.chance_miss         = chance_miss   # v3.1
        self.chance_drop         = chance_drop   # v3.1

    # ── Estado ────────────────────────────────────────────────────────────────

    def esta_vivo(self) -> bool:
        """Retorna True se hp > 0."""
        return self.hp > 0

    def receber_dano(self, dano: int) -> int:
        """
        Aplica dano ao inimigo considerando absorção de armadura.

        A absorção (atributo absorcao_dano) reduz o dano antes de atingir o HP.
        Usado pelo Golem de Pedra: absorcao_dano=2 significa que ataques de
        força <= 2 causam zero dano e ataques maiores têm o dano reduzido.

        Retorna:
            int: Dano efetivamente sofrido após absorção e limite de HP.

        Levanta:
            ValueError: Se dano for negativo.
        """
        if dano < 0:
            raise ValueError("Dano não pode ser negativo.")
        dano_apos_absorcao = max(0, dano - self.absorcao_dano)
        dano_efetivo       = min(dano_apos_absorcao, self.hp)
        self.hp           -= dano_efetivo
        return dano_efetivo

    def curar(self, quantidade: int) -> None:
        """
        Restaura HP sem ultrapassar hp_max.

        Usado pela mecânica do Vampiro das Sombras: após atacar, cura
        uma fração do dano causado ao jogador.

        Levanta:
            ValueError: Se quantidade for negativa.
        """
        if quantidade < 0:
            raise ValueError("Quantidade de cura não pode ser negativa.")
        self.hp = min(self.hp_max, self.hp + quantidade)

    # ── Geração pública ───────────────────────────────────────────────────────

    @staticmethod
    def gerar(andar: int = 1) -> "Inimigo":
        """
        Gera um inimigo aleatório adequado ao andar atual.

        Ordem de verificação:
          1. Horda de Goblins (10% de chance, disponível em qualquer andar).
          2. Elite (dif 2): disponível a partir do andar 5, 25% de chance.
             Dentro do elite: 40% de chance de ser um tipo especial,
             se algum estiver disponível para o andar atual.
          3. Comum (dif 1): caminho padrão.

        Limites dos especiais:
          - Golem de Pedra:      andar >= 8
          - Caçador Sombrio:     andar >= 10
          - Vampiro das Sombras: andar >= 15
          - Banshee:             andar >= 17

        Parâmetros:
            andar (int): Andar atual da masmorra. Deve ser >= 1.

        Levanta:
            ValueError: Se andar < 1.
        """
        if andar < 1:
            raise ValueError("O andar deve ser >= 1.")

        # 1. Horda de Goblins: sempre possível
        if random.random() < 0.10:
            return Inimigo._criar_horda()

        # 2. Elite: disponível a partir do andar 5
        if andar >= 5 and random.random() < 0.25:
            return Inimigo._gerar_elite(andar)

        # 3. Comum
        return Inimigo._gerar_comum()

    # ── Geradores internos ────────────────────────────────────────────────────

    @staticmethod
    def _gerar_comum() -> "Inimigo":
        """
        Gera inimigo comum (dif 1).

        Balanceamento v3:
          - ATK reduzido para 1-2 (era 1-3): início de jogo mais justo.
          - HP reduzido para 3-7 (era 3-8).
          - modificador_fuga=+0.10: fácil fugir de inimigos fracos.
        """
        nome   = random.choice(NOMES_DIFICULDADE_1)
        hp     = random.randint(3, 7)
        atk    = random.randint(1, 2)
        xp     = random.randint(8, 18)
        moedas = random.randint(0, 4)
        # miss por tipo: Zumbi lento (20%), Goblin (15%), Rato (10%)
        miss = {"Zumbi": 0.20, "Goblin": 0.15, "Rato Gigante": 0.10}.get(nome, 0.12)
        return Inimigo(nome, hp, atk, 1, xp, moedas,
                       modificador_fuga=0.10, chance_miss=miss, chance_drop=0.08)

    @staticmethod
    def _gerar_elite(andar: int) -> "Inimigo":
        """
        Gera inimigo elite (dif 2).

        Se inimigos especiais estiverem disponíveis para o andar atual,
        há 40% de chance de um ser escolhido no lugar de um elite comum.

        Balanceamento v3:
          - ATK reduzido para 2-4 (era 3-5).
          - HP reduzido para 8-13 (era 8-15).
          - modificador_fuga=-0.05: levemente mais difícil fugir de elites.
        """
        especiais_disponiveis = []
        if andar >= 8:
            especiais_disponiveis.append("golem")
        if andar >= 10:
            especiais_disponiveis.append("cacador")
        if andar >= 15:
            especiais_disponiveis.append("vampiro")
        if andar >= 17:
            especiais_disponiveis.append("banshee")

        if especiais_disponiveis and random.random() < 0.40:
            tipo = random.choice(especiais_disponiveis)
            return Inimigo._criar_especial(tipo)

        # Elite comum
        nome   = random.choice(NOMES_DIFICULDADE_2)
        hp     = random.randint(8, 13)
        atk    = random.randint(2, 4)
        xp     = random.randint(25, 45)
        moedas = random.randint(5, 10)
        return Inimigo(nome, hp, atk, 2, xp, moedas,
                       modificador_fuga=-0.05, chance_miss=0.10, chance_drop=0.18)

    # ── Dispatcher de especiais ───────────────────────────────────────────────

    @staticmethod
    def _criar_especial(tipo: str) -> "Inimigo":
        """Direciona para a fábrica correta pelo identificador de tipo."""
        fabricas = {
            "vampiro": Inimigo._criar_vampiro,
            "golem":   Inimigo._criar_golem,
            "cacador": Inimigo._criar_cacador,
            "banshee": Inimigo._criar_banshee,
        }
        if tipo not in fabricas:
            raise ValueError(f"Tipo especial desconhecido: {tipo!r}")
        return fabricas[tipo]()

    # ── Fábricas dos inimigos especiais ───────────────────────────────────────

    @staticmethod
    def _criar_vampiro() -> "Inimigo":
        """
        Vampiro das Sombras — aparece a partir do andar 15.

        Mecânica: cura 20% do dano causado ao atacar o jogador.
        Isso torna o combate prolongado progressivamente mais difícil,
        incentivando o jogador a causar dano alto e terminar rápido.

        Fuga: -10% (vampiros são rápidos e persistentes).
        """
        hp     = random.randint(12, 18)
        atk    = random.randint(4, 6)
        xp     = random.randint(35, 55)
        moedas = random.randint(8, 14)
        return Inimigo(
            "Vampiro das Sombras", hp, atk, 2, xp, moedas,
            modificador_fuga=-0.10,
            cura_percentual=0.20,
            tipo_especial="vampiro",
            chance_miss=0.05, chance_drop=0.22,
        )

    @staticmethod
    def _criar_golem() -> "Inimigo":
        """
        Golem de Pedra — aparece a partir do andar 8.

        Mecânica: absorcao_dano=2, processada em receber_dano().
        Ataques <= 2 de força causam zero dano. ATK=5 causa apenas 3 de dano.
        Incentiva o jogador a buscar itens de ATK antes de confrontar um Golem.

        Alto HP para compensar o ATK baixo.
        Fuga: -5% (lento, mas difícil de escapar quando te cerca).
        """
        hp     = random.randint(15, 22)
        atk    = random.randint(2, 4)
        xp     = random.randint(30, 45)
        moedas = random.randint(7, 12)
        return Inimigo(
            "Golem de Pedra", hp, atk, 2, xp, moedas,
            modificador_fuga=-0.05,
            absorcao_dano=2,
            tipo_especial="golem",
            chance_miss=0.10, chance_drop=0.20,
        )

    @staticmethod
    def _criar_cacador() -> "Inimigo":
        """
        Caçador Sombrio — aparece a partir do andar 10.

        Mecânica: ganha +1 ATK por turno. Começa com vida baixa (6-10 HP),
        incentivando o jogador a eliminar rápido antes que o ATK escale.
        Em 3-4 turnos pode ser mais perigoso que um elite comum.

        Fuga: +5% (ligeiramente mais fácil fugir — se o jogador demorar,
        o ATK alto o forçará a tentar escapar).
        """
        hp     = random.randint(6, 10)    # vida intencionalm. baixa
        atk    = random.randint(3, 5)
        xp     = random.randint(30, 50)
        moedas = random.randint(7, 13)
        return Inimigo(
            "Caçador Sombrio", hp, atk, 2, xp, moedas,
            modificador_fuga=+0.05,
            bonus_atk_por_turno=1,
            tipo_especial="cacador",
            chance_miss=0.05, chance_drop=0.20,
        )

    @staticmethod
    def _criar_horda() -> "Inimigo":
        """
        Horda de Goblins — disponível em qualquer andar.

        Representa 3 goblins combinados: HP acumulado (9-12),
        ATK baixo (1-2 por "goblin"), mas constante.
        Disponível desde o andar 1 para variedade no início do jogo.

        Fuga: +20% (goblins são lentos e desorganizados em grupo).
        """
        hp     = random.randint(9, 12)
        atk    = random.randint(1, 2)
        xp     = random.randint(20, 35)
        moedas = random.randint(3, 8)
        return Inimigo(
            "Horda de Goblins", hp, atk, 1, xp, moedas,
            modificador_fuga=+0.20,
            tipo_especial="horda",
            chance_miss=0.20, chance_drop=0.12,
        )

    @staticmethod
    def _criar_banshee() -> "Inimigo":
        """
        Banshee — aparece a partir do andar 17.

        Mecânica: 30% de chance de atordoar o jogador a cada ataque.
        Um turno atordoado = jogador perde seu ataque naquele turno.
        Cria um elemento de risco imprevisível nos andares avançados.

        Fuga: -15% (o grito da Banshee paralisa quem tenta escapar).
        """
        hp     = random.randint(10, 15)
        atk    = random.randint(3, 6)
        xp     = random.randint(40, 60)
        moedas = random.randint(10, 16)
        return Inimigo(
            "Banshee", hp, atk, 2, xp, moedas,
            modificador_fuga=-0.15,
            chance_atordoar=0.30,
            tipo_especial="banshee",
            chance_miss=0.05, chance_drop=0.25,
        )

    # ── Representação ─────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        especial = f", tipo={self.tipo_especial!r}" if self.tipo_especial else ""
        return (
            f"Inimigo(nome={self.nome!r}, hp={self.hp}/{self.hp_max}, "
            f"atk={self.atk}, dificuldade={self.dificuldade}, xp={self.xp}"
            f"{especial})"
        )