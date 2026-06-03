import { useMemo } from "react";
import { useGameStore } from "../store/gameStore";
import { audio } from "../components/audio/AudioEngine";
import { getScores } from "../services/leaderboard";

/**
 * Tela de placar acessível pelo menu principal.
 * Mostra as melhores pontuações guardadas no localStorage (top-5, Lote H),
 * fora do fim da run. Somente leitura — o registro continua acontecendo no
 * GameOver/Victory.
 */
export function LeaderboardScreen() {
  const goToMainMenu = useGameStore((s) => s.goToMainMenu);
  const scores = useMemo(() => getScores(), []);

  const back = () => {
    audio.playSfx("sfx_menu_cancel");
    goToMainMenu();
  };

  const formatarData = (iso: string): string => {
    const d = new Date(iso);
    return isNaN(d.getTime()) ? "" : d.toLocaleDateString();
  };

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
        <h2 style={{ fontSize: "var(--font-size-md)", color: "#000" }}>PLACAR</h2>
        <button className="poke-btn" onClick={back} style={{ padding: "4px 10px" }}>
          VOLTAR
        </button>
      </div>

      {scores.length === 0 ? (
        <div className="poke-box" style={{ padding: "16px 12px", textAlign: "center" }}>
          <p style={{ fontSize: "var(--font-size-sm)", color: "#000" }}>
            Nenhuma pontuação ainda.
          </p>
          <p style={{ fontSize: "var(--font-size-xs)", color: "#555", marginTop: 6 }}>
            Termine uma run para entrar no placar!
          </p>
        </div>
      ) : (
        <div className="poke-box" style={{ fontSize: 7, color: "#000", padding: "10px 12px" }}>
          <p style={{ textAlign: "center", color: "#a06000", marginBottom: 6 }}>
            — MELHORES PONTUAÇÕES —
          </p>
          {scores.map((e, i) => (
            <div
              key={i}
              style={{
                display: "flex",
                justifyContent: "space-between",
                gap: 12,
                margin: "4px 0",
                fontWeight: i === 0 ? "bold" : "normal",
                color: i === 0 ? "#1a7f3c" : "#000",
              }}
            >
              <span>
                {i + 1}. {e.nome} ({e.modo === "story" ? "Camp." : "Inf."})
              </span>
              <span style={{ display: "flex", gap: 10 }}>
                <span style={{ color: "#555" }}>andar {e.andar}</span>
                <span style={{ color: "#999" }}>{formatarData(e.data)}</span>
                <span>{e.score}</span>
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
