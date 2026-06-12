# -*- coding: utf-8 -*-
"""Gera o PDF de estudo de POO (Randongeon x slides do professor)."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted,
    Table, TableStyle, ListFlowable, ListItem, HRFlowable,
)

OUT = r"C:\Users\joaop\OneDrive\Área de Trabalho\Randongeon\Randongeon\docs\Estudo_POO_Randongeon.pdf"

ROXO  = colors.HexColor("#4b2e83")
ROXO2 = colors.HexColor("#6a4caf")
CINZA = colors.HexColor("#f2f0f7")
CODBG = colors.HexColor("#f4f2fb")   # fundo do codigo (claro)
CODFG = colors.HexColor("#242038")   # texto do codigo (escuro, legivel)
CODBD = colors.HexColor("#ccc3e6")   # borda do bloco de codigo
LINHA = colors.HexColor("#d9d3e8")

ss = getSampleStyleSheet()
def style(name, **kw):
    base = kw.pop("parent", ss["Normal"])
    return ParagraphStyle(name, parent=base, **kw)

S_TITLE = style("t", fontName="Helvetica-Bold", fontSize=29, leading=34, textColor=ROXO, alignment=TA_CENTER)
S_SUB   = style("s", fontName="Helvetica", fontSize=13, leading=18, textColor=ROXO2, alignment=TA_CENTER)
S_H1    = style("h1", fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=colors.white,
                backColor=ROXO, borderPadding=(6,8,6,8), spaceBefore=10, spaceAfter=12)
S_H2    = style("h2", fontName="Helvetica-Bold", fontSize=13.5, leading=17, textColor=ROXO, spaceBefore=12, spaceAfter=5)
S_BODY  = style("b", fontName="Helvetica", fontSize=9.7, leading=14, alignment=TA_JUSTIFY, spaceAfter=5)
S_BULL  = style("bl", fontName="Helvetica", fontSize=9.7, leading=13.5)
S_CODE  = style("c", fontName="Courier", fontSize=7.8, leading=10.5, textColor=CODFG)
S_TIP   = style("tip", fontName="Helvetica", fontSize=9.3, leading=13, textColor=colors.HexColor("#1f5132"),
                backColor=colors.HexColor("#e7f5ec"), borderPadding=(6,7,6,7),
                borderColor=colors.HexColor("#7bc99a"), borderWidth=0.7, spaceBefore=4, spaceAfter=8)
S_CELL  = style("cell", fontName="Helvetica", fontSize=8.3, leading=11)
S_CELLB = style("cellb", fontName="Helvetica-Bold", fontSize=8.3, leading=11, textColor=colors.white)
S_NOTE  = style("note", fontName="Helvetica-Oblique", fontSize=8.6, leading=12, textColor=colors.HexColor("#555"))

E = []
def H1(t): E.append(Paragraph(t, S_H1))
def H2(t): E.append(Paragraph(t, S_H2))
def P(t):  E.append(Paragraph(t, S_BODY))
def TIP(t):E.append(Paragraph("<b>Dica:</b> " + t, S_TIP))
def NOTE(t):E.append(Paragraph(t, S_NOTE))
def SP(h=6): E.append(Spacer(1, h))
def CODE(t):
    # Bloco de codigo dentro de uma Table (garante o fundo, que o Preformatted
    # sozinho nao desenhava de forma confiavel). Tema claro = sempre legivel.
    inner = Preformatted(t, S_CODE)
    tbl = Table([[inner]], colWidths=[16.9*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), CODBG),
        ("BOX",        (0,0), (-1,-1), 0.6, CODBD),
        ("LINEBEFORE", (0,0), (-1,-1), 2.2, ROXO2),   # barrinha roxa de destaque
        ("LEFTPADDING",(0,0), (-1,-1), 9),
        ("RIGHTPADDING",(0,0),(-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 7),
        ("BOTTOMPADDING",(0,0),(-1,-1), 7),
    ]))
    E.append(tbl); E.append(Spacer(1, 8))
def BR(): E.append(PageBreak())
def HR(): E.append(HRFlowable(width="100%", thickness=0.6, color=LINHA, spaceBefore=4, spaceAfter=6))
def BULLETS(items):
    E.append(ListFlowable([ListItem(Paragraph(x, S_BULL), leftIndent=10, value="•") for x in items],
                          bulletType="bullet", start="•", leftIndent=12, spaceAfter=6))
def TABLE(rows, widths, header=True):
    data = []
    for r_i, row in enumerate(rows):
        data.append([Paragraph(c, S_CELLB if (header and r_i == 0) else S_CELL) for c in row])
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    cmds = [("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
            ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
            ("LINEBELOW",(0,0),(-1,-1),0.4,LINHA),("BOX",(0,0),(-1,-1),0.5,LINHA)]
    if header:
        cmds += [("BACKGROUND",(0,0),(-1,0),ROXO2),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,CINZA])]
    else:
        cmds += [("ROWBACKGROUNDS",(0,0),(-1,-1),[colors.white,CINZA])]
    t.setStyle(TableStyle(cmds))
    E.append(t); E.append(Spacer(1, 6))

# ============================== CAPA ==============================
E.append(Spacer(1, 4.5*cm))
E.append(Paragraph("Programação Orientada a Objetos", S_TITLE))
SP(6)
E.append(Paragraph("Guia de Estudos com base nos slides do professor", S_SUB))
E.append(Paragraph("e no código do projeto <b>Randongeon</b> (RPG em Python)", S_SUB))
SP(20)
E.append(HRFlowable(width="55%", thickness=1.2, color=ROXO2))
SP(16)
E.append(Paragraph("Os 4 pilares — Encapsulamento, Herança, Polimorfismo e Abstração — explicados, "
                   "com dicas, e comparados com o código real do jogo. Inclui os recursos que o Python "
                   "adiciona e o conteúdo que o projeto usou ALÉM dos slides.",
                   style("capa", parent=S_BODY, alignment=TA_CENTER, fontSize=10.5, textColor=colors.HexColor("#444"))))
SP(30)
E.append(Paragraph("Disciplina: Laboratório de Programação (POO) — UNIT Aracaju", S_SUB))
BR()

# ============================== SUMÁRIO ==============================
H1("Sumário")
TABLE([
    ["Parte", "Conteúdo"],
    ["1", "O que é POO: classes, objetos, __init__/self, atributos de instância vs de classe"],
    ["2", "Os 4 pilares (definição do professor + código do Randongeon + dicas)"],
    ["3", "O que o Python adiciona: @property, duck typing, dunder, @staticmethod/@classmethod, herança múltipla/MRO, composição vs herança"],
    ["4", "Conteúdo ALÉM dos slides: o que o projeto usou que não foi ensinado"],
    ["5", "Crônica do projeto por lote (o que a pasta docs/ aborda)"],
    ["6", "Resumo dos pilares + dicas finais de estudo"],
], [2.0*cm, 14.2*cm])
NOTE("Convenção: trechos de código vêm da pasta randongeon/jogo e api/ do projeto. Onde o código "
     "cita 'slide X', é referência direta ao material da aula.")
BR()

# ============================== PARTE 1 ==============================
H1("Parte 1 — O que é POO")
P("A <b>Programação Orientada a Objetos</b> é um modo de organizar o software em torno de "
  "<b>objetos</b> — entidades que combinam <b>dados</b> (atributos) e <b>comportamentos</b> "
  "(métodos). Contrasta com a programação procedural, focada em sequências de instruções. "
  "Benefícios: reutilização de código, organização, flexibilidade e facilidade de manutenção "
  "(alta coesão, baixo acoplamento).")

H2("Procedural vs Orientado a Objetos")
P("No procedural, os dados andam soltos e as funções os recebem como parâmetro. Na POO, dados "
  "e comportamento ficam <b>juntos</b> dentro da classe:")
CODE('# Procedural                     # Orientado a Objetos\n'
     'nome = "Fusca"                   class Carro:\n'
     'velocidade = 0                       def __init__(self, nome):\n'
     'def acelerar(v, inc):                    self.nome = nome\n'
     '    return v + inc                       self.velocidade = 0\n'
     'velocidade = acelerar(v, 20)         def acelerar(self, inc):\n'
     '                                         self.velocidade += inc')

H2("Classe e Objeto")
P("A <b>classe</b> é o molde (blueprint); o <b>objeto</b> é uma instância concreta criada a "
  "partir dela. Cada objeto tem os seus próprios valores de atributos. No Randongeon, "
  "<font face='Courier'>Jogador</font>, <font face='Courier'>Inimigo</font> e "
  "<font face='Courier'>Item</font> são classes; cada herói/monstro em jogo é um objeto.")

H2("O construtor __init__ e o self")
P("O <font face='Courier'>__init__</font> é chamado automaticamente ao criar o objeto e "
  "inicializa os atributos. O <font face='Courier'>self</font> é sempre o primeiro parâmetro "
  "e representa o próprio objeto (o Python o passa sozinho). Exemplo real do jogo:")
CODE('class Jogador(Entidade):\n'
     '    def __init__(self, nome, hp=20, atk=5, xp=0, esq=0.3, moedas=0):\n'
     '        super().__init__(nome, hp)     # a base valida nome/hp\n'
     '        self.atk    = atk              # atributo de INSTANCIA\n'
     '        self.xp     = xp\n'
     '        self.nivel  = 1\n'
     '        self.esq    = esq')

H2("Atributos de instância vs de classe")
P("<b>Instância</b> (<font face='Courier'>self.attr</font>): único de cada objeto — dados que "
  "variam (hp, atk, xp). <b>Classe</b> (<font face='Courier'>Cls.attr</font>): compartilhado "
  "por todos — ideal para <b>constantes</b>. O Randongeon usa atributos de classe para as "
  "constantes de balanceamento:")
CODE('class Jogador(Entidade):\n'
     '    ATK_POR_NIVEL     = 2      # constantes de CLASSE (valem para todo jogador)\n'
     '    HP_POR_NIVEL      = 12\n'
     '    XP_BASE_NIVEL     = 10\n'
     '    CURA_NIVEL_FRACAO = 0.60\n'
     '    # ... self.hp, self.atk sao de INSTANCIA (variam por objeto)')
TIP("Se o valor é igual para todos os objetos e nunca muda por objeto (uma regra/constante), "
    "ele pertence à CLASSE. Se varia de objeto para objeto (estado), pertence à INSTÂNCIA. "
    "No jogo, isso deixou os números de balanceamento todos juntos e fáceis de calibrar.")
BR()

# ============================== PARTE 2 ==============================
H1("Parte 2 — Os 4 Pilares da POO")
P("Para cada pilar: a <b>definição do professor</b> (slide), <b>como aparece no Randongeon</b> "
  "(com código real) e uma <b>dica</b> de estudo.")

H2("1) Abstração")
P("<b>Professor:</b> ignorar detalhes não relevantes e focar nas características essenciais. "
  "Esconder o COMO e expor o O QUÊ. Em Python usa-se <b>classes abstratas (ABC)</b> com "
  "<font face='Courier'>@abstractmethod</font> para definir um contrato.")
P("<b>No Randongeon:</b> a classe <font face='Courier'>Entidade(ABC)</font> é a base de tudo "
  "que combate. Ela define a interface comum (tem vida, cura, sofre dano) mas <b>não pode ser "
  "instanciada</b> — <font face='Courier'>receber_dano</font> é abstrato, cada filho implementa.")
CODE('from abc import ABC, abstractmethod\n'
     'class Entidade(ABC):                 # abstrata: nao instanciavel\n'
     '    def esta_vivo(self): return self.hp > 0\n'
     '    def curar(self, q): ...          # comportamento COMUM\n'
     '    @abstractmethod\n'
     '    def receber_dano(self, dano):     # CONTRATO: cada subclasse implementa\n'
     '        raise NotImplementedError')
P("Quem combate trata <font face='Courier'>Jogador</font> e <font face='Courier'>Inimigo</font> "
  "uniformemente, \"como Entidades\", sem saber o tipo concreto.")
TIP("Use ABC quando faz sentido ter uma base mas NÃO criar objetos dela, e quando quer obrigar "
    "todas as subclasses a implementar certos métodos. Tentar instanciar uma ABC com método "
    "abstrato gera TypeError — o Python protege o contrato por você.")

H2("2) Encapsulamento")
P("<b>Professor:</b> agrupar dados e métodos numa classe e <b>controlar o acesso</b> aos dados, "
  "protegendo o estado interno. Três níveis: <font face='Courier'>público</font> (acesso livre), "
  "<font face='Courier'>_protegido</font> (convenção, uso interno) e "
  "<font face='Courier'>__privado</font> (name mangling). Mais o <font face='Courier'>@property</font> "
  "(getter/setter com validação).")
P("<b>No Randongeon:</b> usa-se <b>público</b> (<font face='Courier'>self.hp</font>), "
  "<b>_protegido</b> para detalhes internos (<font face='Courier'>_atualizar_nivel</font>, "
  "<font face='Courier'>_rolar_loot</font>, <font face='Courier'>_chance_item</font>) e "
  "<b>@property</b> para valores derivados de leitura:")
CODE('class Jogador(Entidade):\n'
     '    def _atualizar_nivel(self):       # _protegido: detalhe interno, nao e API publica\n'
     '        ...\n'
     '    @property\n'
     '    def pontuacao(self):              # getter calculado (sem expor o calculo)\n'
     '        return self.xp + (self.nivel - 1) * 50 + self.moedas\n\n'
     '    @property\n'
     '    def veneno_turnos(self):          # derivado do efeito ativo (Lote B2)\n'
     '        e = self.buscar_efeito("veneno")\n'
     '        return e.turnos if e else 0')
TIP("@property deixa um método ser lido como se fosse atributo (jogador.pontuacao, sem os "
    "parênteses), mantendo o cálculo escondido e o valor protegido contra escrita externa. "
    "É o jeito Pythônico de fazer getter sem poluir a classe com get_pontuacao().")

H2("3) Herança")
P("<b>Professor:</b> uma classe filha herda atributos e métodos da classe pai, evitando "
  "repetição. Em Python: <font face='Courier'>class Filha(Pai)</font>, e "
  "<font face='Courier'>super()</font> chama o pai. A filha pode <b>sobrescrever</b> métodos.")
P("<b>No Randongeon:</b> a hierarquia é rica. <font face='Courier'>Jogador</font> e "
  "<font face='Courier'>Inimigo</font> herdam de <font face='Courier'>Entidade</font>; e o "
  "<font face='Courier'>Inimigo</font> tem 8 subclasses especializadas:")
CODE('class Nosferatu(Inimigo):              # "e um" Inimigo\n'
     '    def __init__(self, bonus_hp=0, bonus_atk=0):\n'
     '        super().__init__(nome="Nosferatu", cura_percentual=0.20, ...)  # reusa o pai\n'
     '    def tabela_loot(self):              # sobrescreve so o que muda\n'
     '        return LOOT_NOSFERATU')
P("Subclasses: <font face='Courier'>Nosferatu, GolemDePedra, Banshee, Orc, TrollDasCavernas, "
  "HordaDeGoblins, Goblin, CoracaoDaMasmorra</font>. Todas reaproveitam o combate da base via "
  "<font face='Courier'>super()</font>.")
TIP("Herança é a relação \"É UM\": Goblin É UM Inimigo. Se você se pegar copiando código entre "
    "duas classes parecidas, provavelmente existe uma classe-pai esperando para nascer. Mas "
    "cuidado: nem tudo é herança — veja Composição na Parte 3.")

H2("4) Polimorfismo")
P("<b>Professor:</b> \"muitas formas\" — o mesmo método se comporta diferente conforme o tipo "
  "do objeto. Sobrescrita (overriding): a subclasse dá a sua própria versão de um método herdado.")
P("<b>No Randongeon:</b> o caso mais elegante é o combate: um único laço serve a TODOS os "
  "inimigos, sem nenhum <font face='Courier'>if por tipo</font>. O comportamento vem do override "
  "e dos atributos da instância:")
CODE('# Quem rola o loot NAO sabe o tipo concreto do inimigo:\n'
     'item = random.choice(inimigo.tabela_loot())   # cada classe devolve o seu pool\n\n'
     '# receber_dano e polimorfico:\n'
     'class Inimigo(Entidade):\n'
     '    def receber_dano(self, dano):     # desconta armadura\n'
     '        return ... max(0, dano - self.absorcao_dano) ...\n'
     'class Jogador(Entidade):\n'
     '    def receber_dano(self, dano):     # sofre direto\n'
     '        ...')
P("O método <font face='Courier'>Inimigo.atacar(alvo)</font> é o auge: a MESMA chamada faz o "
  "Nosferatu roubar vida, a Banshee atordoar e um goblin só bater — guiado pelos atributos "
  "(<font face='Courier'>cura_percentual</font>, <font face='Courier'>chance_atordoar</font>), "
  "<b>sem if por tipo</b>.")
TIP("O cheiro de código que o polimorfismo elimina é o if/elif por tipo "
    "(if tipo == 'nosferatu': ... elif tipo == 'banshee': ...). Se cada tipo sabe se comportar, "
    "você só chama o método. Adicionar um inimigo novo não mexe no laço de combate — só cria "
    "uma subclasse. Isso é extensibilidade.")
BR()

# ============================== PARTE 3 ==============================
H1("Parte 3 — O que o Python adiciona")
P("O próprio slide final do professor lista: \"Python adiciona herança múltipla, dunder methods, "
  "@property e duck typing\". Veja cada um e onde (ou se) aparece no Randongeon.")

H2("Duck typing")
P("\"Se anda como pato e faz quack, é um pato.\" Em vez de exigir herança, basta o objeto ter o "
  "método/atributo certo. O Randongeon usa o idioma defensivo "
  "<font face='Courier'>getattr(obj, 'attr', padrão)</font>:")
CODE('# Inimigo.atacar: funciona com qualquer "alvo" que exponha o atributo certo\n'
     'miss = self.chance_miss + getattr(alvo, "evasao_passiva", 0.0)\n\n'
     '# Item.usar: so chama curar_veneno se o jogador tiver esse metodo\n'
     'curar = getattr(jogador, "curar_veneno", None)\n'
     'if callable(curar): curar()')
TIP("getattr(obj, nome, padrão) lê um atributo com um valor de reserva se ele não existir. Isso "
    "tolera variações de objeto (até dummies de teste) sem quebrar e sem exigir herança — duck "
    "typing na prática.")

H2("Dunder methods (métodos mágicos)")
P("Métodos com __duplo_underscore__ que o Python chama em certas operações. O slide lista vários "
  "(<font face='Courier'>__init__, __str__, __repr__, __eq__, __lt__, __len__, __add__, "
  "__contains__, __iter__, __getitem__</font>). O Randongeon usa "
  "<font face='Courier'>__init__</font> (em todas as classes) e "
  "<font face='Courier'>__repr__</font> para debug:")
CODE("def __repr__(self):\n"
     "    return (f\"Jogador(nome={self.nome!r}, nivel={self.nivel}, \"\n"
     "            f\"hp={self.hp}/{self.hp_max}, atk={self.atk}, xp={self.xp})\")")
NOTE("Os dunder mais ricos (__eq__, __lt__, __len__, __iter__, __getitem__) não foram "
     "necessários até aqui. Encaixe natural, se quiser demonstrar: BandoDeGoblins já é uma "
     "coleção (__len__/__iter__) e Item poderia ordenar por bônus (__lt__/__eq__).")

H2("@property")
P("Já visto no Encapsulamento. No projeto é usado como <b>getter calculado</b> "
  "(<font face='Courier'>pontuacao, veneno_turnos, envenenado, ja_renasceu</font>) — leitura "
  "derivada, sem setter (a validação mora no __init__ e nos métodos).")

H2("@staticmethod e @classmethod")
P("Métodos que não dependem de uma instância. O Randongeon usa "
  "<font face='Courier'>@staticmethod</font> como <b>fábrica</b> de inimigos:")
CODE('class Inimigo(Entidade):\n'
     '    @staticmethod\n'
     '    def gerar(andar=1):               # fabrica: sorteia comum/elite/especial\n'
     '        if random.random() < 0.10: return HordaDeGoblins()\n'
     '        ...                            # escala por andar, despacha por nome\n'
     '        return Orc(hp, atk, xp, moedas)')
NOTE("@classmethod (recebe cls, útil para fábricas que usam a própria classe) não foi usado — a "
     "fábrica gerar() é @staticmethod por não precisar de cls.")

H2("Herança múltipla e MRO")
P("Python permite herdar de várias bases; o MRO (Method Resolution Order) define a ordem de "
  "busca. O Randongeon usa <b>herança simples</b> (mais clara) — o domínio não pediu misturar "
  "duas bases. Encaixe possível: um mixin <font face='Courier'>Venenoso</font>/"
  "<font face='Courier'>Atordoante</font>.")

H2("Composição vs Herança")
P("<b>Professor:</b> quando uma classe \"É\" outra, herde; quando \"TEM\" outra, componha. O "
  "Randongeon tem o exemplo perfeito lado a lado:")
CODE('class Goblin(Inimigo):                 # HERANCA: Goblin E UM Inimigo\n'
     '    def tabela_loot(self): return LOOT_HORDA\n\n'
     'class BandoDeGoblins:                  # COMPOSICAO: o Bando TEM 3 Goblins\n'
     '    TAMANHO = 3\n'
     '    def __init__(self):\n'
     '        self.goblins = [Goblin("Goblin", hp, atk, xp, moedas)\n'
     '                        for _ in range(self.TAMANHO)]   # NAO e um Inimigo')
TIP("Pergunte \"X É UM Y?\" ou \"X TEM UM Y?\". O Bando não é um inimigo — é um agrupador que TEM "
    "inimigos. Compor evita herança forçada e mantém cada responsabilidade no seu lugar. A "
    "Masmorra também compõe: ela TEM um Jogador e um GeradorSala.")
BR()

# ============================== PARTE 4 ==============================
H1("Parte 4 — Conteúdo ALÉM dos slides")
P("O que o Randongeon usou de POO/Python que os slides NÃO ensinaram. Não são erros — são "
  "recursos e padrões que o projeto trouxe para resolver problemas reais. Conhecê-los enriquece "
  "a prova.")

H2("Anotações de tipo (type hints)")
P("Os slides não cobrem typing, mas o projeto anota tudo: parâmetros, retornos e "
  "<font face='Courier'>Optional</font>/<font face='Courier'>list</font>/"
  "<font face='Courier'>tuple</font>. Documenta a intenção e ajuda ferramentas a achar erros.")
CODE('def atacar(self, alvo) -> dict: ...\n'
     'def gerar(andar: int = 1) -> "Inimigo": ...\n'
     'tipo_especial: Optional[str] = None')

H2("Padrões de projeto (Design Patterns)")
BULLETS([
    "<b>Template Method</b> — <font face='Courier'>Inimigo.tentar_renascer()</font>: a base devolve "
    "False; só <font face='Courier'>CoracaoDaMasmorra</font> sobrescreve para ressuscitar 1x. O "
    "laço de combate chama o hook sem saber o tipo (a 2ª fase do boss nasce sem um 'if').",
    "<b>Strategy (via objetos de efeito)</b> — <font face='Courier'>EfeitoStatus</font> e "
    "subclasses (Veneno/Fraqueza/EsquivaReduzida): cada efeito encapsula seu comportamento em "
    "hooks; a Entidade processa todos uniformemente.",
    "<b>Factory</b> — <font face='Courier'>Inimigo.gerar()</font> centraliza a criação procedural.",
    "<b>Value Object</b> — <font face='Courier'>Dom</font> (dom.py): objeto que sabe se aplicar a "
    "um Jogador (Bruto/Resistente/Ágil/Sortudo/Sanguessuga).",
])

H2("Validação por exceções")
P("Os construtores levantam <font face='Courier'>ValueError</font> para estados inválidos "
  "(hp&lt;=0, atk&lt;=0, chance fora de 0..1). A base abstrata usa "
  "<font face='Courier'>raise NotImplementedError</font>. É uma disciplina de \"falhe cedo, falhe "
  "claro\" que vai além do único exemplo de ValueError do slide.")

H2("Constantes de módulo como configuração tunável")
P("Além dos atributos de classe, o projeto usa constantes de módulo "
  "(<font face='Courier'>CHANCE_VENENO</font>, <font face='Courier'>ESQUIVA_ORC</font>, "
  "<font face='Courier'>BOSS_HP_BASE</font>, <font face='Courier'>ESPECIAL_HP_MULTIPLICADOR</font>) "
  "separando os números de balanceamento da lógica — calibrados por simulação Monte Carlo.")

H2("Arquitetura em camadas (separação de responsabilidades)")
P("O código separa <b>domínio</b> (<font face='Courier'>jogo/</font>: regras puras, sem "
  "print/IO), <b>API</b> (<font face='Courier'>api/</font>: FastAPI/REST) e <b>apresentação</b> "
  "(CLI e frontend). O <font face='Courier'>GeradorSala</font> só produz dados; quem exibe é "
  "outra camada. Isso é \"lógica != apresentação\", um princípio além do escopo de classe-única "
  "dos slides.")

H2("Outros recursos Python no projeto")
BULLETS([
    "<b>dataclass</b> com <font face='Courier'>field(default_factory=list)</font> no GameState (api).",
    "<b>List comprehensions</b>: <font face='Courier'>[Goblin(...) for _ in range(3)]</font>.",
    "<b>Argumentos nomeados e com padrão</b>: <font face='Courier'>bonus_hp: int = 0</font>, "
    "<font face='Courier'>super().__init__(nome=..., hp=...)</font>.",
    "<b>min/max para limites seguros</b>: <font face='Courier'>min(self.hp_max, self.hp + q)</font>.",
    "<b>__new__ nos testes</b>: cria um Inimigo dummy pulando o __init__ (técnica avançada).",
    "<b>Mocking</b> (<font face='Courier'>unittest.mock.patch</font>) e <b>simulação Monte Carlo</b> "
    "para decisões de balanceamento guiadas por dados.",
    "<b>Curto-circuito</b> proposital (<font face='Courier'>esquiva &gt; 0 and random()...</font>) "
    "para preservar sequências de RNG nos testes seeded.",
])
TIP("Testes (pytest), fixtures, parametrize e mocking não estão nos slides, mas são parte "
    "essencial de um projeto OO de verdade: garantem que herança e polimorfismo continuem "
    "funcionando a cada mudança. O Randongeon tem 656 testes de jogo + 35 de API.")
BR()

# ============================== PARTE 5 ==============================
H1("Parte 5 — Crônica do projeto (o que a pasta docs/ aborda)")
P("Cada lote do projeto tem um documento em <font face='Courier'>docs/</font> registrando o que "
  "mudou e quais pilares foram usados. Resumo do que a pasta cobre, ligando ao POO:")
TABLE([
    ["Lote / Tema", "Foco de POO", "Destaque"],
    ["A — Balanceamento v3.2", "Atributos de classe", "Curva de boss/nível em constantes"],
    ["B / B1 — Entidade(ABC)", "Abstração + ABC + Herança", "Base abstrata de Jogador e Inimigo"],
    ["B2 — EfeitoStatus", "Polimorfismo (hooks)", "Veneno/Fraqueza/EsquivaReduzida"],
    ["C — Loot por tipo", "Polimorfismo (override)", "tabela_loot() sem if por tipo"],
    ["D — API + inventário", "Encapsulamento (contrato)", "Schemas FastAPI x domínio"],
    ["E — Bando de Goblins", "Composição vs Herança", "Bando TEM Goblins; Goblin É UM Inimigo"],
    ["I — Inimigo.atacar()", "Encapsulamento + Polimorfismo", "Turno do inimigo unificado, sem if-tipo"],
    ["M — Veneno (DoT)", "Encapsulamento/Polimorfismo", "Efeito de dano por turno"],
    ["1 — Crítico", "Encapsulamento", "rolar_dano() concentra a regra"],
    ["2 — Identidade/evasão", "Herança/Polimorfismo", "Orc/Troll viram subclasses"],
    ["3 — Dom de slot", "Value Object/Encapsulamento", "aplicar_dom(jogador, id)"],
    ["4 — Coração 2 fases", "Template Method", "tentar_renascer() (hook polimórfico)"],
    ["5 — Badge de status", "Polimorfismo (serialização)", "Efeitos expostos por tipo+turnos"],
    ["Feedback level-up", "Encapsulamento", "progresso_nivel() + mensagem única"],
    ["Recalibração geral", "Atributos/constantes", "Curva de boss tunável (Monte Carlo)"],
    ["6 — Tutorial / 7 — Auditoria", "Documentação", "Estado final + aderência aos slides"],
], [4.3*cm, 5.2*cm, 6.7*cm])
NOTE("Outros docs cobrem frontend e correções (placar, robustez de sessão, textos, save em .txt, "
     "victory/game-over) — menos densos em POO, mas parte do mesmo projeto. Todo lote foi testado "
     "e, quando mexeu em balanceamento, calibrado por simulação.")
BR()

# ============================== PARTE 6 ==============================
H1("Parte 6 — Resumo dos pilares + dicas finais")
TABLE([
    ["Pilar", "Em uma frase", "No Randongeon"],
    ["Abstração", "Esconder o COMO, expor o O QUÊ (ABC + @abstractmethod).", "Entidade(ABC), receber_dano abstrato"],
    ["Encapsulamento", "Proteger o estado; público/_protegido/__privado + @property.", "_atualizar_nivel, @property pontuacao"],
    ["Herança", "Reusar via subclasses; super() chama o pai; filho É UM pai.", "Inimigo e 8 subclasses"],
    ["Polimorfismo", "Mesmo método, comportamento por tipo; override sem if-tipo.", "atacar(), tabela_loot(), receber_dano()"],
], [3.0*cm, 7.5*cm, 5.7*cm])

H2("Dicas finais de estudo")
BULLETS([
    "<b>Saiba citar com a palavra certa:</b> ao mostrar um trecho, diga o pilar (\"isto é "
    "polimorfismo por sobrescrita\") — o professor valoriza o vocabulário.",
    "<b>Abstração = ABC:</b> sempre que ver <font face='Courier'>class X(ABC)</font> e "
    "<font face='Courier'>@abstractmethod</font>, é abstração + um contrato.",
    "<b>Encapsulamento tem 3 níveis + @property:</b> lembre público, _protegido, __privado, e que "
    "@property faz getter/setter com sintaxe de atributo.",
    "<b>Herança x Composição:</b> teste com \"É UM\" vs \"TEM UM\". Goblin É UM Inimigo (herança); "
    "Bando TEM Goblins (composição).",
    "<b>Polimorfismo bom não tem if-tipo:</b> o objeto sabe se comportar; você só chama o método.",
    "<b>Dunder:</b> __init__ (criar), __repr__/__str__ (mostrar), __eq__/__lt__ (comparar/ordenar), "
    "__len__/__iter__/__getitem__ (coleções).",
    "<b>@staticmethod x @classmethod:</b> static não recebe nada de especial (função utilitária/"
    "fábrica simples); class recebe cls (fábrica que usa a própria classe).",
    "<b>Para a prova:</b> tenha um exemplo de cada pilar na ponta da língua — o Randongeon te dá "
    "um real para cada um.",
])
SP(10); HR()
NOTE("Documento de estudo gerado a partir dos slides do professor (POO Slide/aula/Código) e do "
     "código-fonte do projeto Randongeon. Use junto com a auditoria em docs/auditoria-poo-prova.md.")

# ============================== BUILD ==============================
def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#999"))
    canvas.drawCentredString(A4[0]/2.0, 1.0*cm, f"Guia de Estudos POO — Randongeon   |   página {doc.page}")
    canvas.restoreState()

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=2.0*cm, rightMargin=2.0*cm,
                        topMargin=1.7*cm, bottomMargin=1.6*cm,
                        title="Guia de Estudos POO — Randongeon", author="Projeto Randongeon")
doc.build(E, onFirstPage=_footer, onLaterPages=_footer)
print("PDF gerado:", OUT)
