import type { SaveState } from "../api/client";

const PREFIX = "randongeon_save_";
const SLOTS = ["slot_1", "slot_2", "slot_3"] as const;
export type SaveSlot = (typeof SLOTS)[number];

export const SAVE_SLOTS: readonly SaveSlot[] = SLOTS;

export interface SaveMeta {
  slot: SaveSlot;
  state: SaveState | null;
}

function key(slot: SaveSlot): string {
  return PREFIX + slot;
}

export function listSaves(): SaveMeta[] {
  return SLOTS.map((slot) => ({ slot, state: getSave(slot) }));
}

export function getSave(slot: SaveSlot): SaveState | null {
  try {
    const raw = localStorage.getItem(key(slot));
    if (!raw) return null;
    const parsed = JSON.parse(raw) as SaveState;
    if (!parsed || typeof parsed !== "object" || !parsed.version) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function putSave(slot: SaveSlot, state: SaveState): void {
  localStorage.setItem(key(slot), JSON.stringify(state));
}

export function deleteSave(slot: SaveSlot): void {
  localStorage.removeItem(key(slot));
}

export function exportSaveToFile(state: SaveState): void {
  const blob = new Blob([JSON.stringify(state, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  const safeName = (state.playerName || "save").replace(/[^a-zA-Z0-9_-]/g, "_");
  a.href = url;
  a.download = `randongeon_${safeName}_andar${state.andar}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export async function importSaveFromFile(file: File): Promise<SaveState> {
  const text = await file.text();
  const data = JSON.parse(text) as SaveState;
  if (!data || typeof data !== "object" || !data.version || !data.jogador) {
    throw new Error("Arquivo de save inválido.");
  }
  return data;
}
