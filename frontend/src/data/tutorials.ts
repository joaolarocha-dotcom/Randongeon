export interface TutorialPage {
  titulo: string;
  paragrafos: string[];
}

export const TUTORIAIS: TutorialPage[] = [
  {
    titulo: "BEM-VINDO À MASMORRA",
    paragrafos: [
      "Você entrou na Masmorra Sem Fim. Cada andar é uma sala: combate, baú/item ou loja.",
      "Avance acumulando XP, moedas e itens — e tente chegar vivo até o fim.",
      "STORY: 20 andares, com um boss a cada 5. INFINITO: sem fim, boss a cada 3 — mais perigo, mais recompensa.",
    ],
  },
  {
    titulo: "SEU HERÓI E O DOM",
    paragrafos: [
      "Você começa com HP 20, ATK 5 e ESQUIVA 30%, mais 2 itens: Poção de Cura Pequena (HP+4) e Punhal Gasto (ATK+1).",
      "No início da run você escolhe UM DOM (passivo permanente, com um trade-off):",
      "BRUTO: +ATK (−esquiva e crítico). RESISTENTE: +HP máx (−esquiva). ÁGIL: +esquiva e inimigos erram mais (−HP).",
      "SORTUDO: muito mais crítico (−ATK base). SANGUESSUGA: cura 10% do dano que você causa.",
    ],
  },
  {
    titulo: "COMBATE",
    paragrafos: [
      "LUTAR: ataque direto. Você tem ~10% de errar; e ~10% de acerto CRÍTICO (1,5× de dano).",
      "ESQUIVAR: chance igual à sua ESQUIVA. Se esquivar, evita o golpe e CONTRA-ATACA; se falhar, sofre o ataque normalmente.",
      "ITEM: use poções/elixires do inventário (curar, +ATK, +esquiva).",
      "FUGIR: ~50% de chance. Alguns inimigos (Nosferatu, Banshee) são mais difíceis de fugir; a Horda, mais fácil.",
      "Alguns inimigos também ESQUIVAM dos seus golpes — nem todo ataque acerta.",
    ],
  },
  {
    titulo: "SUBIR DE NÍVEL",
    paragrafos: [
      "Derrotar inimigos dá XP. Ao acumular o suficiente, você SOBE DE NÍVEL.",
      "A cada nível: +2 ATK, +12 HP máximo, um pouco de esquiva, e sua VIDA é recuperada em 60% do HP máx.",
      "Subir de nível também PURGA o veneno. Uma mensagem ⭐ avisa quando isso acontece.",
      "A barra de XP no combate mostra o quanto falta para o próximo nível.",
    ],
  },
  {
    titulo: "STATUS (BADGES)",
    paragrafos: [
      "Durante o combate, ícones abaixo do seu nome mostram os efeitos ativos:",
      "☠️ VENENO: perde 1 de vida por turno (some ao curar/subir de nível).",
      "💪 FRACO: seu ATK fica reduzido por alguns turnos.",
      "💫 ZONZO: sua ESQUIVA cai no próximo turno.",
      "⭐ DOM: o passivo que você escolheu no começo da run.",
    ],
  },
  {
    titulo: "INIMIGOS ESPECIAIS",
    paragrafos: [
      "GOLEM DE PEDRA: tem ARMADURA — reduz o dano que recebe (e fica mais resistente nos andares fundos).",
      "NOSFERATU: DRENA VIDA ao te acertar, se curando.",
      "BANSHEE: pode ATORDOAR (você perde o turno) e é etérea — ESQUIVA muito.",
      "ORC: aplica FRAQUEZA (−ATK) e desvia de alguns golpes. TROLL DAS CAVERNAS: tanque de HP, e a maçada te deixa ZONZO.",
      "GOBLIN e RATO GIGANTE podem te ENVENENAR. A HORDA/BANDO vem em 3 goblins, um de cada vez.",
    ],
  },
  {
    titulo: "BOSSES",
    paragrafos: [
      "STORY: boss a cada 5 andares (5, 10, 15 e 20). INFINITO: a cada 3.",
      "Os bosses são bem mais fortes que os inimigos comuns — chegue preparado e com poções.",
      "O CORAÇÃO DA MASMORRA (andar 20) tem DUAS FASES: ao cair, ele RENASCE uma vez com metade da vida e em FÚRIA.",
      "Só a SEGUNDA morte do Coração vence a campanha. Não baixe a guarda quando a barra dele zerar!",
    ],
  },
  {
    titulo: "ITENS, LOJA E BAÚS",
    paragrafos: [
      "Entre andares: ~15% de chance de LOJA, ~15% de ITEM e ~70% de INIMIGO.",
      "Na loja você gasta moedas em poções e equipamentos. Itens de ATK/esquiva são permanentes; poções curam.",
      "Cuidado com baús: alguns escondem um MÍMICO disfarçado, que ataca quando aberto.",
    ],
  },
  {
    titulo: "SALVAR E PLACAR",
    paragrafos: [
      "Você pode EXPORTAR sua run para um arquivo .txt e IMPORTAR depois para continuar de onde parou.",
      "Sua pontuação considera XP, nível, moedas e o andar alcançado.",
      "Ao fim da run, sua pontuação pode entrar no PLACAR — tente bater seu recorde!",
    ],
  },
];
