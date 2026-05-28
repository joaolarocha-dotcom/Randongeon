/**
 * AudioEngine — singleton de SFX + BGM.
 *
 * - SFX: cacheados em Map<path, HTMLAudioElement>.
 * - BGM: troca com fade-out leve; loop automático.
 * - Falha silenciosa se o arquivo não existir (catch em play()).
 * - Volume global controlável.
 *
 * Caminhos são resolvidos a partir de /assets/sounds/ (servido por Vite/public).
 */

const BASE = "/assets/sounds/";

// Mapa lógico → nome real do arquivo (tolerante a duplas extensões e renomes).
// Se o arquivo não existir, o engine apenas falha silenciosamente.
const SOUND_FILES: Record<string, string> = {
  // SFX
  sfx_menu_move: "sfx_menu_move.wav",
  sfx_menu_select: "sfx_menu_select.wav",
  sfx_menu_cancel: "sfx_menu_cancel.wav",
  sfx_attack_hit: "sfx_attack_hit.wav",
  sfx_critical_hit: "sfx_critical_hit.wav",
  sfx_attack_miss: "sfx_attack_miss.wav",
  sfx_hp_tick: "sfx_hp_tick.wav",
  sfx_enemy_defeat: "sfx_enemy_defeat.wav",
  sfx_level_up: "sfx_level_up.wav",
  sfx_chest_open: "sfx_chest_open.wav",
  sfx_item_get: "sfx_item_get.wav",
  sfx_shop_buy: "sfx_shop_buy.wav", // pode não existir; falha silenciosa
  sfx_flee_success: "sfx_flee_success.wav",
  sfx_flee_fail: "sfx_flee_fail.wav",
  sfx_dialog_blip: "sfx_dialog_blip.wav", // pode não existir
  sfx_floor_transition: "sfx_floor_transition.wav", // pode não existir

  // BGM (alguns têm dupla extensão no projeto atual; mapeados abaixo)
  bgm_title: "bgm_title.mp3",
  bgm_dungeon: "bgm_dungeon.mp3.mp3",
  bgm_battle_normal: "bgm_battle_normal 1.mp3",
  bgm_battle_normal_alt: "bgm_battle_normal 2.mp3",
  bgm_battle_boss: "bgm_battle_boss.mp3.mp3",
  bgm_victory: "bgm_victory.mp3", // pode não existir
  bgm_shop: "bgm_shop.mp3",
  bgm_game_over: "bgm_game_over.mp3.mp3",
};

class AudioEngine {
  private sfxCache = new Map<string, HTMLAudioElement>();
  private currentMusic: HTMLAudioElement | null = null;
  private currentMusicKey: string | null = null;
  /** Última música solicitada via playMusic/playJingle. Mantida mesmo após mute para permitir retomar. */
  private lastRequestedMusicKey: string | null = null;
  private musicVolume = 0.35;
  private sfxVolume = 0.5;
  private muted = false;
  private interactionListenerInstalled = false;

  private resolve(key: string): string | null {
    const file = SOUND_FILES[key];
    if (!file) return null;
    return BASE + file;
  }

  /**
   * Registra um listener once-only para retomar a BGM atual após a primeira interação do usuário.
   * Necessário porque browsers bloqueiam autoplay até o primeiro click/keypress.
   */
  private installInteractionListener() {
    if (this.interactionListenerInstalled) return;
    this.interactionListenerInstalled = true;
    const resume = () => {
      if (this.currentMusic && this.currentMusic.paused && !this.muted) {
        const p = this.currentMusic.play();
        if (p && typeof p.catch === "function") p.catch(() => {});
      }
    };
    window.addEventListener("click", resume, { once: false });
    window.addEventListener("keydown", resume, { once: false });
    window.addEventListener("touchstart", resume, { once: false });
  }

  /** Toca um SFX. Se o arquivo não existir, falha silenciosamente. */
  playSfx(key: string, volume?: number) {
    if (this.muted) return;
    const path = this.resolve(key);
    if (!path) return;

    let el = this.sfxCache.get(path);
    if (!el) {
      el = new Audio(path);
      el.preload = "auto";
      this.sfxCache.set(path, el);
    }
    try {
      el.currentTime = 0;
      el.volume = (volume ?? this.sfxVolume);
      const p = el.play();
      if (p && typeof p.catch === "function") p.catch(() => {});
    } catch {
      // silencioso
    }
  }

  /**
   * Toca uma BGM em loop. Se já estiver tocando a mesma faixa, não faz nada.
   * Faz fade-out simples da anterior em ~200ms.
   */
  playMusic(key: string, volume?: number) {
    this.lastRequestedMusicKey = key;
    if (this.muted) return;
    if (this.currentMusicKey === key && this.currentMusic && !this.currentMusic.paused) return;

    const path = this.resolve(key);
    if (!path) return;

    this.stopMusic();

    const el = new Audio(path);
    el.loop = true;
    el.volume = volume ?? this.musicVolume;
    el.preload = "auto";

    try {
      const p = el.play();
      if (p && typeof p.catch === "function") {
        p.catch(() => {
          // Browser bloqueou autoplay — instala listener para retomar na 1ª interação
          this.installInteractionListener();
        });
      }
    } catch {
      this.installInteractionListener();
    }

    this.currentMusic = el;
    this.currentMusicKey = key;
  }

  /** Toca uma faixa one-shot (não-loop). Para BGM atual e retoma depois? Não — apenas para. */
  playJingle(key: string, volume?: number) {
    this.lastRequestedMusicKey = key;
    if (this.muted) return;
    const path = this.resolve(key);
    if (!path) return;

    this.stopMusic();

    const el = new Audio(path);
    el.loop = false;
    el.volume = volume ?? this.musicVolume;
    try {
      const p = el.play();
      if (p && typeof p.catch === "function") p.catch(() => {});
    } catch {
      // silencioso
    }

    this.currentMusic = el;
    this.currentMusicKey = key;
  }

  stopMusic() {
    if (this.currentMusic) {
      try {
        this.currentMusic.pause();
        this.currentMusic.currentTime = 0;
      } catch {
        // silencioso
      }
    }
    this.currentMusic = null;
    this.currentMusicKey = null;
  }

  setMusicVolume(v: number) {
    this.musicVolume = Math.max(0, Math.min(1, v));
    if (this.currentMusic) this.currentMusic.volume = this.musicVolume;
  }

  setSfxVolume(v: number) {
    this.sfxVolume = Math.max(0, Math.min(1, v));
  }

  setMuted(muted: boolean) {
    const wasMuted = this.muted;
    this.muted = muted;
    if (muted) {
      this.stopMusic();
    } else if (wasMuted && this.lastRequestedMusicKey) {
      // Retoma a última música pedida ao desmutar.
      this.playMusic(this.lastRequestedMusicKey);
    }
  }

  isMuted() {
    return this.muted;
  }

  /** Pré-carrega um conjunto de SFX para evitar lag no primeiro play. */
  preload(keys: string[]) {
    keys.forEach((key) => {
      const path = this.resolve(key);
      if (!path) return;
      if (!this.sfxCache.has(path)) {
        const el = new Audio(path);
        el.preload = "auto";
        this.sfxCache.set(path, el);
      }
    });
  }
}

export const audio = new AudioEngine();
