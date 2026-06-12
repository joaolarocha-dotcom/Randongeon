# randongeon/jogo/sistemas/masmorra.py

"""
Módulo responsável pelo sistema central da masmorra.

v3.1 — Mecânica de miss + sistema de loot.

Mudanças v3:
  - resolver_combate(): processa mecânicas especiais (Vampiro, Caçador, Banshee).
  - tentar_fuga(inimigo=None): modificador de fuga por tipo.

Mudanças v3.1:
  - CHANCE_MISS_JOGADOR: constante de chance de erro do jogador (10%).
  - _rolar_miss(): rola miss para jogador ou inimigo antes de aplicar dano.
  - _rolar_loot(): rola chance de drop de item ao derrotar inimigo.
  - POOL_LOOT: itens simples que podem ser dropados por inimigos.
    Poções menores — não requer sala de baú nem mercador.

Lote 1:
  - NOMES_BOSS extraído para constante de módulo (testável externamente).
  - __init__: aceita andar_max opcional para Modo Campanha.
"""

import random
import time
from typing import Optional

from jogo.entidades.jogador import Jogador
from jogo.entidades.inimigo import Inimigo
from jogo.entidades.item    import Item
from jogo.sistemas.gerador  import GeradorSala
from jogo.entidades.loja    import Loja


# ── Constantes ────────────────────────────────────────────────────────────────

CHANCE_FUGA          = 0.5
BOSS_A_CADA_ANDARES  = 5
CHANCE_MISS_JOGADOR  = 0.10   # v3.1: 10% base de errar ataque

# Pool de itens simples que inimigos podem dropar ao morrer.
# Poções menores — recompensa pequena sem depender de baús ou mercador.
POOL_LOOT = [
    Item("Poção Menor de Cura",    bonus_hp=3),
    Item("Erva Medicinal",          bonus_hp=2),
    Item("Fragmento de Cristal",   bonus_atk=1),
    Item("Pó de Velocidade",       bonus_esq=0.03),
    Item("Poção de Cura",          bonus_hp=5),
]

# Nomes temáticos de boss por andar (extraído para módulo no Lote 1).
NOMES_BOSS = {
    5:  "Yalergurath",
    10: "Yalergurath",
    15: "Yalergurath",
    20: "Yalergurath",
}

LORE = [
    "Ninguém sabe quando ela surgiu,",
    "do nada no mundo, um abismo se abriu.",
    "",
    "Uns dizem: foi obra de antiga ambição,",
    "outros: sempre existiu, além da razão.",
    "",
    "Chamam-na de Masmorra Sem Fim,",
    "onde poucos voltaram para contar o que viram ali.",
    "",
    "A entrada rasgou o chão sem aviso,",
    "um convite sombrio, um estranho paraíso.",
    "",
    "Muitos entraram buscando poder,",
    "mas poucos viveram pra sobreviver.",
    "",
    "Os que voltaram não falam de ouro,",
    "mas de horrores guardados no escuro tesouro.",
    "",
    "Corredores mudam, sem explicação,",
    "criaturas surgem da própria escuridão.",
    "",
    "Sussurros te chamam, parecem te conhecer,",
    "como se a masmorra pudesse te ver.",
    "",
    "Mas algo te trouxe, não foi por acaso,",
    "talvez redenção… ou poder em atraso.",
    "",
    "Ao cruzar a entrada, você sente o olhar,",
    "algo lá dentro começou a te notar.",
    "",
    "E no fundo eterno, além da razão…",
    "algo te espera na escuridão.",
]


# ── Auxiliares do módulo ──────────────────────────────────────────────────────

def _indicador_especial(inimigo: Inimigo) -> str:
    """
    Retorna string de indicador visual para o tipo especial do inimigo.
    Exibida ao lado do nome durante o combate interativo.
    """
    indicadores = {
        "vampiro": " 🩸 [Regeneração 20%]",
        "golem":   " 🪨 [Armadura: 2]",
        "cacador": " ⚔️  [ATK +1/turno]",
        "horda":   " 👹 [Horda]",
        "banshee": " 💀 [Atordoamento 30%]",
    }
    tipo = getattr(inimigo, 'tipo_especial', None)
    return indicadores.get(tipo, "")


def _imprimir_dano_jogador(atk_jogador: int, dano_efetivo: int, inimigo: Inimigo) -> None:
    """
    Imprime a mensagem de dano causado pelo jogador.
    Informa a absorção de armadura do Golem quando aplicável.
    """
    absorcao = getattr(inimigo, 'absorcao_dano', 0)
    if absorcao > 0 and dano_efetivo < atk_jogador:
        absorvido = atk_jogador - dano_efetivo
        print(f"Você causou {dano_efetivo} de dano. (Armadura absorveu {absorvido})\n")
    else:
        print(f"Você causou {dano_efetivo} de dano.\n")


# ── Classe Masmorra ───────────────────────────────────────────────────────────

class Masmorra:
    """
    Orquestra o estado e o fluxo completo de uma run da masmorra.

    Responsabilidades:
      - Manter estado da run (andar, desistiu, jogador).
      - Delegar geração de salas ao GeradorSala.
      - Executar lógica pura de combate via resolver_combate().
      - Expor métodos de apresentação (prints) separados da lógica.

    Atributos:
        jogador   (Jogador):     Personagem controlado pelo jogador.
        gerador   (GeradorSala): Responsável por gerar salas.
        andar     (int):         Andar atual da masmorra.
        desistiu  (bool):        True se o jogador optou por desistir.
        andar_max (int|None):    Andar máximo para Modo Campanha; None = infinito.
    """

    def __init__(
        self,
        jogador: Jogador,
        gerador: GeradorSala = None,
        andar_max: Optional[int] = None,   # Lote 1: Modo Campanha
    ) -> None:
        self.jogador   = jogador
        self.gerador   = gerador if gerador is not None else GeradorSala()
        self.andar     = 0
        self.desistiu  = False
        self.andar_max = andar_max   # Lote 1: None = modo infinito

    # ── Lógica pura (testável) ─────────────────────────────────────────────────

    def resolver_combate(self, inimigo: Inimigo) -> str:
        """
        Executa combate completo sem I/O.

        Mecânicas especiais:
          - Golem de Pedra:      absorção ocorre em inimigo.receber_dano().
          - Caçador Sombrio:     ganha bonus_atk_por_turno antes de cada ataque.
          - Vampiro das Sombras: cura cura_percentual do dano causado.
          - Banshee:             chance_atordoar de pular o próximo ataque do jogador.

        Retorna:
            str: 'vitoria' ou 'derrota'.

        Levanta:
            ValueError: Se inimigo for None.
        """
        if inimigo is None:
            raise ValueError("Inimigo não pode ser None.")

        jogador_atordoado = False

        while self.jogador.esta_vivo() and inimigo.esta_vivo():

            # ── Fase do Jogador ──────────────────────────────────────────────
            if not jogador_atordoado:
                if not random.random() < CHANCE_MISS_JOGADOR:
                    inimigo.receber_dano(self.jogador.atk)
                # se miss do jogador: nenhum dano neste turno
            else:
                jogador_atordoado = False   # consome atordoamento

            # ── Fase do Inimigo (apenas se ainda vivo) ───────────────────────
            if inimigo.esta_vivo():

                # Caçador Sombrio: escala ATK antes de atacar
                if inimigo.bonus_atk_por_turno > 0:
                    inimigo.atk += inimigo.bonus_atk_por_turno

                # Miss do inimigo
                if not random.random() < inimigo.chance_miss:
                    dano_causado = self.jogador.receber_dano(inimigo.atk)
                else:
                    dano_causado = 0   # inimigo errou

                # Vampiro das Sombras: cura % do dano causado
                if inimigo.cura_percentual > 0 and dano_causado > 0:
                    cura = max(1, int(dano_causado * inimigo.cura_percentual))
                    inimigo.curar(cura)

                # Banshee: atordoa o jogador no próximo turno
                if inimigo.chance_atordoar > 0:
                    if random.random() < inimigo.chance_atordoar:
                        jogador_atordoado = True

        if not self.jogador.esta_vivo():
            return "derrota"

        self.jogador.ganhar_xp(inimigo.xp)
        self.jogador.ganhar_moedas(inimigo.moedas)
        loot = self._rolar_loot(inimigo)
        if loot:
            self.aplicar_item(loot)
        return "vitoria"

    def tentar_fuga(self, inimigo: Inimigo = None) -> bool:
        """
        Simula tentativa de fuga do combate.

        Chance base: CHANCE_FUGA (50%).
        Modificadores por tipo:
          Horda de Goblins:    +0.20 → 70%
          Comum (dif 1):       +0.10 → 60%
          Elite comum (dif 2): -0.05 → 45%
          Golem de Pedra:      -0.05 → 45%
          Caçador Sombrio:     +0.05 → 55%
          Vampiro das Sombras: -0.10 → 40%
          Banshee:             -0.15 → 35%

        Limites: mínimo 5%, máximo 90%.

        Parâmetros:
            inimigo (Inimigo | None): Se None, usa CHANCE_FUGA pura.

        Retorna:
            bool: True se a fuga foi bem-sucedida.
        """
        chance = CHANCE_FUGA
        if inimigo is not None:
            modificador = getattr(inimigo, 'modificador_fuga', 0.0)
            chance      = max(0.05, min(0.90, CHANCE_FUGA + modificador))
        return random.random() < chance

    def e_andar_de_boss(self) -> bool:
        """Retorna True se o andar atual é múltiplo de BOSS_A_CADA_ANDARES."""
        return self.andar > 0 and self.andar % BOSS_A_CADA_ANDARES == 0

    def gerar_boss(self) -> Inimigo:
        """
        Cria um boss escalado ao andar atual.

        Patch v3 — balanceamento revisado:
          Fórmulas antigas eram muito lineares e suaves — boss do andar 10
          tinha HP=40 e ATK=9, fraco demais para um jogador com itens acumulados.

          Novo escalonamento (fator = andar // 5):
            HP     = 40 + (fator * 18)   → andares  5/10/15/20: 58 / 76 / 94 / 112
            ATK    =  8 + (fator *  3)   → andares  5/10/15/20: 11 / 14 / 17 / 20
            XP     = 80 + (fator * 40)   → andares  5/10/15/20: 120/ 160/ 200/ 240
            moedas = 25 + (fator *  8)   → andares  5/10/15/20: 33 / 41 / 49 / 57

          Nomes temáticos por nível de boss (ver constante NOMES_BOSS).
        """
        fator  = self.andar // BOSS_A_CADA_ANDARES
        hp     = 40 + (fator * 18)
        atk    =  8 + (fator *  3)
        xp     = 80 + (fator * 40)
        moedas = 25 + (fator *  8)
        nome   = NOMES_BOSS.get(self.andar, "Yalergurath")

        return Inimigo(nome, hp=hp, atk=atk, dificuldade=3, xp=xp, moedas=moedas)

    def gerar_mimico(self) -> Inimigo:
        """
        Cria um Mímico com atributos fixos.

        Patch v3: HP aumentado de 10→14, ATK de 3→4.
        Mímicos devem ser uma surpresa desafiadora, não um inimigo trivial.
        XP e moedas mantidos altos para recompensar o susto.
        """
        return Inimigo("Mímico", hp=14, atk=4, dificuldade=2, xp=40, moedas=10)

    def aplicar_item(self, item: Item) -> dict:
        """
        Aplica item no jogador desta masmorra.

        Levanta:
            ValueError: Se item for None.
        """
        if item is None:
            raise ValueError("Item não pode ser None.")
        return item.usar(self.jogador)

    def _rolar_loot(self, inimigo: Inimigo):
        """
        Rola a chance de drop de item ao derrotar um inimigo.

        Chance base definida em inimigo.chance_drop:
          - Comuns dif 1:  8%
          - Elites dif 2: 18-25% (varia por tipo especial)
          - Bosses dif 3: 50% (garantia de recompensa maior)
          - Horda:        12%

        Se o drop acontece, retorna um Item aleatório do POOL_LOOT.
        Se não, retorna None — e a chamada no resolver_combate é segura.

        O item NÃO é aplicado aqui. Quem chama decide se aplica
        (resolver_combate aplica; api/main.py aplica e inclui no response).

        Retorna:
            Item | None
        """
        # Bosses têm chance maior independente do atributo
        chance = 0.50 if inimigo.dificuldade == 3 else inimigo.chance_drop
        if random.random() < chance:
            return random.choice(POOL_LOOT)
        return None

    # ── Apresentação (não testada unitariamente) ───────────────────────────────

    def mostrar_lore(self) -> None:
        """Exibe o texto de lore de introdução."""
        introducao = input("Gostaria de ouvir uma história? [y/n]\n")
        if introducao.lower() == "n":
            print("\n")
            return
        for linha in LORE:
            print(linha)
            time.sleep(0.75)
        print("\n" * 2)

    def mostrar_status(self) -> None:
        """Exibe o status atual do jogador no terminal."""
        print("─" * 40)
        print("STATUS\n")
        print(f"Nome:   {self.jogador.nome}")
        print(f"HP:     {self.jogador.hp} / {self.jogador.hp_max}")
        print(f"ATK:    {self.jogador.atk}")
        print(f"ESQ:    {self.jogador.esq * 100:.0f}%")
        print(f"XP:     {self.jogador.xp}")
        print(f"Moedas: {self.jogador.moedas}")
        print(f"Andar:  {self.andar}")
        print("─" * 40 + "\n")

    def menu(self) -> str:
        """Exibe menu principal e captura escolha do jogador."""
        print("\n─" * 20)
        print("O QUE DESEJA FAZER?\n")
        time.sleep(0.1)
        print("1 - Avançar")
        print("2 - Ver status")
        print("3 - Desistir\n")
        return input("> ")

    def _combate_interativo(self, inimigo: Inimigo) -> str:
        """
        Executa combate com input do jogador a cada turno.

        Exibe indicadores visuais do tipo especial e processa todas as
        mecânicas com mensagens narrativas.

        Retorna:
            str: 'vitoria', 'derrota' ou 'fuga'.
        """
        jogador_atordoado = False

        while self.jogador.esta_vivo() and inimigo.esta_vivo():

            # ── Cabeçalho do turno ────────────────────────────────────────────
            print("\n" + "─" * 40)
            indicador = _indicador_especial(inimigo)
            print(f"{inimigo.nome}{indicador}")
            print(f"  HP: {inimigo.hp}/{inimigo.hp_max}  |  ATK: {inimigo.atk}")
            print(f"\nSeu HP: {self.jogador.hp}/{self.jogador.hp_max}\n")

            # ── Fase do Jogador ───────────────────────────────────────────────
            if jogador_atordoado:
                print("⚡ Você está ATORDOADO e perde seu ataque neste turno!\n")
                time.sleep(0.5)
                jogador_atordoado = False
                # Não mostra o menu; o inimigo ainda ataca abaixo

            else:
                print("1 - Atacar")
                print("2 - Esquivar e Atacar")
                print("3 - Fugir\n")

                acao = input("> ").strip()
                print()

                if acao == "1":
                    dano = inimigo.receber_dano(self.jogador.atk)
                    _imprimir_dano_jogador(self.jogador.atk, dano, inimigo)
                    time.sleep(0.2)

                elif acao == "2":
                    print("Você tenta se esquivar e contra-atacar...\n")
                    time.sleep(0.2)

                    if random.random() <= self.jogador.esq:
                        dano = inimigo.receber_dano(self.jogador.atk)
                        _imprimir_dano_jogador(self.jogador.atk, dano, inimigo)
                        print("Esquiva bem-sucedida! Não foi atingido.\n")
                        time.sleep(0.2)
                        continue   # dodge de sucesso: inimigo NÃO ataca

                    else:
                        dano_dobrado = self.jogador.receber_dano(inimigo.atk * 2)
                        print(
                            f"Esquiva falhou! {inimigo.nome} causou "
                            f"{dano_dobrado} de dano (dobrado).\n"
                        )
                        time.sleep(0.2)

                        # Mecânicas especiais do ataque dobrado
                        if inimigo.cura_percentual > 0 and dano_dobrado > 0:
                            cura = max(1, int(dano_dobrado * inimigo.cura_percentual))
                            inimigo.curar(cura)
                            print(
                                f"O Vampiro das Sombras absorveu sua energia "
                                f"vital e se curou em {cura} HP! "
                                f"(HP: {inimigo.hp}/{inimigo.hp_max})\n"
                            )
                            time.sleep(0.3)
                        continue   # evita o bloco de fase do inimigo abaixo

                elif acao == "3":
                    modificador  = getattr(inimigo, 'modificador_fuga', 0.0)
                    chance_real  = max(0.05, min(0.90, CHANCE_FUGA + modificador))
                    print(f"Tentando fugir... (chance: {int(chance_real * 100)}%)\n")
                    time.sleep(0.2)

                    if self.tentar_fuga(inimigo):
                        print("Você fugiu da batalha!\n")
                        time.sleep(0.2)
                        return "fuga"
                    else:
                        dano_fuga = self.jogador.receber_dano(inimigo.atk)
                        print(
                            f"Fuga falhou! {inimigo.nome} te alcançou "
                            f"e causou {dano_fuga} de dano.\n"
                        )
                        time.sleep(0.2)
                        # segue para fase do inimigo
                else:
                    print("Opção inválida!\n")
                    continue

            # ── Fase do Inimigo ───────────────────────────────────────────────
            if inimigo.esta_vivo():

                # Caçador Sombrio: ATK escala a cada turno
                if inimigo.bonus_atk_por_turno > 0:
                    inimigo.atk += inimigo.bonus_atk_por_turno
                    print(
                        f"O {inimigo.nome} ficou mais forte! "
                        f"ATK aumentou para {inimigo.atk}!\n"
                    )
                    time.sleep(0.3)

                dano_causado = self.jogador.receber_dano(inimigo.atk)
                print(f"{inimigo.nome} causou {dano_causado} de dano em você.\n")
                time.sleep(0.2)

                # Vampiro das Sombras: cura 20% do dano causado
                if inimigo.cura_percentual > 0 and dano_causado > 0:
                    cura = max(1, int(dano_causado * inimigo.cura_percentual))
                    inimigo.curar(cura)
                    print(
                        f"O Vampiro das Sombras absorveu sua energia "
                        f"vital e se curou em {cura} HP! "
                        f"(HP: {inimigo.hp}/{inimigo.hp_max})\n"
                    )
                    time.sleep(0.3)

                # Banshee: chance de atordoar no próximo turno
                if inimigo.chance_atordoar > 0:
                    if random.random() < inimigo.chance_atordoar:
                        jogador_atordoado = True
                        print(
                            "O grito da Banshee ecoa dentro do seu crânio... "
                            "Você será ATORDOADO no próximo turno!\n"
                        )
                        time.sleep(0.4)

        if not self.jogador.esta_vivo():
            return "derrota"

        self.jogador.ganhar_xp(inimigo.xp)
        self.jogador.ganhar_moedas(inimigo.moedas)
        return "vitoria"

    def avancar(self) -> None:
        """
        Avança um andar, gera o conteúdo e o resolve interativamente.
        v3: mensagem diferenciada para a Horda de Goblins.
        """
        self.andar += 1
        print(f"\nVocê avançou para o andar {self.andar}...\n")
        time.sleep(0.25)

        if self.e_andar_de_boss():
            print("⚠️  Um BOSS bloqueia o caminho!\n")
            time.sleep(0.4)
            boss      = self.gerar_boss()
            resultado = self._combate_interativo(boss)

        else:
            tipo, conteudo, descricao = self.gerador.gerar_sala(self.andar)
            print(descricao + "\n")
            time.sleep(0.25)

            if tipo == "loja":
                print("Um mercador encapuzado surge das sombras!")
                mercado = Loja()
                mercado.menu(self.jogador)
                return

            elif tipo == "item":
                bau = input(
                    "Você avista um baú antigo no centro da sala. "
                    "Deseja abri-lo?\n1 - Sim\n2 - Não\n\n> "
                )
                if bau == "1":
                    resultado_item = self.aplicar_item(conteudo)
                    print(f"\nVocê encontrou: {conteudo.nome}!")
                    if "atk" in resultado_item:
                        print(f"  ATK +{resultado_item['atk']}")
                    if "hp" in resultado_item:
                        print(f"  HP  +{resultado_item['hp']}")
                    if "esq" in resultado_item:
                        print(f"  ESQ +{resultado_item['esq'] * 100:.0f}%")
                    print()
                else:
                    print("\nVocê ignorou o baú.\n")
                return

            elif tipo == "inimigo":
                e_especial = random.randint(1, 20)
                if e_especial == 1:
                    bau = input(
                        "Você avista um baú antigo no centro da sala. "
                        "Deseja abri-lo?\n1 - Sim\n2 - Não\n\n> "
                    )
                    if bau == "1":
                        print("\nERA UM MÍMICO DISFARÇADO!!!\n")
                        mimico    = self.gerar_mimico()
                        resultado = self._combate_interativo(mimico)
                    else:
                        return
                else:
                    inimigo = conteudo
                    # Mensagem diferenciada para a Horda
                    if getattr(inimigo, 'tipo_especial', None) == "horda":
                        print(f"Uma {inimigo.nome} irrompeu pela porta!\n")
                    else:
                        print(f"Um {inimigo.nome} apareceu!\n")
                    time.sleep(0.25)
                    resultado = self._combate_interativo(inimigo)

        if 'resultado' in locals():
            if resultado == "vitoria":
                print("Você venceu o combate!\n")
                time.sleep(0.25)
            elif resultado == "derrota":
                print(f"{self.jogador.nome} foi derrotado...\n")
                time.sleep(0.25)
            elif resultado == "fuga":
                print("Você escapou!\n")
                time.sleep(0.25)

    def jogar(self) -> None:
        """Loop principal da run."""
        while self.jogador.esta_vivo() and not self.desistiu:
            escolha = self.menu()
            print()

            if escolha == "3":
                time.sleep(0.25)
                print(f"{self.jogador.nome} desistiu da jornada...\n")
                print(f"XP obtido: {self.jogador.xp}\n")
                self.desistiu = True

            elif escolha == "2":
                time.sleep(0.25)
                self.mostrar_status()

            elif escolha == "1":
                time.sleep(0.25)
                self.avancar()

            else:
                print("Opção inválida!\n")

        if not self.jogador.esta_vivo():
            print(f"\n{self.jogador.nome} foi consumido pela masmorra...\n")
            print(f"XP total obtido: {self.jogador.xp}\n")