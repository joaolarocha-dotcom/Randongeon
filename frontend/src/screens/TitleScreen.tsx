import { useState, useEffect } from "react";
import { useGameStore } from "../store/gameStore";
import { LOGO_SPRITE, FALLBACK_SPRITE_PATH } from "../assets/spriteMap";
import { audio } from "../components/audio/AudioEngine";

export function TitleScreen() {
  const [nome, setNome] = useState("");
  const [logoSrc, setLogoSrc] = useState(LOGO_SPRITE.src);
  const { startGame, loading, error, pendingModo, goToMainMenu } = useGameStore();

  // Tenta tocar o BGM do título no primeiro mount; o browser pode bloquear
  // até o primeiro clique. O onClick do submit garante o playback.
  useEffect(() => {
    audio.playMusic("bgm_title");
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (nome.trim()) {
      audio.playSfx("sfx_menu_select");
      audio.playMusic("bgm_title");
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
        gap: 16,
        padding: 24,
        background: "linear-gradient(180deg, var(--poke-bg) 0%, #b0e0f8 100%)",
      }}
    >
      <img
        src={logoSrc}
        alt="RANDONGEON"
        onError={() => {
          if (logoSrc !== FALLBACK_SPRITE_PATH) setLogoSrc(FALLBACK_SPRITE_PATH);
        }}
        style={{
          width: 240,
          maxWidth: "80%",
          imageRendering: "pixelated",
        }}
        draggable={false}
      />

      <p style={{ fontSize: "var(--font-size-sm)", color: "#000", textShadow: "1px 1px 0 #fff" }}>
        {pendingModo === "infinite" ? "Modo Infinito" : "A Masmorra Sem Fim"}
      </p>

      <form
        onSubmit={handleSubmit}
        style={{ display: "flex", flexDirection: "column", gap: 12, alignItems: "center" }}
      >
        <label style={{ fontSize: "var(--font-size-sm)", color: "#000" }}>Nome do Herói:</label>
        <input
          type="text"
          value={nome}
          onChange={(e) => setNome(e.target.value)}
          maxLength={16}
          style={{
            fontFamily: "'Press Start 2P', monospace",
            fontSize: "var(--font-size-sm)",
            padding: "8px 12px",
            background: "#fff",
            color: "#000",
            border: "3px solid #000",
            borderRadius: 4,
            outline: "none",
            textAlign: "center",
            width: 200,
          }}
        />
        <div style={{ display: "flex", gap: 8 }}>
          <button
            className="poke-btn"
            type="button"
            onClick={() => {
              audio.playSfx("sfx_menu_cancel");
              goToMainMenu();
            }}
            disabled={loading}
          >
            VOLTAR
          </button>
          <button className="poke-btn" type="submit" disabled={loading || !nome.trim()}>
            {loading ? "..." : "INICIAR"}
          </button>
        </div>
      </form>

      {error && (
        <p style={{ fontSize: "var(--font-size-sm)", color: "var(--hp-red)" }}>{error}</p>
      )}
    </div>
  );
}
