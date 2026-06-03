import random
from typing import Optional

from jogo.entidades.entidade import Entidade
from jogo.entidades.item import Item

# "Aranha Gigante" foi removida: era um resquício do Lote F (o nome do Bando de
# Goblins foi renomeado por engano para "Aranha Gigante" ao sair desta lista) e
# nunca teve sprite próprio — aparecia com o sprite do goblin, quebrando a
# imersão. O inimigo de "grupo" correto é o Bando de Goblins, que já existe como
# encontro especial próprio (HordaDeGoblins → BandoDeGoblins).
NOMES_DIFICULDADE_1 = ["Goblin", "Rato Gigante"]
NOMES_DIFICULDADE_2 = ["Esqueleto Guerreiro", "Orc", "Troll das Cavernas"]

# ── Escala de inimigos por andar (balanceamento v4 — "config F") ──────────────
# Comuns e elites ganham bônus de HP/ATK/moedas conforme o andar, para cada andar
# ser um desafio (antes eram triviais no fim). Calibrado por simulação Monte Carlo.
ESCALA_HP_POR_ANDAR    = 1.8   # bônus de HP ≈ andar * 1.8
ESCALA_ATK_DIVISOR     = 5     # +1 de ATK a cada 5 andares
ESCALA_MOEDAS_DIVISOR  = 2     # +1 de moeda a cada 2 andares
ELITE_HP_MULTIPLICADOR = 1.4   # elites escalam mais HP que comuns

# ── Rampa de presença de elites/especiais por andar (balanceamento) ───────────
# Até o andar 5 mantém a base; a partir do 6 a chance de aparecer um elite ou
# especial cresce com o andar (vale para os dois modos). Calibrado por simulação
# Monte Carlo (config "MODERADA"): no fim da campanha ~1 em 3 vira especial e
# ~1 em 5 vira elite, sem apagar os comuns.
ELITE_GATE_BASE     = 0.25   # chance de entrar no ramo elite/especial no andar 5
ELITE_GATE_STEP     = 0.04   # +chance por andar a partir do andar 6
ELITE_GATE_CAP      = 0.60   # teto da chance de entrar no ramo
ESPECIAL_RATIO_BASE = 0.40   # dentro do ramo, chance de ser ESPECIAL (vs elite)
ESPECIAL_RATIO_STEP = 0.02   # +chance de especial por andar
ESPECIAL_RATIO_CAP  = 0.60   # teto da chance de especial


def chance_elite(andar: int) -> float:
    """Chance de o encontro entrar no ramo elite/especial, escalando por andar."""
    if andar < 5:
        return 0.0
    if andar < 6:
        return ELITE_GATE_BASE
    return min(ELITE_GATE_CAP, ELITE_GATE_BASE + (andar - 5) * ELITE_GATE_STEP)


def ratio_especial(andar: int) -> float:
    """Dentro do ramo, chance de ser um ESPECIAL (em vez de um elite comum)."""
    return min(ESPECIAL_RATIO_CAP, ESPECIAL_RATIO_BASE + max(0, andar - 5) * ESPECIAL_RATIO_STEP)

# ── Veneno (Lote M) ───────────────────────────────────────────────────────────
# Chance de um inimigo COMUM (apenas Goblin e Rato Gigante) envenenar o jogador
# ao acertar um golpe. Mantida baixa de propósito — calibrada por simulação.
# Veneno = 1 de dano/turno por até Jogador.VENENO_DURACAO turnos.
CHANCE_VENENO = 0.08
NOMES_PODEM_ENVENENAR = ("Goblin", "Rato Gigante")

# ── Debuffs de elite (Lote B2) ────────────────────────────────────────────────
# Orc → Fraqueza (−ATK); Troll das Cavernas → reduz a esquiva (golpe de maça).
# Chances por acerto (a calibrar na próxima rodada de balanceamento).
CHANCE_FRAQUEZA        = 0.30
CHANCE_ESQUIVA_DEBUFF  = 0.35

# ── Evasão e identidade de elites (Lote 2 de balanceamento) ───────────────────
# `esquiva` = chance de o inimigo DESVIAR do golpe do jogador (≠ chance_miss, que
# é o inimigo errar o próprio ataque). Combate a monotonia do "mato tudo num
# golpe". Orc é esperto (esquiva moderada); Banshee é etérea (esquiva alta);
# Troll é um tanque de HP (sem armadura, sem esquiva).
ESQUIVA_ORC            = 0.15
ESQUIVA_BANSHEE        = 0.30
TROLL_HP_MULTIPLICADOR = 1.6   # Troll tem ~60% mais HP que um elite comum

# Flavor da picada de veneno, por inimigo (Lote 2 de textos). Mantido junto da
# definição dos inimigos para API e CLI usarem a MESMA mensagem.
MENSAGENS_VENENO = {
    "Rato Gigante": "O Rato Gigante crava seus dentes imundos em você; a saliva "
                    "contaminada arde na ferida. Você foi ENVENENADO!",
    "Goblin":       "A faca enferrujada e suja do Goblin te acerta de raspão e um "
                    "mal-estar sobe pelo corpo. Você foi ENVENENADO!",
}
MENSAGEM_VENENO_PADRAO = "Você foi ENVENENADO!"


def mensagem_veneno(nome_inimigo: str) -> str:
    """Texto temático de envenenamento conforme o inimigo (Goblin/Rato Gigante)."""
    return MENSAGENS_VENENO.get(nome_inimigo, MENSAGEM_VENENO_PADRAO)


def mensagem_fraqueza(nome_inimigo: str) -> str:
    """Texto do debuff de fraqueza (Orc)."""
    return (f"O {nome_inimigo} desfere um golpe brutal que abala seus músculos — "
            f"você fica ENFRAQUECIDO (ATK reduzido por alguns turnos)!")


def mensagem_esquiva_reduzida(nome_inimigo: str) -> str:
    """Texto do debuff de esquiva (Troll das Cavernas)."""
    return (f"A maça do {nome_inimigo} te acerta em cheio e te deixa ZONZO — "
            f"sua ESQUIVA cai no próximo turno!")

# ── Pools de loot (Lote C) ────────────────────────────────────────────────────
# Cada tipo de inimigo tem um pool temático. O pool padrão (LOOT_PADRAO) é usado
# por inimigos comuns e bosses. As subclasses sobrescrevem tabela_loot() para
# devolver o seu pool — é polimorfismo: quem rola o loot chama inimigo.tabela_loot()
# sem precisar saber o tipo concreto.
LOOT_PADRAO = [
    Item("Poção Menor de Cura",  bonus_hp=3),
    Item("Erva Medicinal",       bonus_hp=2),
    Item("Fragmento de Cristal", bonus_atk=1),
    Item("Pó de Velocidade",     bonus_esq=0.03),
    Item("Poção de Cura",        bonus_hp=5),
]
LOOT_GOLEM = [
    Item("Fragmento de Pedra", bonus_hp=4),
    Item("Núcleo de Pedra",    bonus_atk=2),
]
LOOT_NOSFERATU = [
    Item("Sangue Vital",     bonus_hp=6),
    Item("Essência Sombria", bonus_atk=2),
]
LOOT_BANSHEE = [
    Item("Eco da Banshee",      bonus_esq=0.08),
    Item("Grito Cristalizado",  bonus_atk=1),
]
LOOT_HORDA = [
    Item("Bolsa de Moedas Goblin", bonus_hp=2),
    Item("Adaga Enferrujada",      bonus_atk=1),
]

class Inimigo(Entidade):
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
        tipo_especial: Optional[str] = None,
        chance_miss: float = 0.10,
        chance_drop: float = 0.10,
        chance_veneno: float = 0.0,
        chance_fraqueza: float = 0.0,
        chance_esquiva_debuff: float = 0.0,
        esquiva: float = 0.0
    ) -> None:
        # Base (Entidade): valida nome/hp e define nome, hp_max e hp.
        super().__init__(nome, hp)
        if atk <= 0:
            raise ValueError()
        if dificuldade < 1:
            raise ValueError()
        if xp < 0:
            raise ValueError()
        if moedas < 0:
            raise ValueError()
        if not (0.0 <= cura_percentual <= 1.0):
            raise ValueError()
        if absorcao_dano < 0:
            raise ValueError()
        if bonus_atk_por_turno < 0:
            raise ValueError()
        if not (0.0 <= chance_atordoar <= 1.0):
            raise ValueError()
        if not (0.0 <= chance_veneno <= 1.0):
            raise ValueError()
        if not (0.0 <= chance_fraqueza <= 1.0):
            raise ValueError()
        if not (0.0 <= chance_esquiva_debuff <= 1.0):
            raise ValueError()
        if not (0.0 <= esquiva <= 1.0):
            raise ValueError()

        self.atk = atk
        self.dificuldade = dificuldade
        self.xp = xp
        self.moedas = moedas
        self.modificador_fuga = modificador_fuga
        self.cura_percentual = cura_percentual
        self.absorcao_dano = absorcao_dano
        self.bonus_atk_por_turno = bonus_atk_por_turno
        self.chance_atordoar = chance_atordoar
        self.tipo_especial = tipo_especial
        self.chance_miss = chance_miss
        self.chance_drop = chance_drop
        self.chance_veneno = chance_veneno
        self.chance_fraqueza = chance_fraqueza
        self.chance_esquiva_debuff = chance_esquiva_debuff
        self.esquiva = esquiva

    # esta_vivo() e curar() são herdados de Entidade.

    def receber_dano(self, dano: int) -> int:
        """
        Override (Polimorfismo): o Inimigo desconta a armadura (absorcao_dano)
        antes de aplicar o dano — diferente do Jogador, que sofre direto.
        """
        if dano < 0:
            raise ValueError()
        dano_apos_absorcao = max(0, dano - self.absorcao_dano)
        dano_efetivo = min(dano_apos_absorcao, self.hp)
        self.hp -= dano_efetivo
        return dano_efetivo

    def tentar_esquivar(self) -> bool:
        """
        True se o inimigo DESVIAR do golpe do jogador neste turno (Lote 2).
        Curto-circuito: se esquiva==0 nem consome a sorte.
        """
        return self.esquiva > 0 and random.random() < self.esquiva

    def atacar(self, alvo) -> dict:
        """
        Executa UM turno de ataque deste inimigo contra um alvo.

        Encapsulamento (slide "Encapsulamento") + Abstração: o inimigo é o
        DONO das suas próprias mecânicas de turno — escalada de ATK, erro
        (chance_miss), roubo de vida (cura_percentual) e atordoamento
        (chance_atordoar). Antes, cada laço de combate (automático, CLI e API)
        repetia esta mesma sequência de regras com getattr(...) defensivo;
        agora todos chamam inimigo.atacar(alvo) e recebem um relatório.

        Polimorfismo: a mesma chamada serve para qualquer subclasse — Nosferatu
        rouba vida, Banshee atordoa, comum só bate — porque o comportamento é
        guiado pelos atributos da instância, sem if por tipo concreto.

        O método NÃO decide nada sobre o estado externo (atordoamento do
        jogador, logs da tela): apenas aplica o efeito no próprio inimigo e no
        alvo, e REPORTA o que aconteceu para o chamador agir.

        Parâmetros:
            alvo: entidade atacada (Jogador). Precisa expor receber_dano(int).

        Retorna:
            dict: {
                "dano":      int  — dano efetivo causado ao alvo (0 se errou),
                "errou":     bool — True se o ataque errou (chance_miss),
                "curou":     int  — HP recuperado por roubo de vida (lifesteal),
                "atordoou":  bool — True se atordoou o alvo neste turno,
                "envenenou": bool — True se aplicou veneno no alvo neste turno,
                "subiu_atk": int  — quanto o ATK escalou neste turno (0 se nada),
            }

        Levanta:
            ValueError: Se alvo for None.
        """
        if alvo is None:
            raise ValueError("Alvo do ataque não pode ser None.")

        # Inimigos que ficam mais fortes a cada turno (ex.: futuros "enrage").
        subiu_atk = self.bonus_atk_por_turno
        if subiu_atk > 0:
            self.atk += subiu_atk

        # Erro: alguns tipos erram muito (Horda) ou quase nunca (Banshee).
        if random.random() < self.chance_miss:
            return {"dano": 0, "errou": True, "curou": 0, "atordoou": False,
                    "envenenou": False, "fraqueza": False, "esquiva_reduzida": False,
                    "subiu_atk": subiu_atk}

        dano = alvo.receber_dano(self.atk)

        # Roubo de vida (Nosferatu): recupera parte do dano causado.
        curou = 0
        if self.cura_percentual > 0 and dano > 0:
            curou = self.curar(max(1, int(dano * self.cura_percentual)))

        # Atordoamento (Banshee): chance de o alvo perder o próximo turno.
        atordoou = self.chance_atordoar > 0 and random.random() < self.chance_atordoar

        # Debuffs por acerto — só REPORTAMOS; o laço de combate aplica o efeito
        # no jogador (mesmo padrão do veneno):
        #   veneno (Goblin/Rato), fraqueza (Orc), esquiva reduzida (Troll).
        envenenou        = self.chance_veneno > 0 and dano > 0 and random.random() < self.chance_veneno
        fraqueza         = self.chance_fraqueza > 0 and dano > 0 and random.random() < self.chance_fraqueza
        esquiva_reduzida = self.chance_esquiva_debuff > 0 and dano > 0 and random.random() < self.chance_esquiva_debuff

        return {"dano": dano, "errou": False, "curou": curou,
                "atordoou": atordoou, "envenenou": envenenou,
                "fraqueza": fraqueza, "esquiva_reduzida": esquiva_reduzida,
                "subiu_atk": subiu_atk}

    def tabela_loot(self) -> list:
        """
        Pool de itens que este inimigo pode dropar.

        Polimorfismo (slide "Polimorfismo"): a base devolve o pool padrão; cada
        subclasse especial SOBRESCREVE este método com o seu pool temático.
        Quem rola o loot chama inimigo.tabela_loot() sem saber o tipo concreto.
        """
        return LOOT_PADRAO

    @staticmethod
    def gerar(andar: int = 1) -> "Inimigo":
        if andar < 1:
            raise ValueError()

        if random.random() < 0.10:
            return HordaDeGoblins()

        # Bônus de escala por andar (balanceamento v4)
        bonus_hp     = round(andar * ESCALA_HP_POR_ANDAR)
        bonus_atk    = andar // ESCALA_ATK_DIVISOR
        bonus_moedas = andar // ESCALA_MOEDAS_DIVISOR

        if andar >= 5 and random.random() < chance_elite(andar):
            # Thresholds antecipados (Lote C): os especiais aparecem mais cedo,
            # quando o herói ainda é vulnerável. A chance de entrar aqui (e de
            # virar um especial) cresce com o andar a partir do 6 — ver
            # chance_elite()/ratio_especial().
            pool_especiais = []
            if andar >= 5:
                pool_especiais.append(GolemDePedra)
            if andar >= 8:
                pool_especiais.append(Nosferatu)
            if andar >= 10:
                pool_especiais.append(Banshee)

            if pool_especiais and random.random() < ratio_especial(andar):
                classe_escolhida = random.choice(pool_especiais)
                return classe_escolhida()

            # Elite (dif 2) — stats escalam com o andar. Orc e Troll têm
            # identidade própria (Lote 2): viram subclasses; Esqueleto é genérico.
            nome = random.choice(NOMES_DIFICULDADE_2)
            hp = random.randint(8, 15) + round(bonus_hp * ELITE_HP_MULTIPLICADOR)
            atk = random.randint(3, 5) + bonus_atk + 1
            xp = random.randint(25, 50)
            moedas = random.randint(5, 10) + bonus_moedas
            if nome == "Orc":
                return Orc(hp, atk, xp, moedas)
            if nome == "Troll das Cavernas":
                return TrollDasCavernas(hp, atk, xp, moedas)
            return Inimigo(nome, hp, atk, 2, xp, moedas)   # Esqueleto Guerreiro

        # Comum (dif 1) — escala por andar.
        nome = random.choice(NOMES_DIFICULDADE_1)
        hp = random.randint(3, 8) + bonus_hp
        atk = random.randint(1, 3) + bonus_atk
        xp = random.randint(10, 20)
        moedas = random.randint(0, 4) + bonus_moedas
        # Veneno (Lote M): apenas Goblin e Rato Gigante podem envenenar.
        chance_veneno = CHANCE_VENENO if nome in NOMES_PODEM_ENVENENAR else 0.0
        return Inimigo(nome, hp, atk, 1, xp, moedas, chance_veneno=chance_veneno)

    def __repr__(self) -> str:
        return (
            f"Inimigo(nome={self.nome!r}, hp={self.hp}/{self.hp_max}, "
            f"atk={self.atk}, dificuldade={self.dificuldade}, xp={self.xp})"
        )

class Nosferatu(Inimigo):
    # Antigo "Vampiro das Sombras" (renomeado no Lote B). Mantém a mecânica de
    # regeneração ao causar dano. Herda de Inimigo e especializa o construtor.
    def __init__(self) -> None:
        super().__init__(
            nome="Nosferatu",
            hp=random.randint(12, 18),
            atk=random.randint(4, 6),
            dificuldade=2,
            xp=45,
            moedas=random.randint(10, 15),
            modificador_fuga=-0.10,
            cura_percentual=0.20,
            tipo_especial="nosferatu",
            chance_miss=0.05,
            chance_drop=0.22
        )

    def tabela_loot(self) -> list:   # Polimorfismo: sobrescreve o pool padrão
        return LOOT_NOSFERATU

class GolemDePedra(Inimigo):
    def __init__(self) -> None:
        super().__init__(
            nome="Golem de Pedra",
            hp=random.randint(15, 22),
            atk=random.randint(3, 5),
            dificuldade=2,
            xp=50,
            moedas=random.randint(10, 15),
            modificador_fuga=0.40,
            absorcao_dano=3,          # Lote C: defesa maior (era 2)
            tipo_especial="golem",
            chance_miss=0.10,
            chance_drop=0.20
        )

    def tabela_loot(self) -> list:
        return LOOT_GOLEM

class HordaDeGoblins(Inimigo):
    def __init__(self) -> None:
        super().__init__(
            nome="Horda de Goblins",
            hp=random.randint(9, 12),
            atk=random.randint(1, 2),
            dificuldade=1,
            xp=20,
            moedas=random.randint(5, 10),
            modificador_fuga=0.20,
            tipo_especial="horda",
            chance_miss=0.20,
            chance_drop=0.12
        )

    def tabela_loot(self) -> list:
        return LOOT_HORDA

class Banshee(Inimigo):
    def __init__(self) -> None:
        super().__init__(
            nome="Banshee",
            hp=random.randint(10, 15),
            atk=random.randint(3, 6),
            dificuldade=2,
            xp=55,
            moedas=random.randint(10, 20),
            modificador_fuga=-0.15,
            chance_atordoar=0.30,
            tipo_especial="banshee",
            chance_miss=0.05,
            chance_drop=0.25,
            esquiva=ESQUIVA_BANSHEE,   # Lote 2: fantasma etéreo, difícil de acertar
        )

    def tabela_loot(self) -> list:
        return LOOT_BANSHEE


class Orc(Inimigo):
    """
    Elite "inteligente" (Lote 2): além da Fraqueza (B2), tem uma esquiva moderada
    — desvia de alguns golpes do jogador. Recebe as stats de elite já escaladas
    por andar (via gerar()).
    """
    def __init__(self, hp: int = 12, atk: int = 5, xp: int = 30, moedas: int = 8) -> None:
        super().__init__(
            nome="Orc",
            hp=hp, atk=atk, dificuldade=2, xp=xp, moedas=moedas,
            chance_fraqueza=CHANCE_FRAQUEZA,
            esquiva=ESQUIVA_ORC,
        )


class TrollDasCavernas(Inimigo):
    """
    Elite tanque de HP (Lote 2): tem MUITO mais vida que os outros, mas SEM
    armadura (diferente do Golem, que mitiga por absorção). Aguenta dano
    sustentado; cada golpe entra inteiro. Mantém o debuff de esquiva (maça, B2).
    """
    def __init__(self, hp: int = 14, atk: int = 5, xp: int = 30, moedas: int = 8) -> None:
        super().__init__(
            nome="Troll das Cavernas",
            hp=round(hp * TROLL_HP_MULTIPLICADOR), atk=atk, dificuldade=2,
            xp=xp, moedas=moedas,
            chance_esquiva_debuff=CHANCE_ESQUIVA_DEBUFF,
            absorcao_dano=0,   # sem armadura — é tanque por bolha de HP
        )


# ── Bando de Goblins: combate sequencial (Lote E) ─────────────────────────────

class Goblin(Inimigo):
    """
    Um goblin individual de um Bando.

    Herança (slide "Herança"): É UM Inimigo — herda combate, dano, cura etc.,
    e usa super().__init__ para reaproveitar a construção.
    Polimorfismo: sobrescreve tabela_loot() para dropar o pool da horda.
    """
    def __init__(self, nome: str, hp: int, atk: int, xp: int, moedas: int) -> None:
        super().__init__(
            nome=nome,
            hp=hp,
            atk=atk,
            dificuldade=1,
            xp=xp,
            moedas=moedas,
            modificador_fuga=0.20,
            tipo_especial="horda",
            chance_miss=0.15,
            chance_drop=0.12,
        )

    def tabela_loot(self) -> list:
        return LOOT_HORDA


class BandoDeGoblins:
    """
    Um bando enfrentado em sequência (3 goblins IDÊNTICOS, um de cada vez).

    Composição (slide "Composição vs Herança"): um Bando NÃO é um Inimigo —
    ele TEM vários Goblins (relação "tem um"). O combate continua consumindo
    UM Inimigo por vez; a fila de goblins é estado da sessão.

    Os 3 goblins são iguais entre si (mesmo nome, mesmas stats) — no frontend
    usam um único sprite "Goblin". Stats próximas às de um goblin comum.
    """
    TAMANHO = 3

    def __init__(self) -> None:
        # Rola as stats UMA vez e aplica aos 3 → goblins idênticos.
        hp     = random.randint(4, 7)
        atk    = random.randint(1, 2)
        xp     = random.randint(8, 12)
        moedas = random.randint(2, 4)
        # Cada goblin se identifica como "Bando de Goblins" (nome distinto do
        # goblin comum) — assim o jogador sabe que é a horda sequencial.
        self.goblins = [
            Goblin("Bando de Goblins", hp=hp, atk=atk, xp=xp, moedas=moedas)
            for _ in range(self.TAMANHO)
        ]

    def fila(self) -> list:
        """Devolve a fila de goblins (cópia), na ordem em que serão enfrentados."""
        return list(self.goblins)