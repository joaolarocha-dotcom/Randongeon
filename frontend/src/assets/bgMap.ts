/**
 * Mapa de backgrounds da arena/cenário, em função do andar e tipo de sala.
 *
 * Assets disponíveis em /assets/sprites/:
 *   - bg_dungeon_stone.png  (andares 1-4)
 *   - bg_dungeon_crypt.png  (andares 6+, fallback geral)
 *   - bg_boss_throne.png    (boss/múltiplos de 5)
 *   - bg_chest_room.png     (ChestScreen)
 *   - bg_shop_interior.png  (ShopScreen)
 */

const BASE = "/assets/sprites/";

export const BG = {
  dungeonStone: BASE + "bg_dungeon_stone.png",
  dungeonCrypt: BASE + "bg_dungeon_crypt.png",
  bossThrone: BASE + "bg_boss_throne.png",
  chestRoom: BASE + "bg_chest_room.png",
  shopInterior: BASE + "bg_shop_interior.png",
} as const;

/** Retorna o background da arena de batalha para o andar/tipo. */
export function getArenaBg(andar: number, tipo?: string): string {
  if (tipo === "boss" || (andar > 0 && andar % 5 === 0)) {
    return BG.bossThrone;
  }
  if (andar <= 4) return BG.dungeonStone;
  // Sem bg_dungeon_lava no momento — usa crypt para todos os andares > 4
  return BG.dungeonCrypt;
}

/** Retorna a BGM apropriada (chave do AudioEngine) para o andar/tipo. */
export function getArenaMusic(andar: number, tipo?: string): string {
  if (tipo === "boss" || (andar > 0 && andar % 5 === 0)) {
    return "bgm_battle_boss";
  }
  // Alterna entre as duas faixas normais para variar
  return andar % 2 === 0 ? "bgm_battle_normal_alt" : "bgm_battle_normal";
}
