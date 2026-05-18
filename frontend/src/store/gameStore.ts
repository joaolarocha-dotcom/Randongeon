import { create } from "zustand";
import {
  api,
} from "../api/client";
import type {
  JogadorStatus,
  InimigoInfo,
  ItemInfo,
  LojaInfo,
  CombatActionResponse,
} from "../api/client";

export type Screen =
  | "title"
  | "lore"
  | "menu"
  | "advancing"
  | "combat"
  | "chest"
  | "shop"
  | "game_over";

interface CombatLog {
  mensagem: string;
  tipo: "info" | "dano" | "vitoria" | "derrota" | "fuga";
}

interface GameStore {
  screen: Screen;
  sessionId: string | null;
  jogador: JogadorStatus | null;
  inimigo: InimigoInfo | null;
  item: ItemInfo | null;
  loja: LojaInfo | null;
  loreLinhas: string[];
  combatLog: CombatLog[];
  descricaoSala: string;
  gameOverMsg: string;
  loading: boolean;
  error: string | null;

  startGame: (nome: string) => Promise<void>;
  fetchLore: () => Promise<void>;
  goToMenu: () => void;
  advance: () => Promise<void>;
  combatAttack: () => Promise<void>;
  combatDodge: () => Promise<void>;
  combatFlee: () => Promise<void>;
  openChest: () => Promise<void>;
  ignoreChest: () => Promise<void>;
  shopBuy: (indice: number) => Promise<void>;
  shopLeave: () => Promise<void>;
  quit: () => Promise<void>;
  reset: () => void;
}

export const useGameStore = create<GameStore>((set, get) => ({
  screen: "title",
  sessionId: null,
  jogador: null,
  inimigo: null,
  item: null,
  loja: null,
  loreLinhas: [],
  combatLog: [],
  descricaoSala: "",
  gameOverMsg: "",
  loading: false,
  error: null,

  startGame: async (nome: string) => {
    set({ loading: true, error: null });
    try {
      const res = await api.newGame(nome);
      set({
        sessionId: res.session_id,
        jogador: res.jogador,
        screen: "lore",
        loading: false,
      });
    } catch (e: any) {
      set({ error: e.message, loading: false });
    }
  },

  fetchLore: async () => {
    const { sessionId } = get();
    if (!sessionId) return;
    const res = await api.getLore(sessionId);
    set({ loreLinhas: res.linhas });
  },

  goToMenu: () => set({ screen: "menu" }),

  advance: async () => {
    const { sessionId } = get();
    if (!sessionId) return;
    set({ loading: true, error: null, combatLog: [] });
    try {
      const res = await api.advance(sessionId);
      set({ jogador: res.jogador, descricaoSala: res.descricao });

      if (res.tipo === "inimigo" || res.tipo === "boss") {
        set({ inimigo: res.inimigo!, screen: "combat", loading: false });
      } else if (res.tipo === "item") {
        set({ item: res.item || null, screen: "chest", loading: false });
      } else if (res.tipo === "loja") {
        set({ loja: res.loja!, screen: "shop", loading: false });
      } else {
        set({ screen: "menu", loading: false });
      }
    } catch (e: any) {
      set({ error: e.message, loading: false });
    }
  },

  combatAttack: async () => {
    const { sessionId } = get();
    if (!sessionId) return;
    set({ loading: true });
    try {
      const res = await api.combatAttack(sessionId);
      handleCombatResult(res, set, get);
    } catch (e: any) {
      set({ error: e.message, loading: false });
    }
  },

  combatDodge: async () => {
    const { sessionId } = get();
    if (!sessionId) return;
    set({ loading: true });
    try {
      const res = await api.combatDodge(sessionId);
      handleCombatResult(res, set, get);
    } catch (e: any) {
      set({ error: e.message, loading: false });
    }
  },

  combatFlee: async () => {
    const { sessionId } = get();
    if (!sessionId) return;
    set({ loading: true });
    try {
      const res = await api.combatFlee(sessionId);
      handleCombatResult(res, set, get);
    } catch (e: any) {
      set({ error: e.message, loading: false });
    }
  },

  openChest: async () => {
    const { sessionId } = get();
    if (!sessionId) return;
    set({ loading: true });
    try {
      const res = await api.chestOpen(sessionId);
      set({ jogador: res.jogador, loading: false });
      if (res.tipo === "mimico") {
        set({
          inimigo: res.inimigo!,
          screen: "combat",
          combatLog: [{ mensagem: res.mensagem, tipo: "info" }],
        });
      } else {
        set({
          item: res.item || null,
          descricaoSala: res.mensagem,
          screen: "menu",
        });
      }
    } catch (e: any) {
      set({ error: e.message, loading: false });
    }
  },

  ignoreChest: async () => {
    const { sessionId } = get();
    if (!sessionId) return;
    const res = await api.chestIgnore(sessionId);
    set({ jogador: res.jogador, screen: "menu" });
  },

  shopBuy: async (indice: number) => {
    const { sessionId } = get();
    if (!sessionId) return;
    set({ loading: true });
    try {
      const res = await api.shopBuy(sessionId, indice);
      set({ jogador: res.jogador, loja: res.loja || null, loading: false });
      if (!res.loja) {
        set({ screen: "menu" });
      }
    } catch (e: any) {
      set({ error: e.message, loading: false });
    }
  },

  shopLeave: async () => {
    const { sessionId } = get();
    if (!sessionId) return;
    const res = await api.shopLeave(sessionId);
    set({ jogador: res.jogador, loja: null, screen: "menu" });
  },

  quit: async () => {
    const { sessionId } = get();
    if (!sessionId) return;
    try {
      const res = await api.quit(sessionId);
      set({ gameOverMsg: res.mensagem, jogador: res.jogador, screen: "game_over" });
    } catch (e: any) {
      set({ error: e.message });
    }
  },

  reset: () =>
    set({
      screen: "title",
      sessionId: null,
      jogador: null,
      inimigo: null,
      item: null,
      loja: null,
      loreLinhas: [],
      combatLog: [],
      descricaoSala: "",
      gameOverMsg: "",
      loading: false,
      error: null,
    }),
}));

function handleCombatResult(
  res: CombatActionResponse,
  set: any,
  get: any
) {
  const log = get().combatLog;
  const tipo =
    res.resultado === "vitoria"
      ? "vitoria"
      : res.resultado === "derrota"
      ? "derrota"
      : res.resultado === "fuga"
      ? "fuga"
      : "dano";

  const newLog = [...log, { mensagem: res.mensagem, tipo }];
  set({ jogador: res.jogador, inimigo: res.inimigo, combatLog: newLog, loading: false });

  if (res.resultado === "vitoria" || res.resultado === "fuga") {
    setTimeout(() => set({ screen: "menu" }), 1500);
  } else if (res.resultado === "derrota") {
    setTimeout(
      () =>
        set({
          screen: "game_over",
          gameOverMsg: `${res.jogador.nome} foi derrotado no andar ${res.jogador.andar}.`,
        }),
      1500
    );
  }
}
