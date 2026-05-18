import { useGameStore } from "../store/gameStore";

export function GameOverScreen() {
  const { jogador, gameOverMsg, reset } = useGameStore();

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
      <h2
        style={{
          fontSize: "var(--font-size-lg)",
          color: "var(--hp-red)",
          textShadow: "2px 2px 0px #000",
        }}
      >
        GAME OVER
      </h2>

      <p style={{ fontSize: "var(--font-size-sm)", textAlign: "center" }}>
        {gameOverMsg}
      </p>

      {jogador && (
        <div className="pixel-box" style={{ fontSize: "var(--font-size-sm)", textAlign: "center" }}>
          <p>Andar alcançado: {jogador.andar}</p>
          <p>XP total: {jogador.xp}</p>
          <p style={{ color: "var(--gold)" }}>Moedas: {jogador.moedas}</p>
        </div>
      )}

      <button className="pixel-btn" onClick={reset}>
        JOGAR NOVAMENTE
      </button>
    </div>
  );
}
