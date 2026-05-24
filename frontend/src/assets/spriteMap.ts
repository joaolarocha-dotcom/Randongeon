/**
 * Mapa mestre de sprites do jogo.
 *
 * Convenção: as larguras/alturas aqui são as do PNG original (sem escala CSS).
 * Componentes podem multiplicar por 2x/3x/4x para escalar mantendo pixel art.
 *
 * Fallback: qualquer inimigo sem sprite mapeado cai para Goblin via getEnemySprite.
 * Robustez extra: componentes <img> devem usar onError para trocar src para o goblin.
 */

export const SPRITE_BASE = "/assets/sprites/";
export const FALLBACK_SPRITE_FILE = "goblin.png";
export const FALLBACK_SPRITE_PATH = SPRITE_BASE + FALLBACK_SPRITE_FILE;

export interface SpriteInfo {
  file: string;   // nome do arquivo dentro de /assets/sprites/
  w: number;      // largura nativa em pixels
  h: number;      // altura nativa em pixels
  src: string;    // caminho completo pronto para <img src>
}

function s(file: string, w: number, h: number): SpriteInfo {
  return { file, w, h, src: SPRITE_BASE + file };
}

// ─────────────────────────────────────────────────────────────────────────
// Protagonista
// ─────────────────────────────────────────────────────────────────────────
export const PLAYER_SPRITE: SpriteInfo = s("zeppeli - Protagonista (48x52).png", 48, 52);

// ─────────────────────────────────────────────────────────────────────────
// Inimigos por nome (chave = nome retornado pelo backend)
// ─────────────────────────────────────────────────────────────────────────
const ENEMY_SPRITES: Record<string, SpriteInfo> = {
  // Dificuldade 1
  "Goblin": s("goblin.png", 50, 50),
  "Rato Gigante": s("rato.png", 50, 50),
  "Zumbi": s("nosferatu.png", 50, 50), // Zumbi foi reskinado para Nosferatu

  // Dificuldade 2
  "Esqueleto Guerreiro": s("esqueleto.png", 60, 60),
  "Orc": s("orc.png", 60, 60),
  "Troll das Cavernas": s("troll.png", 70, 70),

  // Especial
  "Mímico": s("mímico.png", 50, 50),
};

// Boss genérico (qualquer inimigo com dificuldade === 3 usa este sprite)
export const BOSS_SPRITE: SpriteInfo = s("boss_demonio.png", 80, 80);

// Sprites de baú
export const CHEST_CLOSED: SpriteInfo = s("bau.png", 50, 50);
export const CHEST_OPEN: SpriteInfo = s("bau_aberto.png", 50, 50);

// Sprite de mercador
export const MERCHANT_SPRITE: SpriteInfo = s("mercador.png", 50, 100);

// ─────────────────────────────────────────────────────────────────────────
// Resolvers
// ─────────────────────────────────────────────────────────────────────────

/**
 * Retorna o sprite do inimigo. Se dificuldade === 3, retorna o boss.
 * Se o nome não estiver mapeado, retorna o goblin (fallback).
 */
export function getEnemySprite(nome: string, dificuldade: number): SpriteInfo {
  if (dificuldade === 3) return BOSS_SPRITE;
  const found = ENEMY_SPRITES[nome];
  if (found) return found;
  // Fallback
  return ENEMY_SPRITES["Goblin"];
}

// Logo + ícone de moeda
export const LOGO_SPRITE: SpriteInfo = s("logo_randongeon.png", 240, 80);
export const COIN_ICON: SpriteInfo = s("coin_icon.png", 16, 16);
