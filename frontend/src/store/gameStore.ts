import { create } from "zustand";
import { api, isSessionLost } from "../api/client";
import type {
  JogadorStatus,
  InimigoInfo,
  ItemInfo,
  LojaInfo,
  CombatActionResponse,
  Modo,
  SaveState,
} from "../api/client";
import { audio } from "../components/audio/AudioEngine";
import { getArenaMusic } from "../assets/bgMap";

function errorMessage(e: unknown): string {
  if (e instanceof Error) return e.message;
  if (typeof e === "string") return e;
  return "Erro desconhecido";
}

/** Aviso mostrado ao usuário quando a run é encerrada por perda de sessão. */
const SESSION_LOST_MSG =
  "Sua sessão expirou (o servidor foi reiniciado). Inicie uma nova run.";

function normalizeJogador(jogador: JogadorStatus): JogadorStatus {
  return {
    ...jogador,
    nivel: jogador.nivel ?? Math.max(1, Math.floor(jogador.xp / 50) + 1),
  };
}

function pick<T>(opcoes: T[]): T {
  return opcoes[Math.floor(Math.random() * opcoes.length)];
}

/**
 * Monta as falas de abertura do combate.
 *
 * Tom: sombrio com toques de humor. Cada tipo de inimigo (e o boss) tem suas
 * próprias linhas, escolhidas ao acaso para a entrada não ficar repetitiva —
 * substitui o antigo "Um X selvagem apareceu! / Vai, fulano!" estilo Pokémon.
 */
function buildEnemyIntro(
  inimigo: InimigoInfo,
  jogador: JogadorStatus,
  tipo: "inimigo" | "boss"
): string[] {
  const nome = inimigo.nome;

  if (tipo === "boss" || inimigo.dificuldade === 3) {
    return pick<string[]>([
      [`${nome} ergue-se das sombras. O ar fica pesado.`, `A saída desaparece atrás de você. Boa sorte — vai precisar.`],
      [`${nome} encara você sem nenhuma pressa.`, `Não há para onde correr desta vez, ${jogador.nome}.`],
      [`O chão treme: ${nome} despertou.`, `Respira fundo. Pode ser o último fôlego.`],
    ]);
  }

  switch (inimigo.tipo_especial) {
    case "nosferatu":
      return pick<string[]>([
        [`${nome} desperta com a sede de sempre.`, `Ele observa seu pescoço com um sorriso paciente.`],
        [`Um ${nome} emerge entre os caixões.`, `"Sangue novo", ele sussurra. Que gentil.`],
      ]);
    case "golem":
      return pick<string[]>([
        [`Um ${nome} se levanta — a rocha range como ossos antigos.`, `Bater nele vai doer mais em você do que nele.`],
        [`${nome} bloqueia o corredor. Literalmente.`],
      ]);
    case "banshee":
      return pick<string[]>([
        [`O lamento de uma ${nome} corta o ar.`, `Tapar os ouvidos não vai adiantar muito.`],
        [`Uma ${nome} flutua à sua frente, chorando.`, `Não é de tristeza. É de fome.`],
      ]);
    case "horda":
      return pick<string[]>([
        [`Goblins irrompem de todos os cantos.`, `Eles mal sabem contar até três, mas sabem te cercar.`],
        [`Uma horda de goblins range os dentes.`, `Um de cada vez — por pura falta de educação.`],
      ]);
    default:
      return pick<string[]>([
        [`Um ${nome} bloqueia seu caminho.`],
        [`${nome} surge das sombras, faminto.`],
        [`Algo se arrasta no escuro: um ${nome}.`],
        [`Um ${nome} range os dentes e avança.`],
      ]);
  }
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
  | "main_menu"
  | "tutorials"
  | "load_game"
  | "settings"
  | "leaderboard"
  | "title"
  | "lore"
  | "menu"
  | "advancing"
  | "combat"
  | "chest"
  | "shop"
  | "game_over"
  | "victory";

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
  modo: Modo;
  pendingModo: Modo;
  jogador: JogadorStatus | null;
  inimigo: InimigoInfo | null;
  item: ItemInfo | null;
  loja: LojaInfo | null;
  loreLinhas: string[];
  combatLog: CombatLog[];
  descricaoSala: string;
  gameOverMsg: string;
  victoryMsg: string;
  loading: boolean;
  error: string | null;

  // Estado de animação
  animPhase: AnimPhase;
  /** HP exibido (anima rumo a jogador.hp). */
  displayedPlayerHP: number;
  /** HP exibido (anima rumo a inimigo.hp). */
  displayedEnemyHP: number;
  /** Lote 4b: boss em 2ª fase/fúria (Coração da Masmorra renasceu). */
  bossEnraged: boolean;
  /** Fila de mensagens a exibir na BattleDialog. */
  dialogQueue: string[];
  /** Mensagem atual sendo digitada (null = nenhuma). */
  currentDialog: string | null;
  /** Transição de andar ativa. Se !== null, FloorTransition é mostrado. */
  floorTransitionAndar: number | null;
  /** XP no início do último combate (para calcular ganho). */
  lastXpSnapshot: number;

  // Navegação de telas (fora do jogo)
  goToMainMenu: () => void;
  goToTutorials: () => void;
  goToLoadGame: () => void;
  goToSettings: () => void;
  goToLeaderboard: () => void;
  goToTitle: (modo?: Modo) => void;

  // Actions principais (jogo)
  startGame: (nome: string, dom?: string | null) => Promise<void>;
  loadFromSave: (save: SaveState) => Promise<void>;
  fetchLore: () => Promise<void>;
  goToMenu: () => void;
  advance: () => Promise<void>;
  combatAttack: () => Promise<void>;
  combatDodge: () => Promise<void>;
  combatFlee: () => Promise<void>;
  combatUseItem: (indice: number) => Promise<void>;
  openChest: () => Promise<void>;
  ignoreChest: () => Promise<void>;
  shopBuy: (indice: number) => Promise<void>;
  shopLeave: () => Promise<void>;
  quit: () => Promise<void>;
  /** Aborta a run atual e volta ao menu principal sem game-over. */
  exitToMainMenu: () => Promise<void>;
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
  screen: "main_menu",
  sessionId: null,
  modo: "story",
  pendingModo: "story",
  jogador: null,
  inimigo: null,
  item: null,
  loja: null,
  loreLinhas: [],
  combatLog: [],
  descricaoSala: "",
  gameOverMsg: "",
  victoryMsg: "",
  loading: false,
  error: null,

  animPhase: "idle",
  displayedPlayerHP: 0,
  displayedEnemyHP: 0,
  bossEnraged: false,
  dialogQueue: [],
  currentDialog: null,
  floorTransitionAndar: null,
  lastXpSnapshot: 0,

  // ───────── Navegação ─────────

  goToMainMenu: () => {
    cancelAllTimeouts();
    set({ screen: "main_menu", error: null });
    audio.playMusic("bgm_title");
  },
  goToTutorials: () => set({ screen: "tutorials" }),
  goToLoadGame: () => set({ screen: "load_game" }),
  goToSettings: () => set({ screen: "settings" }),
  goToLeaderboard: () => set({ screen: "leaderboard" }),
  goToTitle: (modo: Modo = "story") => set({ screen: "title", pendingModo: modo, error: null }),

  // ───────── Jogo ─────────

  startGame: async (nome: string, dom: string | null = null) => {
    set({ loading: true, error: null });
    try {
      const modo = get().pendingModo;
      const res = await api.newGame(nome, modo, dom);
      const jogador = normalizeJogador(res.jogador);
      set({
        sessionId: res.session_id,
        modo: res.modo,
        jogador,
        displayedPlayerHP: jogador.hp,
        screen: "lore",
        loading: false,
      });
      audio.playMusic("bgm_title");
    } catch (e) {
      if (isSessionLost(e)) { get().reset(); set({ error: SESSION_LOST_MSG }); return; }
      set({ error: errorMessage(e), loading: false });
    }
  },

  loadFromSave: async (save) => {
    set({ loading: true, error: null });
    try {
      const res = await api.loadGame(save);
      const jogador = normalizeJogador(res.jogador);
      set({
        sessionId: res.session_id,
        modo: res.modo,
        jogador,
        displayedPlayerHP: jogador.hp,
        screen: "menu",
        loading: false,
      });
      audio.playMusic("bgm_dungeon");
    } catch (e) {
      if (isSessionLost(e)) { get().reset(); set({ error: SESSION_LOST_MSG }); return; }
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
      const jogadorAtualizado = normalizeJogador(res.jogador);
      set({
        jogador: jogadorAtualizado,
        displayedPlayerHP: jogadorAtualizado.hp,
        descricaoSala: res.descricao,
        floorTransitionAndar: null,
      });

      if (res.tipo === "inimigo" || res.tipo === "boss") {
        const inimigo = res.inimigo!;
        const intro = buildEnemyIntro(inimigo, jogadorAtualizado, res.tipo);
        set({
          inimigo,
          displayedEnemyHP: inimigo.hp_max,
          bossEnraged: false,        // Lote 4b: começa sem fúria; só após renascer
          screen: "combat",
          loading: false,
          animPhase: "intro",
          // Inicia com o primeiro item e enfileira o resto
          currentDialog: intro[0],
          dialogQueue: intro.slice(1),
          lastXpSnapshot: jogadorAtualizado.xp,
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
      if (isSessionLost(e)) { get().reset(); set({ error: SESSION_LOST_MSG }); return; }
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
      if (isSessionLost(e)) { get().reset(); set({ error: SESSION_LOST_MSG }); return; }
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
      if (isSessionLost(e)) { get().reset(); set({ error: SESSION_LOST_MSG }); return; }
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
      if (isSessionLost(e)) { get().reset(); set({ error: SESSION_LOST_MSG }); return; }
      set({ error: errorMessage(e), loading: false, animPhase: "idle" });
    }
  },

  combatUseItem: async (indice: number) => {
    const { sessionId } = get();
    if (!sessionId) return;
    audio.playSfx("sfx_item_get");
    set({ loading: true });
    try {
      const res = await api.inventoryUse(sessionId, indice);
      const jogadorAtualizado = normalizeJogador(res.jogador);
      set({
        jogador: jogadorAtualizado,
        loading: false,
      });
      get().enqueueDialog(res.mensagem);
    } catch (e) {
      if (isSessionLost(e)) { get().reset(); set({ error: SESSION_LOST_MSG }); return; }
      set({ error: errorMessage(e), loading: false });
    }
  },

  openChest: async () => {
    const { sessionId } = get();
    if (!sessionId) return;
    audio.playSfx("sfx_chest_open");
    set({ loading: true });
    try {
      const res = await api.chestOpen(sessionId);
      const jogadorAtualizado = normalizeJogador(res.jogador);
      set({ jogador: jogadorAtualizado, displayedPlayerHP: jogadorAtualizado.hp, loading: false });
      if (res.tipo === "mimico") {
        const inimigo = res.inimigo!;
        const intro = [res.mensagem, `O baú tinha dentes — e fome. O ${inimigo.nome} avança!`];
        set({
          inimigo,
          displayedEnemyHP: inimigo.hp_max,
          screen: "combat",
          combatLog: [{ mensagem: res.mensagem, tipo: "info" }],
          animPhase: "intro",
          currentDialog: intro[0],
          dialogQueue: intro.slice(1),
          lastXpSnapshot: jogadorAtualizado.xp,
        });
        // Mímico em andar de boss usa BGM de boss; senão, BGM normal
        audio.playMusic(getArenaMusic(jogadorAtualizado.andar));
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
      if (isSessionLost(e)) { get().reset(); set({ error: SESSION_LOST_MSG }); return; }
      set({ error: errorMessage(e), loading: false });
    }
  },

  ignoreChest: async () => {
    const { sessionId } = get();
    if (!sessionId) return;
    audio.playSfx("sfx_menu_cancel");
    const res = await api.chestIgnore(sessionId);
    const jogadorAtualizado = normalizeJogador(res.jogador);
    set({ jogador: jogadorAtualizado, displayedPlayerHP: jogadorAtualizado.hp, screen: "menu" });
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
      const jogadorAtualizado = normalizeJogador(res.jogador);
      set({
        jogador: jogadorAtualizado,
        displayedPlayerHP: jogadorAtualizado.hp,
        loja: res.loja || null,
        loading: false,
      });
      if (!res.loja) {
        set({ screen: "menu" });
        audio.playMusic("bgm_dungeon");
      }
    } catch (e) {
      if (isSessionLost(e)) { get().reset(); set({ error: SESSION_LOST_MSG }); return; }
      set({ error: errorMessage(e), loading: false });
    }
  },

  shopLeave: async () => {
    const { sessionId } = get();
    if (!sessionId) return;
    audio.playSfx("sfx_menu_cancel");
    const res = await api.shopLeave(sessionId);
    const jogadorAtualizado = normalizeJogador(res.jogador);
    set({ jogador: jogadorAtualizado, displayedPlayerHP: jogadorAtualizado.hp, loja: null, screen: "menu" });
    audio.playMusic("bgm_dungeon");
  },

  quit: async () => {
    const { sessionId, jogador } = get();
    cancelAllTimeouts();
    // Sem sessão: encerra para o menu sem travar.
    if (!sessionId) {
      get().reset();
      return;
    }
    try {
      const res = await api.quit(sessionId);
      const jogadorAtualizado = normalizeJogador(res.jogador);
      set({ gameOverMsg: res.mensagem, jogador: jogadorAtualizado, screen: "game_over" });
      audio.playJingle("bgm_game_over");
    } catch (e) {
      // Sessão perdida (servidor reiniciou): volta ao menu com aviso.
      if (isSessionLost(e)) {
        get().reset();
        set({ error: SESSION_LOST_MSG });
        return;
      }
      // Qualquer outra falha: ainda assim encerra a run para o game over,
      // usando o estado local — DESISTIR nunca deve ficar sem efeito.
      set({
        gameOverMsg: `${jogador?.nome ?? "Você"} desistiu da jornada.`,
        screen: "game_over",
      });
      audio.playJingle("bgm_game_over");
    }
  },

  exitToMainMenu: async () => {
    const { sessionId } = get();
    cancelAllTimeouts();
    if (sessionId) {
      // Encerra a sessão no backend; ignora erro caso a sessão já tenha sumido.
      try {
        await api.quit(sessionId);
      } catch {
        // silencioso
      }
    }
    get().reset();
  },

  reset: () => {
    audio.stopMusic();
    cancelAllTimeouts();
    set({
      screen: "main_menu",
      sessionId: null,
      modo: "story",
      pendingModo: "story",
      jogador: null,
      inimigo: null,
      item: null,
      loja: null,
      loreLinhas: [],
      combatLog: [],
      descricaoSala: "",
      gameOverMsg: "",
      victoryMsg: "",
      loading: false,
      error: null,
      animPhase: "idle",
      displayedPlayerHP: 0,
      displayedEnemyHP: 0,
      bossEnraged: false,
      dialogQueue: [],
      currentDialog: null,
      floorTransitionAndar: null,
      lastXpSnapshot: 0,
    });
    audio.playMusic("bgm_title");
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
  const nivelAntes = get().jogador?.nivel ?? 1;   // p/ detectar level-up
  const tipo: CombatLog["tipo"] =
    res.resultado === "vitoria"
      ? "vitoria"
      : res.resultado === "derrota"
      ? "derrota"
      : res.resultado === "fuga"
      ? "fuga"
      : "dano";

  const newLog: CombatLog[] = [...log, { mensagem: res.mensagem, tipo }];
  const jogadorAtualizado = normalizeJogador(res.jogador);
  const subiuNivel = jogadorAtualizado.nivel > nivelAntes;   // Lote 6/feedback

  // Atualiza dados base (sem mexer no displayed HP — barras animam separadamente).
  // Lote E: no "proximo" (novo goblin do bando), reseta a barra de HP exibida
  // para o HP cheio do novo inimigo — senão ela animaria do goblin morto (~0)
  // para o HP do novo, parecendo uma cura.
  set({
    jogador: jogadorAtualizado,
    inimigo: res.inimigo ?? null,
    combatLog: newLog,
    loading: false,
    ...(res.resultado === "proximo" && res.inimigo
      ? { displayedEnemyHP: res.inimigo.hp_max }
      : {}),
  });
  if (res.resultado === "proximo") {
    audio.playSfx("sfx_enemy_defeat");   // um goblin caiu; o próximo avança
  }

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

  // Lote 6/feedback: subiu de nível neste combate → toca o jingle de level-up
  // (a mensagem comemorativa já vem em res.mensagem, vinda da API).
  if (subiuNivel) {
    scheduleTimeout(() => audio.playSfx("sfx_level_up"), 650);
  }

  // Enfileira mensagens
  const mensagens = splitMensagem(res.mensagem);

  // Resolução final
  if (res.resultado === "vitoria_campanha") {
    // Lote G: boss final do andar 20 derrotado → tela de vitória da campanha.
    set({ animPhase: "victory", victoryMsg: res.mensagem });
    appendDialog(set, get, mensagens);
    audio.playSfx("sfx_enemy_defeat");
    scheduleTimeout(() => {
      set({ screen: "victory", animPhase: "idle", currentDialog: null, dialogQueue: [] });
      audio.playJingle("bgm_victory");
    }, 4000);
  } else if (res.resultado === "vitoria") {
    const xpGanho = jogadorAtualizado.xp - (get().lastXpSnapshot ?? 0);
    if (xpGanho > 0) mensagens.push(`${jogadorAtualizado.nome} ganhou ${xpGanho} de XP!`);
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
    appendDialog(set, get, [...mensagens, `${jogadorAtualizado.nome} foi derrotado...`]);
    scheduleTimeout(() => {
      set({
        screen: "game_over",
        gameOverMsg: `${jogadorAtualizado.nome} foi derrotado no andar ${jogadorAtualizado.andar}.`,
        animPhase: "idle",
        currentDialog: null,
        dialogQueue: [],
      });
      audio.playJingle("bgm_game_over");
    }, 3500);
  } else if (res.resultado === "renasceu") {
    // Lote 4b: o Coração da Masmorra renasceu (2ª fase). NÃO abrir a tela de
    // vitória — a luta continua. O boss volta a ~50% (a barra sobe rumo a
    // inimigo.hp) e entra em fúria (badge no status do inimigo).
    set({ animPhase: "enemy_action", bossEnraged: true });
    appendDialog(set, get, mensagens);
    audio.playSfx("sfx_enemy_defeat");                 // o golpe derruba o boss…
    scheduleTimeout(() => audio.playSfx("sfx_level_up"), 450);  // …e ele ressurge em fúria
    // Volta ao idle quando o diálogo esvaziar (fallback, igual ao "continua").
    scheduleTimeout(() => {
      const s = get();
      if (s.screen === "combat" && s.inimigo && s.inimigo.hp > 0 &&
          s.jogador && s.jogador.hp > 0 && s.animPhase !== "idle") {
        set({ animPhase: "idle" });
      }
    }, 1800);
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
