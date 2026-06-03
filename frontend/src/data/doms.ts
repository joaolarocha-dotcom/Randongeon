/**
 * Doms selecionáveis no início da run (Lote 3b).
 * Espelha o registro DONS do backend (jogo/entidades/dom.py).
 * O `id` é o que vai para a API; `null` = nenhum dom.
 */
export interface DomInfo {
  id: string;
  nome: string;
  descricao: string;
}

export const DOMS: DomInfo[] = [
  { id: "bruto",       nome: "Bruto",       descricao: "+3 ATK. Em troca: menos esquiva e crítico." },
  { id: "resistente",  nome: "Resistente",  descricao: "+10 HP máximo. Em troca: um pouco menos de esquiva." },
  { id: "agil",        nome: "Ágil",        descricao: "+esquiva e inimigos erram mais. Em troca: menos HP." },
  { id: "sortudo",     nome: "Sortudo",     descricao: "Muito mais crítico. Em troca: menos dano base." },
  { id: "sanguessuga", nome: "Sanguessuga", descricao: "Cura 10% do dano que você causa." },
];
