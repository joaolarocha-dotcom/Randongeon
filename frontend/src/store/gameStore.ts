import { create } from "zustand";
import { api } from "../api/client";
import type {
  JogadorStatus,
  InimigoInfo,
  ItemInfo,
  LojaInfo,
  CombatActionResponse,
} from "../api/client";
import { audio } from "../components/audio/AudioEngine";
import { getArenaMusic } from "../assets/bgMap";

function errorMessage(e: unknown): string {
  if (e instanceof Error) return e.message;
  if (typeof e === "string") return e;
  return "Erro desconhecido";
}

/**
 * Registry de setTimeouts em vôo. Evita race condition entre setTimeouts de fim de combate
 * e ações subsequentes do jogador (ex: AVANÇAR enquanto victory ainda não disparou).
 */
const pendingTimeouts = new Set<number>();

function scheduleTimeout(fn: () => void, ms: number): number {
  const id = window.setTimeout(() => {
    pendingTimeouts.delete(id);
    fn();
  }, ms);
  pendingTimeouts.add(id);
  return id;
}

function cancelAllTimeouts() {
  pendingTimeouts.forEach((id) => clearTimeout(id));
  pendingTimeouts.clear();
}

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

/**
 * Fases de animação da CombatScreen.
 * - idle: aguardando input do jogador
 * - intro: slide-in dos sprites + diálogos iniciais
 * - player_action: ataque/esquiva/fuga do jogador animando
 * - enemy_action: contra-ataque animando
 * - hp_drain: barras de HP drenando
 * - victory / defeat / flee: fim de combate
 */
export type AnimPhase =
  | "idle"
  | "intro"
  | "player_action"
  | "enemy_action"
  | "hp_drain"
  | "victory"
  | "defeat"
  | "flee";

interface GameStore {
  // Estado de jogo
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

  // Estado de animação
  animPhase: AnimPhase;
  /** HP exibido (anima rumo a jogador.hp). */
  displayedPlayerHP: number;
  /** HP exibido (anima rumo a inimigo.hp). */
  displayedEnemyHP: number;
  /** Fila de mensagens a exibir na BattleDialog. */
  dialogQueue: string[];
  /** Mensagem atual sendo digitada (null = nenhuma). */
  currentDialog: string | null;
  /** Transição de andar ativa. Se !== null, FloorTransition é mostrado. */
  floorTransitionAndar: number | null;
  /** XP no início do último combate (para calcular ganho). */
  lastXpSnapshot: number;

  // Actions principais (jogo)
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

  // Actions de animação
  setAnimPhase: (phase: AnimPhase) => void;
  enqueueDialog: (text: string | string[]) => void;
  nextDialog: () => void;
  clearDialog: () => void;
  setDisplayedPlayerHP: (v: number) => void;
  setDisplayedEnemyHP: (v: number) => void;
  setFloorTransition: (andar: number | null) => void;
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

  animPhase: "idle",
  displayedPlayerHP: 0,
  displayedEnemyHP: 0,
  dialogQueue: [],
  currentDialog: null,
  floorTransitionAndar: null,
  lastXpSnapshot: 0,

  // ───────── Jogo ─────────

  startGame: async (nome: string) => {
    set({ loading: true, error: null });
    try {
      const res = await api.newGame(nome);
      set({
        sessionId: res.session_id,
        jogador: res.jogador,
        displayedPlayerHP: res.jogador.hp,
        screen: "lore",
        loading: false,
      });
      audio.playMusic("bgm_title");
    } catch (e) {
      set({ error: errorMessage(e), loading: false });
    }
  },

  fetchLore: async () => {
    const { sessionId } = get();
    if (!sessionId) return;
    const res = await api.getLore(sessionId);
    set({ loreLinhas: res.linhas });
  },

  goToMenu: () => {
    set({ screen: "menu" });
    audio.playMusic("bgm_dungeon");
  },

  advance: async () => {
    const { sessionId, jogador } = get();
    if (!sessionId) return;

    // Cancela timeouts pendentes (ex: vitória ainda não disparou e jogador já clicou AVANÇAR)
    cancelAllTimeouts();
    set({ loading: true, error: null, combatLog: [], dialogQueue: [], currentDialog: null });

    // Mostra transição de andar antes da resposta da API
    const proximoAndar = (jogador?.andar ?? 0) + 1;
    set({ floorTransitionAndar: proximoAndar });
    audio.playSfx("sfx_floor_transition");

    // Pequeno delay para a transição ser perceptível
    await new Promise((r) => setTimeout(r, 700));

    try {
      const res = await api.advance(sessionId);
      set({
        jogador: res.jogador,
        displayedPlayerHP: res.jogador.hp,
        descricaoSala: res.descricao,
        floorTransitionAndar: null,
      });

      if (res.tipo === "inimigo" || res.tipo === "boss") {
        const inimigo = res.inimigo!;
        const intro = [
          `Um ${inimigo.nome} selvagem apareceu!`,
          `Vai, ${res.jogador.nome}!`,
        ];
        set({
          inimigo,
          displayedEnemyHP: inimigo.hp_max,
          screen: "combat",
          loading: false,
          animPhase: "intro",
          // Inicia com o primeiro item e enfileira o resto
          currentDialog: intro[0],
          dialogQueue: intro.slice(1),
          lastXpSnapshot: res.jogador.xp,
        });
        audio.playMusic(getArenaMusic(res.andar, res.tipo));
      } else if (res.tipo === "item") {
        set({ item: res.item || null, screen: "chest", loading: false });
        audio.playMusic("bgm_dungeon");
      } else if (res.tipo === "loja") {
        set({ loja: res.loja!, screen: "shop", loading: false });
        audio.playMusic("bgm_shop");
      } else {
        set({ screen: "menu", loading: false });
        audio.playMusic("bgm_dungeon");
      }
    } catch (e) {
      set({ error: errorMessage(e), loading: false, floorTransitionAndar: null });
    }
  },

  combatAttack: async () => {
    const { sessionId } = get();
    if (!sessionId) return;
    audio.playSfx("sfx_menu_select");
    set({ loading: true, animPhase: "player_action" });
    try {
      const res = await api.combatAttack(sessionId);
      handleCombatResult(res, "attack", set, get);
    } catch (e) {
      set({ error: errorMessage(e), loading: false, animPhase: "idle" });
    }
  },

  combatDodge: async () => {
    const { sessionId } = get();
    if (!sessionId) return;
    audio.playSfx("sfx_menu_select");
    set({ loading: true, animPhase: "player_action" });
    try {
      const res = await api.combatDodge(sessionId);
      handleCombatResult(res, "dodge", set, get);
    } catch (e) {
      set({ error: errorMessage(e), loading: false, animPhase: "idle" });
    }
  },

  combatFlee: async () => {
    const { sessionId } = get();
    if (!sessionId) return;
    audio.playSfx("sfx_menu_select");
    set({ loading: true, animPhase: "player_action" });
    try {
      const res = await api.combatFlee(sessionId);
      handleCombatResult(res, "flee", set, get);
    } catch (e) {
      set({ error: errorMessage(e), loading: false, animPhase: "idle" });
    }
  },

  openChest: async () => {
    const { sessionId } = get();
    if (!sessionId) return;
    audio.playSfx("sfx_chest_open");
    set({ loading: true });
    try {
      const res = await api.chestOpen(sessionId);
      set({ jogador: res.jogador, displayedPlayerHP: res.jogador.hp, loading: false });
      if (res.tipo === "mimico") {
        const inimigo = res.inimigo!;
        const intro = [res.mensagem, `O ${inimigo.nome} ataca!`];
        set({
          inimigo,
          displayedEnemyHP: inimigo.hp_max,
          screen: "combat",
          combatLog: [{ mensagem: res.mensagem, tipo: "info" }],
          animPhase: "intro",
          currentDialog: intro[0],
          dialogQueue: intro.slice(1),
          lastXpSnapshot: res.jogador.xp,
        });
        // Mímico em andar de boss usa BGM de boss; senão, BGM normal
        audio.playMusic(getArenaMusic(res.jogador.andar));
      } else {
        audio.playSfx("sfx_item_get");
        set({
          item: res.item || null,
          descricaoSala: res.mensagem,
          screen: "menu",
        });
        audio.playMusic("bgm_dungeon");
      }
    } catch (e) {
      set({ error: errorMessage(e), loading: false });
    }
  },

  ignoreChest: async () => {
    const { sessionId } = get();
    if (!sessionId) return;
    audio.playSfx("sfx_menu_cancel");
    const res = await api.chestIgnore(sessionId);
    set({ jogador: res.jogador, displayedPlayerHP: res.jogador.hp, screen: "menu" });
    audio.playMusic("bgm_dungeon");
  },

  shopBuy: async (indice: number) => {
    const { sessionId } = get();
    if (!sessionId) return;
    set({ loading: true });
    try {
      const res = await api.shopBuy(sessionId, indice);
      // Toca som de compra se foi sucesso; senão, cancel
      if (res.sucesso) {
        audio.playSfx("sfx_shop_buy");
      } else {
        audio.playSfx("sfx_menu_cancel");
      }
      set({
        jogador: res.jogador,
        displayedPlayerHP: res.jogador.hp,
        loja: res.loja || null,
        loading: false,
      });
      if (!res.loja) {
        set({ screen: "menu" });
        audio.playMusic("bgm_dungeon");
      }
    } catch (e) {
      set({ error: errorMessage(e), loading: false });
    }
  },

  shopLeave: async () => {
    const { sessionId } = get();
    if (!sessionId) return;
    audio.playSfx("sfx_menu_cancel");
    const res = await api.shopLeave(sessionId);
    set({ jogador: res.jogador, displayedPlayerHP: res.jogador.hp, loja: null, screen: "menu" });
    audio.playMusic("bgm_dungeon");
  },

  quit: async () => {
    const { sessionId } = get();
    if (!sessionId) return;
    cancelAllTimeouts();
    try {
      const res = await api.quit(sessionId);
      set({ gameOverMsg: res.mensagem, jogador: res.jogador, screen: "game_over" });
      audio.playJingle("bgm_game_over");
    } catch (e) {
      set({ error: errorMessage(e) });
    }
  },

  reset: () => {
    audio.stopMusic();
    cancelAllTimeouts();
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
      animPhase: "idle",
      displayedPlayerHP: 0,
      displayedEnemyHP: 0,
      dialogQueue: [],
      currentDialog: null,
      floorTransitionAndar: null,
      lastXpSnapshot: 0,
    });
  },

  // ───────── Animação ─────────

  setAnimPhase: (phase) => set({ animPhase: phase }),

  enqueueDialog: (text) => {
    const arr = Array.isArray(text) ? text : [text];
    const filtered = arr.map((t) => (t ?? "").trim()).filter(Boolean);
    const { currentDialog, dialogQueue } = get();
    if (!currentDialog && filtered.length > 0) {
      // Inicia imediatamente com o primeiro e enfileira o restante
      set({ currentDialog: filtered[0], dialogQueue: [...dialogQueue, ...filtered.slice(1)] });
    } else {
      set({ dialogQueue: [...dialogQueue, ...filtered] });
    }
  },

  nextDialog: () => {
    const { dialogQueue } = get();
    if (dialogQueue.length === 0) {
      set({ currentDialog: null });
      return;
    }
    const [next, ...rest] = dialogQueue;
    set({ currentDialog: next, dialogQueue: rest });
  },

  clearDialog: () => set({ currentDialog: null, dialogQueue: [] }),

  setDisplayedPlayerHP: (v) => set({ displayedPlayerHP: v }),
  setDisplayedEnemyHP: (v) => set({ displayedEnemyHP: v }),
  setFloorTransition: (andar) => set({ floorTransitionAndar: andar }),
}));

// ─────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────

type CombatAction = "attack" | "dodge" | "flee";

type StoreSet = (partial: Partial<GameStore>) => void;
type StoreGet = () => GameStore;

/**
 * Quebra uma mensagem do backend em linhas para exibir sequencialmente.
 * Backend manda strings como "Você causou 3 de dano. Goblin causou 1 de dano em você."
 */
function splitMensagem(msg: string): string[] {
  if (!msg) return [];
  // Quebra por ". " mas mantém o ponto final
  return msg
    .split(/(?<=\.)\s+/)
    .map((s) => s.trim())
    .filter(Boolean);
}

/**
 * Adiciona mensagens à fila de diálogo, promovendo a primeira para currentDialog
 * caso este esteja vazio. Centraliza o "enqueue manual" usado em handleCombatResult.
 */
function appendDialog(set: StoreSet, get: StoreGet, mensagens: string[]) {
  if (mensagens.length === 0) return;
  const { currentDialog, dialogQueue } = get();
  if (!currentDialog) {
    set({
      currentDialog: mensagens[0],
      dialogQueue: [...dialogQueue, ...mensagens.slice(1)],
    });
  } else {
    set({ dialogQueue: [...dialogQueue, ...mensagens] });
  }
}

function handleCombatResult(
  res: CombatActionResponse,
  action: CombatAction,
  set: StoreSet,
  get: StoreGet
) {
  const log = get().combatLog;
  const tipo: CombatLog["tipo"] =
    res.resultado === "vitoria"
      ? "vitoria"
      : res.resultado === "derrota"
      ? "derrota"
      : res.resultado === "fuga"
      ? "fuga"
      : "dano";

  const newLog: CombatLog[] = [...log, { mensagem: res.mensagem, tipo }];

  // Atualiza dados base (sem mexer no displayed HP — barras animam separadamente)
  set({
    jogador: res.jogador,
    inimigo: res.inimigo ?? null,
    combatLog: newLog,
    loading: false,
  });

  // SFX por tipo de ação
  if (action === "attack") {
    if (res.dano_inimigo > 0) audio.playSfx("sfx_attack_hit");
  } else if (action === "dodge") {
    if (res.dano_jogador === 0) audio.playSfx("sfx_attack_miss");
    if (res.dano_inimigo > 0) audio.playSfx("sfx_attack_hit");
  } else if (action === "flee") {
    if (res.resultado === "fuga") audio.playSfx("sfx_flee_success");
    else audio.playSfx("sfx_flee_fail");
  }

  // Enfileira mensagens
  const mensagens = splitMensagem(res.mensagem);

  // Resolução final
  if (res.resultado === "vitoria") {
    const xpGanho = res.jogador.xp - (get().lastXpSnapshot ?? 0);
    if (xpGanho > 0) mensagens.push(`${res.jogador.nome} ganhou ${xpGanho} de XP!`);
    set({ animPhase: "victory" });
    appendDialog(set, get, mensagens);
    audio.playSfx("sfx_enemy_defeat");

    // Após dialog acabar + animação de faint + drenagem de HP, voltar ao menu.
    // 4500ms cobre: digitação (~2s) + faint (700ms) + drenagem HP (700ms) + leitura.
    scheduleTimeout(() => {
      set({ screen: "menu", animPhase: "idle", currentDialog: null, dialogQueue: [] });
      audio.playMusic("bgm_dungeon");
    }, 4500);
  } else if (res.resultado === "derrota") {
    set({ animPhase: "defeat" });
    appendDialog(set, get, [...mensagens, `${res.jogador.nome} foi derrotado...`]);
    scheduleTimeout(() => {
      set({
        screen: "game_over",
        gameOverMsg: `${res.jogador.nome} foi derrotado no andar ${res.jogador.andar}.`,
        animPhase: "idle",
        currentDialog: null,
        dialogQueue: [],
      });
      audio.playJingle("bgm_game_over");
    }, 3500);
  } else if (res.resultado === "fuga") {
    set({ animPhase: "flee" });
    appendDialog(set, get, mensagens);
    scheduleTimeout(() => {
      set({ screen: "menu", animPhase: "idle", currentDialog: null, dialogQueue: [] });
      audio.playMusic("bgm_dungeon");
    }, 2800);
  } else {
    // continua — enfileira mensagens; CombatScreen volta para idle quando dialog esvaziar
    set({ animPhase: "enemy_action" });
    appendDialog(set, get, mensagens);
    // Volta para idle após um tempo razoável; BattleDialog onQueueEmpty cuida do caso ideal
    scheduleTimeout(() => {
      const s = get();
      if (
        s.screen === "combat" &&
        s.inimigo &&
        s.inimigo.hp > 0 &&
        s.jogador &&
        s.jogador.hp > 0 &&
        s.animPhase !== "idle"
      ) {
        set({ animPhase: "idle" });
      }
    }, 1800);
  }
}
