import { useGameStore } from "../store/gameStore";
import { HPBar } from "../components/HPBar";

export function MenuScreen() {
  const { jogador, advance, quit, loading, descricaoSala } = useGameStore();

  if (!jogador) return null;

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        padding: 16,
        gap: 12,
      }}
    >
      {/* Status Panel */}
      <div className="pixel-box" style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: "var(--font-size-sm)" }}>
          <span>{jogador.nome}</span>
          <span>Andar {jogador.andar}</span>
        </div>
        <HPBar current={jogador.hp} max={jogador.hp_max} label="HP" />
        <div style={{ display: "flex", gap: 16, fontSize: "var(--font-size-sm)" }}>
          <span>ATK: {jogador.atk}</span>
          <span>ESQ: {Math.round(jogador.esq * 100)}%</span>
          <span>XP: {jogador.xp}</span>
          <span style={{ color: "var(--gold)" }}>$ {jogador.moedas}</span>
        </div>
      </div>

      {/* Room description */}
      {descricaoSala && (
        <div style={{ fontSize: "var(--font-size-sm)", color: "var(--text-dim)", textAlign: "center", padding: "8px 0" }}>
          {descricaoSala}
        </div>
      )}

      {/* Actions */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", gap: 12 }}>
        <button className="pixel-btn" onClick={advance} disabled={loading} style={{ width: 200 }}>
          AVANÇAR
        </button>
        <button className="pixel-btn" onClick={quit} disabled={loading} style={{ width: 200 }}>
          DESISTIR
        </button>
      </div>
    </div>
  );
}
