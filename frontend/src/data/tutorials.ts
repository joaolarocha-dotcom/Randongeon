export interface TutorialPage {
  titulo: string;
  paragrafos: string[];
}

export const TUTORIAIS: TutorialPage[] = [
  {
    titulo: "BEM-VINDO À MASMORRA",
    paragrafos: [
      "Você é um aventureiro que entrou na Masmorra Sem Fim.",
      "Cada andar tem uma sala: combate, baú, ou loja.",
      "Avance pelos andares acumulando XP, moedas e itens.",
    ],
  },
  {
    titulo: "COMBATE",
    paragrafos: [
      "LUTAR: ataque direto, ambos se atacam.",
      "ESQUIVAR: chance baseada na sua ESQ — sucesso evita dano e contra-ataca; falha causa dano dobrado.",
      "ITEM: use poções e elixires do seu inventário.",
      "FUGIR: 50% de chance, falha sofre o ataque inimigo.",
    ],
  },
  {
    titulo: "ITENS E LOJAS",
    paragrafos: [
      "Lojas aparecem 15% das vezes entre andares.",
      "Após derrotar um boss, uma loja sempre aparece.",
      "Você começa com 2 itens: Erva Medicinal (HP+3) e Poção de Força (ATK+1).",
    ],
  },
  {
    titulo: "BOSSES",
    paragrafos: [
      "Modo Story: boss a cada 5 andares.",
      "Modo Infinito: boss a cada 3 andares — mais recompensas, mais perigo.",
      "Vencer um boss restaura 40% do seu HP máximo.",
      "Cuidado com baús: 1 em 20 é um Mímico disfarçado!",
    ],
  },
];
