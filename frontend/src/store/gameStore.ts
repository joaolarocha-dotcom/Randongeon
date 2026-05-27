// frontend/src/store/gameStore.ts  — v3.1

import { create } from "zustand";
import { api } from "../api/client";
import type {
  JogadorStatus,
  InimigoInfo,
  ItemInfo,
  LojaInfo,
  CombatActionResponse,
} from "../api/client";

export type Screen =
  | "title" | "lore" | "menu" | "advancing"
  | "combat" | "chest" | "shop" | "game_over";

export interface CombatLog {
  mensagem: string;
  tipo: "info" | "dano" | "vitoria" | "derrota" | "fuga" | "miss" | "loot";
}

interface GameStore {
  screen:            Screen;
  sessionId:         string | null;
  jogador:           JogadorStatus | null;
  inimigo:           InimigoInfo | null;
  item:              ItemInfo | null;
  loja:              LojaInfo | null;
  loreLinhas:        string[];
  combatLog:         CombatLog[];
  descricaoSala:     string;
  gameOverMsg:       string;
  loading:           boolean;
  error:             string | null;
  jogadorAtordoado:  boolean;
  ultimoLoot:        ItemInfo | null;   // v3.1 — último item dropado

  startGame:    (nome: string)    => Promise<void>;
  fetchLore:    ()                => Promise<void>;
  goToMenu:     ()                => void;
  advance:      ()                => Promise<void>;
  combatAttack: ()                => Promise<void>;
  combatDodge:  ()                => Promise<void>;
  combatFlee:   ()                => Promise<void>;
  openChest:    ()                => Promise<void>;
  ignoreChest:  ()                => Promise<void>;
  shopBuy:      (indice: number)  => Promise<void>;
  shopLeave:    ()                => Promise<void>;
  quit:         ()                => Promise<void>;
  reset:        ()                => void;
}

export const useGameStore = create<GameStore>((set, get) => ({
  screen:           "title",
  sessionId:        null,
  jogador:          null,
  inimigo:          null,
  item:             null,
  loja:             null,
  loreLinhas:       [],
  combatLog:        [],
  descricaoSala:    "",
  gameOverMsg:      "",
  loading:          false,
  error:            null,
  jogadorAtordoado: false,
  ultimoLoot:       null,

  startGame: async (nome) => {
    set({ loading: true, error: null });
    try {
      const res = await api.newGame(nome);
      set({ sessionId: res.session_id, jogador: res.jogador, screen: "lore", loading: false });
    } catch (e: unknown) {
      set({ error: (e as Error).message, loading: false });
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
    set({ loading: true, error: null, combatLog: [], jogadorAtordoado: false, ultimoLoot: null });
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
    } catch (e: unknown) {
      set({ error: (e as Error).message, loading: false });
    }
  },

  combatAttack: async () => {
    const { sessionId } = get();
    if (!sessionId) return;
    set({ loading: true });
    try {
      const res = await api.combatAttack(sessionId);
      handleCombatResult(res, set, get);
    } catch (e: unknown) {
      set({ error: (e as Error).message, loading: false });
    }
  },

  combatDodge: async () => {
    const { sessionId } = get();
    if (!sessionId) return;
    set({ loading: true });
    try {
      const res = await api.combatDodge(sessionId);
      handleCombatResult(res, set, get);
    } catch (e: unknown) {
      set({ error: (e as Error).message, loading: false });
    }
  },

  combatFlee: async () => {
    const { sessionId } = get();
    if (!sessionId) return;
    set({ loading: true });
    try {
      const res = await api.combatFlee(sessionId);
      handleCombatResult(res, set, get);
    } catch (e: unknown) {
      set({ error: (e as Error).message, loading: false });
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
        set({ item: res.item || null, descricaoSala: res.mensagem, screen: "menu" });
      }
    } catch (e: unknown) {
      set({ error: (e as Error).message, loading: false });
    }
  },

  ignoreChest: async () => {
    const { sessionId } = get();
    if (!sessionId) return;
    const res = await api.chestIgnore(sessionId);
    set({ jogador: res.jogador, screen: "menu" });
  },

  shopBuy: async (indice) => {
    const { sessionId } = get();
    if (!sessionId) return;
    set({ loading: true });
    try {
      const res = await api.shopBuy(sessionId, indice);
      set({ jogador: res.jogador, loja: res.loja || null, loading: false });
      if (!res.loja) set({ screen: "menu" });
    } catch (e: unknown) {
      set({ error: (e as Error).message, loading: false });
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
    } catch (e: unknown) {
      set({ error: (e as Error).message });
    }
  },

  reset: () => set({
    screen: "title", sessionId: null, jogador: null, inimigo: null,
    item: null, loja: null, loreLinhas: [], combatLog: [],
    descricaoSala: "", gameOverMsg: "", loading: false,
    error: null, jogadorAtordoado: false, ultimoLoot: null,
  }),
}));

// ── Handler central de resultado de combate ───────────────────────────────────

function handleCombatResult(res: CombatActionResponse, set: any, get: any) {
  const log: CombatLog[] = [...get().combatLog];

  // Entrada principal de combate
  const tipo =
    res.resultado === "vitoria" ? "vitoria" :
    res.resultado === "derrota" ? "derrota" :
    res.resultado === "fuga"    ? "fuga"    : "dano";

  log.push({ mensagem: res.mensagem, tipo });

  // Entradas extras de miss
  if (res.miss_jogador) {
    log.push({ mensagem: "✗ Você errou o ataque.", tipo: "miss" });
  }
  if (res.miss_inimigo) {
    log.push({ mensagem: "✗ O inimigo errou o ataque.", tipo: "miss" });
  }

  // Entrada de loot
  if (res.loot) {
    log.push({
      mensagem: `✨ Drop: ${res.loot.nome}!`,
      tipo: "loot",
    });
  }

  set({
    jogador:          res.jogador,
    inimigo:          res.inimigo,
    combatLog:        log,
    loading:          false,
    jogadorAtordoado: res.jogador_atordoado ?? false,
    ultimoLoot:       res.loot ?? null,
  });

  if (res.resultado === "vitoria" || res.resultado === "fuga") {
    setTimeout(() => set({ screen: "menu", jogadorAtordoado: false }), 1800);
  } else if (res.resultado === "derrota") {
    setTimeout(() => set({
      screen:           "game_over",
      gameOverMsg:      `${res.jogador.nome} foi derrotado no andar ${res.jogador.andar}.`,
      jogadorAtordoado: false,
    }), 1800);
  }
}