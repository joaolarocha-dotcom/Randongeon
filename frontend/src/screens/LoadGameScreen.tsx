import { useRef, useState } from "react";
import { useGameStore } from "../store/gameStore";
import {
  SAVE_SLOTS,
  type SaveSlot,
  deleteSave,
  exportSaveToFile,
  importSaveFromFile,
  listSaves,
  putSave,
} from "../services/saveService";
import { audio } from "../components/audio/AudioEngine";

export function LoadGameScreen() {
  const goToMainMenu = useGameStore((s) => s.goToMainMenu);
  const loadFromSave = useGameStore((s) => s.loadFromSave);
  const loading = useGameStore((s) => s.loading);
  const error = useGameStore((s) => s.error);

  const [tick, setTick] = useState(0);
  const refresh = () => setTick((t) => t + 1);
  const slots = listSaves();
  const fileRef = useRef<HTMLInputElement>(null);
  const [msg, setMsg] = useState<string | null>(null);

  const onLoad = async (slot: SaveSlot) => {
    const meta = slots.find((s) => s.slot === slot);
    if (!meta?.state) return;
    audio.playSfx("sfx_menu_select");
    await loadFromSave(meta.state);
  };

  const onDelete = (slot: SaveSlot) => {
    audio.playSfx("sfx_menu_cancel");
    if (!confirm(`Apagar save do ${slot}?`)) return;
    deleteSave(slot);
    refresh();
  };

  const onExport = (slot: SaveSlot) => {
    const meta = slots.find((s) => s.slot === slot);
    if (!meta?.state) return;
    audio.playSfx("sfx_menu_select");
    exportSaveToFile(meta.state);
  };

  const onImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const state = await importSaveFromFile(file);
      // Coloca no primeiro slot livre, ou no slot_1 sobrescrevendo
      const livre = SAVE_SLOTS.find((s) => !slots.find((m) => m.slot === s)?.state) ?? "slot_1";
      putSave(livre, state);
      setMsg(`Save importado para ${livre}.`);
      refresh();
    } catch (err) {
      setMsg(`Falha ao importar: ${(err as Error).message}`);
    } finally {
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const back = () => {
    audio.playSfx("sfx_menu_cancel");
    goToMainMenu();
  };

  // Subscreve em tick para reler a lista após mudanças
  void tick;

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        padding: 12,
        gap: 10,
        background: "var(--poke-bg)",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2 style={{ fontSize: "var(--font-size-md)", color: "#000" }}>CARREGAR JOGO</h2>
        <button className="poke-btn" onClick={back} style={{ padding: "4px 10px" }}>
          VOLTAR
        </button>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 8, flex: 1, overflowY: "auto" }}>
        {slots.map(({ slot, state }) => (
          <div key={slot} className="poke-box" style={{ padding: "8px 10px" }}>
            <div style={{ fontSize: "var(--font-size-sm)", marginBottom: 6 }}>
              <strong>{slot.toUpperCase()}</strong>
              {" "}
              {state
                ? `— ${state.playerName} · andar ${state.andar} · ${state.modo}`
                : "— vazio"}
            </div>
            <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
              <button
                className="poke-btn"
                onClick={() => onLoad(slot)}
                disabled={!state || loading}
                style={{ padding: "4px 10px" }}
              >
                CARREGAR
              </button>
              <button
                className="poke-btn"
                onClick={() => onExport(slot)}
                disabled={!state}
                style={{ padding: "4px 10px" }}
              >
                EXPORTAR
              </button>
              <button
                className="poke-btn"
                onClick={() => onDelete(slot)}
                disabled={!state}
                style={{ padding: "4px 10px" }}
              >
                APAGAR
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="poke-box" style={{ padding: "8px 10px" }}>
        <div style={{ fontSize: "var(--font-size-sm)", marginBottom: 6 }}>
          IMPORTAR ARQUIVO .txt
        </div>
        <input
          ref={fileRef}
          type="file"
          accept=".txt,.json,text/plain,application/json"
          onChange={onImport}
          style={{ fontSize: "var(--font-size-sm)" }}
        />
        {msg && (
          <p style={{ fontSize: "var(--font-size-sm)", marginTop: 6, color: "#000" }}>{msg}</p>
        )}
      </div>

      {error && (
        <p style={{ fontSize: "var(--font-size-sm)", color: "var(--hp-red)" }}>{error}</p>
      )}
    </div>
  );
}
