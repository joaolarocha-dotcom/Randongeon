# randongeon/jogo/sistemas/masmorra.py

"""
Módulo responsável pelo sistema central da masmorra.
A classe Masmorra orquestra o loop do jogo, gerencia o estado da run
e separa completamente a lógica de negócio (testável) da camada de
apresentação (prints, inputs, sleeps).
"""

import random
import time

from jogo.entidades.jogador import Jogador
from jogo.entidades.inimigo import Inimigo
from jogo.entidades.item import Item
from jogo.sistemas.gerador import GeradorSala


# ── Constantes ────────────────────────────────────────────────────────────────

CHANCE_FUGA = 0.5          # 50% de chance de fugir com sucesso
BOSS_A_CADA_ANDARES = 5    # Boss a cada X andares

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



class Masmorra:
    """
    Orquestra o estado e o fluxo completo de uma run da masmorra.

    Responsabilidades desta classe:
      - Manter o estado da run (andar, desistiu, jogador).
      - Delegar a geração de salas ao GeradorSala.
      - Executar a lógica pura de combate via resolver_combate().
      - Expor métodos de apresentação (prints) separados da lógica.

    A separação entre lógica e apresentação é intencional:
    resolver_combate() não chama input() nem print(), permitindo
    que os testes unitários o exercitem sem efeitos colaterais.

    Atributos:
        jogador   (Jogador):     Instância do personagem controlado.
        gerador   (GeradorSala): Responsável por gerar salas.
        andar     (int):         Andar atual da masmorra.
        desistiu  (bool):        True se o jogador optou por desistir.
    """

    def __init__(self, jogador: Jogador, gerador: GeradorSala = None) -> None:
        """
        Inicializa a Masmorra com um jogador e um gerador de salas.

        Parâmetros:
            jogador (Jogador):          Instância do jogador. Pode ser None
                                         inicialmente (definido depois em main.py).
            gerador (GeradorSala|None): Gerador de salas. Se None, um
                                         GeradorSala padrão é criado.
                                         Aceita objetos fake para testes.
        """
        self.jogador  = jogador
        self.gerador  = gerador if gerador is not None else GeradorSala()
        self.andar    = 0
        self.desistiu = False

    # ── Lógica pura (testável) ─────────────────────────────────────────────────

    def resolver_combate(self, inimigo: Inimigo) -> str:
        """
        Executa um combate completo até o fim, sem interação humana.
        Usado internamente pelo loop de apresentação e diretamente pelos testes.

        Regras:
          - A cada turno: jogador ataca primeiro, depois inimigo (se ainda vivo).
          - O combate termina quando hp de um dos lados chega a 0.
          - Se o jogador vencer, o XP do inimigo é concedido.
          - Este método NÃO realiza prints, inputs ou sleeps.

        Parâmetros:
            inimigo (Inimigo): Instância do inimigo a combater.

        Retorna:
            str: 'vitoria' se o jogador derrotou o inimigo,
                 'derrota'  se o jogador morreu durante o combate.

        Levanta:
            ValueError: Se inimigo for None.
        """
        if inimigo is None:
            raise ValueError("Inimigo não pode ser None.")

        while self.jogador.esta_vivo() and inimigo.esta_vivo():
            # Jogador ataca
            inimigo.receber_dano(self.jogador.atk)

            # Inimigo contra-ataca apenas se ainda estiver vivo
            if inimigo.esta_vivo():
                self.jogador.receber_dano(inimigo.atk)

        if not self.jogador.esta_vivo():
            return "derrota"

        self.jogador.ganhar_xp(inimigo.xp)
        return "vitoria"

    def tentar_fuga(self) -> bool:
        """
        Simula uma tentativa de fuga do combate.

        A chance de sucesso é definida pela constante CHANCE_FUGA (50%).

        Retorna:
            bool: True se a fuga foi bem-sucedida, False caso contrário.
        """
        return random.random() < CHANCE_FUGA

    def e_andar_de_boss(self) -> bool:
        """
        Verifica se o andar atual deve conter um boss.

        Um boss aparece a cada BOSS_A_CADA_ANDARES andares (ex: 5, 10, 15...).
        O andar 0 nunca é andar de boss.

        Retorna:
            bool: True se o andar atual é múltiplo de BOSS_A_CADA_ANDARES.
        """
        return self.andar > 0 and self.andar % BOSS_A_CADA_ANDARES == 0

    def gerar_boss(self) -> Inimigo:
        """
        Cria um boss escalado ao andar atual.

        Os atributos do boss são proporcionais ao andar, garantindo
        que bosses mais profundos sejam progressivamente mais difíceis.

        Retorna:
            Inimigo: Instância de boss com dificuldade 3.
        """
        fator  = self.andar // BOSS_A_CADA_ANDARES
        hp     = 20 + (fator * 10)
        atk    = 5  + (fator * 2)
        xp     = 50 + (fator * 25)
        nome   = f"Guardião do Andar {self.andar}"

        return Inimigo(nome, hp=hp, atk=atk, dificuldade=3, xp=xp)

    def aplicar_item(self, item: Item) -> dict:
        """
        Aplica um item no jogador desta masmorra.

        Parâmetros:
            item (Item): Item a ser usado.

        Retorna:
            dict: Resultado retornado por item.usar() com os efeitos aplicados.

        Levanta:
            ValueError: Se item for None.
        """
        if item is None:
            raise ValueError("Item não pode ser None.")
        return item.usar(self.jogador)

    # ── Apresentação (não testada unitariamente) ───────────────────────────────

    def mostrar_lore(self) -> None:
        """Exibe o texto de lore de introdução linha a linha com delay."""
        introducao = input("Gostaria de ouvir uma história? [y/n] \n")
        if introducao.lower() == "y":
            for linha in LORE:
                print(linha)
                time.sleep(0.75)
            print("\n" * 2)
        elif introducao.lower() == "n":
            print("\n")
        else: 
            print("Vou entender como um sim...")
            for linha in LORE:
                print(linha)
                time.sleep(0.75)
            print("\n" * 2)
        
        
        

    def mostrar_status(self) -> None:
        """Exibe o status atual do jogador no terminal."""
        print("--- STATUS ---\n")
        print(f"Nome:  {self.jogador.nome}")
        print(f"HP:    {self.jogador.hp} / {self.jogador.hp_max}")
        print(f"ATK:   {self.jogador.atk}")
        print(f"ESQ:   {self.jogador.esq * 100}%")
        print(f"XP:    {self.jogador.xp}")
        print(f"Andar: {self.andar}\n")

    def menu(self) -> str:
        """
        Exibe o menu principal e captura a escolha do jogador.

        Retorna:
            str: String digitada pelo jogador ('1', '2' ou '3').
        """
        print("\n--- O QUE DESEJA FAZER? ---\n")
        time.sleep(0.1)
        print("1 - Avançar")
        print("2 - Ver status")
        print("3 - Desistir\n")
        return input("> ")

    def _combate_interativo(self, inimigo: Inimigo) -> str:
        """
        Executa o combate com input do jogador a cada turno.
        Utilizado apenas pelo loop jogar() — não é testado unitariamente.

        Ações disponíveis:
            '1' - Atacar
            '2' - Defender (reduz dano do próximo ataque inimigo em 50%)
            '3' - Fugir
            '4' - (reservado para uso de item em versão futura)

        Parâmetros:
            inimigo (Inimigo): Inimigo do combate atual.

        Retorna:
            str: 'vitoria', 'derrota' ou 'fuga'.
        """
        defendendo = False

        while self.jogador.esta_vivo() and inimigo.esta_vivo():
            print("--- COMBATE ---\n")
            print(f"{inimigo.nome} — HP: {inimigo.hp}")
            print(f"Seu HP: {self.jogador.hp}\n")
            print("1 - Atacar")
            print("2 - Esquivar e Atacar")
            print("3 - Fugir\n")

            acao = input("> ")
            print()

            if acao == "1":
                inimigo.receber_dano(self.jogador.atk)
                print(f"Você causou {self.jogador.atk} de dano.\n")
                time.sleep(0.2)

                if inimigo.esta_vivo():
                    self.jogador.receber_dano(inimigo.atk)

            elif acao == "2":
                print("Você tentou se preparou para se esquivar do ataque inimigo e contra-atacar... \n")
                time.sleep(0.2)
                
                if random.random() <= self.jogador.esq:
                    
                    
                    print("E CONSEGUIU!!! \n")
                    time.sleep(0.2)
                    inimigo.receber_dano(self.jogador.atk)
                    self.jogador.receber_dano(0)
                else:
                    print("Mas falhou... \n")
                    time.sleep(0.2)
                    self.jogador.receber_dano(inimigo.atk * 2)
                    print(f"O {inimigo.nome} causou {inimigo.atk * 2} de dano (aumentado).\n")
                    time.sleep(0.2)  
                

                

            elif acao == "3":
                if self.tentar_fuga():
                    print("Você fugiu da batalha!\n")
                    time.sleep(0.2)
                    return "fuga"
                else:
                    print("Fuga falhou! O inimigo te alcançou.\n")
                    self.jogador.receber_dano(inimigo.atk)
                    time.sleep(0.2)
            else:
                print("Opção inválida!\n")

        if not self.jogador.esta_vivo():
            return "derrota"

        self.jogador.ganhar_xp(inimigo.xp)
        return "vitoria"

    def avancar(self) -> None:
        """
        Avança um andar, gera o conteúdo da sala e o resolve interativamente.
        Orquestra apresentação e chamadas à lógica de negócio.
        """
        self.andar += 1
        print(f"\nVocê avançou para o andar {self.andar}...\n")
        time.sleep(0.25)

        # Verifica se é andar de boss
        if self.e_andar_de_boss():
            print("⚠️  Um BOSS bloqueia o caminho!\n")
            time.sleep(0.4)
            boss = self.gerar_boss()
            resultado = self._combate_interativo(boss)
        else:
            tipo, conteudo, descricao = self.gerador.gerar_sala(self.andar)
            print(descricao + "\n")
            time.sleep(0.25)

            if tipo == "item":
                resultado_item = self.aplicar_item(conteudo)
                print(f"Você encontrou: {conteudo.nome}!")
                if "atk" in resultado_item:
                    print(f"  ATK +{resultado_item['atk']}")
                if "hp" in resultado_item:
                    print(f"  HP  +{resultado_item['hp']}")
                print()
                return

            elif tipo == "inimigo":
                inimigo = conteudo
                print(f"Um {inimigo.nome} apareceu!\n")
                time.sleep(0.25)
                resultado = self._combate_interativo(inimigo)

        # Trata o resultado do combate
        if resultado == "vitoria":
            print(f"Você venceu o combate!\n")
            time.sleep(0.25)
        elif resultado == "derrota":
            print(f"{self.jogador.nome} foi derrotado...\n")
            time.sleep(0.25)
        elif resultado == "fuga":
            print("Você escapou!\n")
            time.sleep(0.25)

    def jogar(self) -> None:
        """
        Loop principal da run. Exibe o menu e processa as escolhas do jogador
        até que ele morra ou desista.
        """
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
