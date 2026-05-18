const API_BASE = "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Erro desconhecido" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export interface JogadorStatus {
  nome: string;
  hp: number;
  hp_max: number;
  atk: number;
  esq: number;
  xp: number;
  moedas: number;
  andar: number;
}

export interface InimigoInfo {
  nome: string;
  hp: number;
  hp_max: number;
  atk: number;
  dificuldade: number;
}

export interface ItemInfo {
  nome: string;
  bonus_atk: number;
  bonus_hp: number;
  bonus_esq: number;
}

export interface LojaOferta {
  nome: string;
  preco: number;
  bonus_atk: number;
  bonus_hp: number;
  bonus_esq: number;
}

export interface LojaInfo {
  ofertas: LojaOferta[];
}

export interface SalaResponse {
  tipo: string;
  descricao: string;
  andar: number;
  inimigo?: InimigoInfo;
  item?: ItemInfo;
  loja?: LojaInfo;
  jogador: JogadorStatus;
}

export interface CombatActionResponse {
  resultado: string;
  mensagem: string;
  dano_jogador: number;
  dano_inimigo: number;
  jogador: JogadorStatus;
  inimigo?: InimigoInfo;
}

export interface ChestResponse {
  tipo: string;
  mensagem: string;
  item?: ItemInfo;
  inimigo?: InimigoInfo;
  jogador: JogadorStatus;
}

export interface ShopBuyResponse {
  sucesso: boolean;
  mensagem: string;
  jogador: JogadorStatus;
  loja?: LojaInfo;
}

export interface LoreResponse {
  linhas: string[];
}

export interface GameOverResponse {
  mensagem: string;
  jogador: JogadorStatus;
}

export const api = {
  newGame: (nome: string) =>
    request<{ session_id: string; jogador: JogadorStatus }>("/game/new", {
      method: "POST",
      body: JSON.stringify({ nome }),
    }),

  getStatus: (id: string) =>
    request<JogadorStatus>(`/game/${id}/status`),

  getLore: (id: string) =>
    request<LoreResponse>(`/game/${id}/lore`),

  advance: (id: string) =>
    request<SalaResponse>(`/game/${id}/advance`, { method: "POST" }),

  combatAttack: (id: string) =>
    request<CombatActionResponse>(`/game/${id}/combat/attack`, { method: "POST" }),

  combatDodge: (id: string) =>
    request<CombatActionResponse>(`/game/${id}/combat/dodge`, { method: "POST" }),

  combatFlee: (id: string) =>
    request<CombatActionResponse>(`/game/${id}/combat/flee`, { method: "POST" }),

  chestOpen: (id: string) =>
    request<ChestResponse>(`/game/${id}/chest/open`, { method: "POST" }),

  chestIgnore: (id: string) =>
    request<ChestResponse>(`/game/${id}/chest/ignore`, { method: "POST" }),

  shopBuy: (id: string, indice: number) =>
    request<ShopBuyResponse>(`/game/${id}/shop/buy`, {
      method: "POST",
      body: JSON.stringify({ indice }),
    }),

  shopLeave: (id: string) =>
    request<ShopBuyResponse>(`/game/${id}/shop/leave`, { method: "POST" }),

  quit: (id: string) =>
    request<GameOverResponse>(`/game/${id}/quit`, { method: "POST" }),
};
