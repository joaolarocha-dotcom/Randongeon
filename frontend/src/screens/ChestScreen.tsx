import { useGameStore } from "../store/gameStore";

export function ChestScreen() {
  const { descricaoSala, item, openChest, ignoreChest, loading } = useGameStore();

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 20,
        padding: 24,
      }}
    >
      {/* Chest sprite placeholder */}
      <div
        style={{
          width: 64,
          height: 64,
          backgroundColor: "var(--gold)",
          opacity: 0.8,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: "32px",
        }}
      >
        🎁
      </div>

      <p style={{ fontSize: "var(--font-size-sm)", textAlign: "center" }}>
        {descricaoSala}
      </p>

      {item && (
        <div className="pixel-box" style={{ fontSize: "var(--font-size-sm)" }}>
          <p style={{ color: "var(--gold)", marginBottom: 8 }}>{item.nome}</p>
          {item.bonus_atk > 0 && <p>ATK +{item.bonus_atk}</p>}
          {item.bonus_hp > 0 && <p>HP +{item.bonus_hp}</p>}
          {item.bonus_esq > 0 && <p>ESQ +{Math.round(item.bonus_esq * 100)}%</p>}
        </div>
      )}

      <div style={{ display: "flex", gap: 12 }}>
        <button className="pixel-btn" onClick={openChest} disabled={loading}>
          ABRIR
        </button>
        <button className="pixel-btn" onClick={ignoreChest} disabled={loading}>
          IGNORAR
        </button>
      </div>
    </div>
  );
}
