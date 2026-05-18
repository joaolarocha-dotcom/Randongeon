import { useState } from "react";
import { useGameStore } from "../store/gameStore";

export function TitleScreen() {
  const [nome, setNome] = useState("");
  const { startGame, loading, error } = useGameStore();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (nome.trim()) {
      startGame(nome.trim());
    }
  };

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 24,
        padding: 24,
      }}
    >
      <h1
        style={{
          fontSize: "var(--font-size-lg)",
          color: "var(--border-color)",
          textAlign: "center",
          textShadow: "3px 3px 0px #000",
        }}
      >
        RANDONGEON
      </h1>

      <p style={{ fontSize: "var(--font-size-sm)", color: "var(--text-dim)" }}>
        A Masmorra Sem Fim
      </p>

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 12, alignItems: "center" }}>
        <label style={{ fontSize: "var(--font-size-sm)" }}>Nome do Herói:</label>
        <input
          type="text"
          value={nome}
          onChange={(e) => setNome(e.target.value)}
          maxLength={16}
          style={{
            fontFamily: "'Press Start 2P', monospace",
            fontSize: "var(--font-size-sm)",
            padding: "8px 12px",
            backgroundColor: "var(--bg-panel)",
            color: "var(--text-color)",
            border: "3px solid var(--border-color)",
            outline: "none",
            textAlign: "center",
            width: 200,
          }}
        />
        <button className="pixel-btn" type="submit" disabled={loading || !nome.trim()}>
          {loading ? "..." : "INICIAR"}
        </button>
      </form>

      {error && <p style={{ fontSize: "var(--font-size-sm)", color: "var(--hp-red)" }}>{error}</p>}
    </div>
  );
}
