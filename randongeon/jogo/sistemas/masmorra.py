import random
import time
from typing import Optional

from jogo.entidades.jogador import Jogador
from jogo.entidades.inimigo import (
    Inimigo, LOOT_PADRAO,
    mensagem_veneno, mensagem_fraqueza, mensagem_esquiva_reduzida,
)
from jogo.entidades.efeitos import Fraqueza, EsquivaReduzida
from jogo.entidades.item    import Item
from jogo.sistemas.gerador  import GeradorSala
from jogo.entidades.loja    import Loja

CHANCE_FUGA                  = 0.5
BOSS_A_CADA_ANDARES          = 5
BOSS_A_CADA_ANDARES_INFINITO = 3
CHANCE_MISS_JOGADOR          = 0.10

# POOL_LOOT mantido por compatibilidade (API e testes importam daqui). A partir
# do Lote C ele é o pool PADRÃO definido em inimigo.py; cada inimigo especial tem
# o seu próprio via inimigo.tabela_loot() (polimorfismo).
POOL_LOOT = LOOT_PADRAO

NOMES_BOSS = {
    5:  "Arauto das Sombras",
    10: "Senhor dos Corredores",
    15: "Ceifador Eterno",
    20: "Coração da Masmorra",
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

def _indicador_especial(inimigo: Inimigo) -> str:
    indicadores = {
        "nosferatu": " 🩸 [Regeneração 20%]",
        "golem":     " 🪨 [Armadura: 2]",
        "horda":     " 👹 [Horda]",
        "banshee":   " 💀 [Atordoamento 30%]",
    }
    tipo = getattr(inimigo, 'tipo_especial', None)
    return indicadores.get(tipo, "")

def _imprimir_dano_jogador(atk_jogador: int, dano_efetivo: int, inimigo: Inimigo) -> None:
    absorcao = getattr(inimigo, 'absorcao_dano', 0)
    if absorcao > 0 and dano_efetivo < atk_jogador:
        absorvido = atk_jogador - dano_efetivo
        print(f"Você causou {dano_efetivo} de dano. (Armadura absorveu {absorvido})\n")
    else:
        print(f"Você causou {dano_efetivo} de dano.\n")

class Masmorra:
    def __init__(
        self,
        jogador: Jogador,
        gerador: GeradorSala = None,
        andar_max: Optional[int] = None,
        modo: str = "story"
    ) -> None:
        if modo not in ("story", "infinite"):
            raise ValueError()
        self.jogador   = jogador
        self.gerador   = gerador if gerador is not None else GeradorSala()
        self.andar     = 0
        self.desistiu  = False
        self.andar_max = andar_max
        self.modo      = modo

    def resolver_combate(self, inimigo: Inimigo) -> str:
        if inimigo is None:
            raise ValueError("Inimigo não pode ser None.")

        jogador_atordoado = False

        while self.jogador.esta_vivo() and inimigo.esta_vivo():
            if not jogador_atordoado:
                if not random.random() < CHANCE_MISS_JOGADOR:
                    if not inimigo.tentar_esquivar():      # Lote 2: inimigo pode desviar
                        dano_base, _ = self.jogador.rolar_dano()
                        inimigo.receber_dano(dano_base)
            else:
                jogador_atordoado = False

            if inimigo.esta_vivo():
                # Efeitos de status (veneno) agem no início da troca (Lote M/B2).
                self.jogador.processar_efeitos_turno()
                if not self.jogador.esta_vivo():
                    break
                # Turno do inimigo: a lógica (miss/lifesteal/atordoar/escala)
                # vive em Inimigo.atacar(). Aqui só reagimos ao relatório.
                relatorio = inimigo.atacar(self.jogador)
                if relatorio["atordoou"]:
                    jogador_atordoado = True
                if relatorio["envenenou"]:
                    self.jogador.envenenar()
                if relatorio.get("fraqueza"):
                    self.jogador.aplicar_efeito(Fraqueza(2))
                if relatorio.get("esquiva_reduzida"):
                    self.jogador.aplicar_efeito(EsquivaReduzida(1))

        if not self.jogador.esta_vivo():
            return "derrota"

        self.jogador.ganhar_xp(inimigo.xp)
        self.jogador.ganhar_moedas(inimigo.moedas)
        loot = self._rolar_loot(inimigo)
        if loot:
            self.aplicar_item(loot)
        return "vitoria"

    def tentar_fuga(self, inimigo: Inimigo = None) -> bool:
        chance = CHANCE_FUGA
        if inimigo is not None:
            modificador = getattr(inimigo, 'modificador_fuga', 0.0)
            chance      = max(0.05, min(0.90, CHANCE_FUGA + modificador))
        return random.random() < chance

    def e_andar_de_boss(self) -> bool:
        if self.modo == "story":
            return self.andar > 0 and self.andar % BOSS_A_CADA_ANDARES == 0
        else:
            return self.andar > 0 and self.andar % BOSS_A_CADA_ANDARES_INFINITO == 0

    def gerar_boss(self) -> Inimigo:
        # Curva progressiva (balance v3.2 — "config I" do simulador Monte Carlo):
        # base baixa para SUAVIZAR o primeiro boss (andar 5) e passo alto para os
        # bosses tardios continuarem ameaçadores. Casa com o sistema de nível do
        # jogador, que faz o herói escalar junto.
        #   andar:   5    10    15    20
        #   HP:     40    60    80   100   (= 20 + fator*20)
        #   ATK:     8    11    14    17   (= 5  + fator*3)
        fator  = self.andar // (BOSS_A_CADA_ANDARES if self.modo == "story" else BOSS_A_CADA_ANDARES_INFINITO)
        hp     = 20 + (fator * 20)
        atk    =  5 + (fator * 3)
        xp     = 80 + (fator * 40)
        moedas = 25 + (fator * 8)
        nome   = NOMES_BOSS.get(self.andar, f"Guardião do Andar {self.andar}")

        return Inimigo(nome, hp=hp, atk=atk, dificuldade=3, xp=xp, moedas=moedas)

    def gerar_mimico(self) -> Inimigo:
        return Inimigo("Mímico", hp=14, atk=4, dificuldade=2, xp=40, moedas=10)

    def aplicar_item(self, item: Item) -> dict:
        if item is None:
            raise ValueError("Item não pode ser None.")
        return item.usar(self.jogador)

    def calcular_score(self) -> int:
        """
        Pontuação total da run (Lote H): pontuação do herói + bônus por andar.

        Combina o estado do jogador (jogador.pontuacao) com o andar alcançado
        — métrica de "quão longe você foi", especialmente no modo infinito.
        Serve de comparativo de competição (placar).
        """
        return self.jogador.pontuacao + self.andar * 100

    def _rolar_loot(self, inimigo: Inimigo):
        chance = 0.50 if inimigo.dificuldade == 3 else getattr(inimigo, 'chance_drop', 0.10)
        if random.random() < chance:
            # Lote C: pool específico do tipo de inimigo (polimorfismo).
            return random.choice(inimigo.tabela_loot())
        return None

    def mostrar_lore(self) -> None:
        introducao = input("Gostaria de ouvir uma história? [y/n]\n")
        if introducao.lower() == "n":
            print("\n")
            return
        for linha in LORE:
            print(linha)
            time.sleep(0.75)
        print("\n" * 2)

    def mostrar_status(self) -> None:
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
        print("\n─" * 20)
        print("O QUE DESEJA FAZER?\n")
        time.sleep(0.1)
        print("1 - Avançar")
        print("2 - Ver status")
        print("3 - Desistir\n")
        return input("> ")

    def _combate_interativo(self, inimigo: Inimigo) -> str:
        jogador_atordoado = False

        while self.jogador.esta_vivo() and inimigo.esta_vivo():
            print("\n" + "─" * 40)
            indicador = _indicador_especial(inimigo)
            print(f"{inimigo.nome}{indicador}")
            print(f"  HP: {inimigo.hp}/{getattr(inimigo, 'hp_max', inimigo.hp)}  |  ATK: {inimigo.atk}")
            print(f"\nSeu HP: {self.jogador.hp}/{self.jogador.hp_max}\n")

            if jogador_atordoado:
                print("⚡ Você está ATORDOADO e perde seu ataque neste turno!\n")
                time.sleep(0.5)
                jogador_atordoado = False
            else:
                print("1 - Atacar")
                print("2 - Esquivar e Atacar")
                print("3 - Fugir\n")

                acao = input("> ").strip()
                print()

                if acao == "1":
                    if inimigo.tentar_esquivar():
                        print(f"{inimigo.nome} desviou do seu golpe!\n")
                        time.sleep(0.2)
                    else:
                        atk, critico = self.jogador.rolar_dano()
                        dano = inimigo.receber_dano(atk)
                        if critico:
                            print("💥 Acerto CRÍTICO!")
                        _imprimir_dano_jogador(atk, dano, inimigo)
                        time.sleep(0.2)

                elif acao == "2":
                    print("Você tenta se esquivar e contra-atacar...\n")
                    time.sleep(0.2)

                    if random.random() <= self.jogador.esquiva_efetiva():
                        if inimigo.tentar_esquivar():
                            print(f"Você esquivou, mas o {inimigo.nome} desviou do seu contra-ataque!\n")
                            time.sleep(0.2)
                            continue
                        atk, critico = self.jogador.rolar_dano()
                        dano = inimigo.receber_dano(atk)
                        if critico:
                            print("💥 Acerto CRÍTICO!")
                        _imprimir_dano_jogador(atk, dano, inimigo)
                        print("Esquiva bem-sucedida! Não foi atingido.\n")
                        time.sleep(0.2)
                        continue

                    else:
                        dano_dobrado = self.jogador.receber_dano(inimigo.atk * 2)
                        print(
                            f"Esquiva falhou! {inimigo.nome} causou "
                            f"{dano_dobrado} de dano (dobrado).\n"
                        )
                        time.sleep(0.2)

                        if getattr(inimigo, 'cura_percentual', 0) > 0 and dano_dobrado > 0:
                            cura = max(1, int(dano_dobrado * inimigo.cura_percentual))
                            inimigo.curar(cura)
                            print(
                                f"O {inimigo.nome} absorveu sua energia "
                                f"vital e se curou em {cura} HP! "
                                f"(HP: {inimigo.hp}/{getattr(inimigo, 'hp_max', inimigo.hp)})\n"
                            )
                            time.sleep(0.3)
                        continue

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
                else:
                    print("Opção inválida!\n")
                    continue

            if inimigo.esta_vivo():
                # Veneno de turnos anteriores age primeiro (Lote M).
                dano_veneno = self.jogador.tick_veneno()
                if dano_veneno > 0:
                    print(
                        f"O veneno corrói {dano_veneno} de vida. "
                        f"(HP: {self.jogador.hp}/{self.jogador.hp_max})\n"
                    )
                    time.sleep(0.2)
                    if not self.jogador.esta_vivo():
                        break

                # Turno do inimigo centralizado em Inimigo.atacar(); aqui só
                # narramos o relatório na tela.
                relatorio = inimigo.atacar(self.jogador)

                if relatorio["subiu_atk"] > 0:
                    print(
                        f"O {inimigo.nome} ficou mais forte! "
                        f"ATK aumentou para {inimigo.atk}!\n"
                    )
                    time.sleep(0.3)

                if relatorio["errou"]:
                    print(f"{inimigo.nome} tentou atacar, mas errou!\n")
                else:
                    print(f"{inimigo.nome} causou {relatorio['dano']} de dano em você.\n")

                time.sleep(0.2)

                if relatorio["curou"] > 0:
                    print(
                        f"O {inimigo.nome} absorveu sua energia "
                        f"vital e se curou em {relatorio['curou']} HP! "
                        f"(HP: {inimigo.hp}/{getattr(inimigo, 'hp_max', inimigo.hp)})\n"
                    )
                    time.sleep(0.3)

                if relatorio["atordoou"]:
                    jogador_atordoado = True
                    print(
                        "O grito da Banshee ecoa dentro do seu crânio... "
                        "Você será ATORDOADO no próximo turno!\n"
                    )
                    time.sleep(0.4)

                if relatorio["envenenou"]:
                    self.jogador.envenenar()
                    print(mensagem_veneno(inimigo.nome) + "\n")
                    time.sleep(0.4)

                if relatorio.get("fraqueza"):
                    self.jogador.aplicar_efeito(Fraqueza(2))
                    print(mensagem_fraqueza(inimigo.nome) + "\n")
                    time.sleep(0.4)

                if relatorio.get("esquiva_reduzida"):
                    self.jogador.aplicar_efeito(EsquivaReduzida(1))
                    print(mensagem_esquiva_reduzida(inimigo.nome) + "\n")
                    time.sleep(0.4)

        if not self.jogador.esta_vivo():
            return "derrota"

        self.jogador.ganhar_xp(inimigo.xp)
        self.jogador.ganhar_moedas(inimigo.moedas)
        return "vitoria"

    def avancar(self) -> None:
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