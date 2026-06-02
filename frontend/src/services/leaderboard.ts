/**
 * Placar local (Lote H) — guarda as melhores runs no localStorage.
 * Serve de comparativo de competição (sobretudo no modo infinito).
 */
import type { Modo } from "../api/client";

export interface ScoreEntry {
  nome: string;
  score: number;
  andar: number;
  modo: Modo;
  data: string; // ISO date
}

const STORAGE_KEY = "randongeon_leaderboard";
const TOP_N = 5;

export function getScores(): ScoreEntry[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as ScoreEntry[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export interface RecordResult {
  /** true se entrou no top-N. */
  entrouNoPlacar: boolean;
  /** true se é a nova melhor pontuação (#1). */
  novoRecorde: boolean;
  /** posição (1-based) no placar, ou null se não entrou. */
  posicao: number | null;
  placar: ScoreEntry[];
}

/**
 * Registra uma run e devolve o placar atualizado + se foi recorde.
 * Mantém apenas as TOP_N melhores pontuações.
 */
export function recordScore(entry: ScoreEntry): RecordResult {
  const anteriores = getScores();
  const melhorAntes = anteriores.length ? anteriores[0].score : -1;

  const todas = [...anteriores, entry].sort((a, b) => b.score - a.score);
  const placar = todas.slice(0, TOP_N);

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(placar));
  } catch {
    // localStorage indisponível: segue sem persistir
  }

  const posicaoIdx = placar.findIndex((e) => e === entry);
  return {
    entrouNoPlacar: posicaoIdx !== -1,
    novoRecorde: entry.score > melhorAntes,
    posicao: posicaoIdx === -1 ? null : posicaoIdx + 1,
    placar,
  };
}
