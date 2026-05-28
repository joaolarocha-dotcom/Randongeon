import { useEffect, useState } from "react";
import { useGameStore } from "../store/gameStore";
import { PLAYER_SPRITE, FALLBACK_SPRITE_PATH } from "../assets/spriteMap";
import { audio } from "../components/audio/AudioEngine";

export function GameOverScreen() {
  const { jogador, gameOverMsg, reset } = useGameStore();
  const [playerSrc, setPlayerSrc] = useState(PLAYER_SPRITE.src);

  useEffect(() => {
    audio.playJingle("bgm_game_over");
    return () => {
      audio.stopMusic();
    };
  }, []);

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
        background: "linear-gradient(180deg, #1a1a2e 0%, #000 100%)",
      }}
    >
      <img
        src={playerSrc}
        alt="Herói desmaiado"
        className="fade-in"
        onError={() => {
          if (playerSrc !== FALLBACK_SPRITE_PATH) setPlayerSrc(FALLBACK_SPRITE_PATH);
        }}
        style={{
          width: PLAYER_SPRITE.w * 2,
          height: PLAYER_SPRITE.h * 2,
          imageRendering: "pixelated",
          filter: "grayscale(80%) brightness(0.5)",
          opacity: 0.7,
        }}
        draggable={false}
      />

      <h2
        style={{
          fontSize: "var(--font-size-lg)",
          color: "#fff",
          textShadow: "2px 2px 0 #e94560",
          letterSpacing: 2,
        }}
      >
        GAME OVER
      </h2>

      <p style={{ fontSize: "var(--font-size-sm)", color: "#ccc", textAlign: "center" }}>
        {gameOverMsg}
      </p>

      {jogador && (
        <div className="poke-box" style={{ fontSize: 7, textAlign: "center", color: "#000" }}>
          <p>Andar alcançado: {jogador.andar}</p>
          <p>XP total: {jogador.xp}</p>
          <p style={{ color: "#d8a000" }}>Moedas: {jogador.moedas}</p>
        </div>
      )}

      <button
        className="poke-btn"
        onClick={() => {
          audio.playSfx("sfx_menu_select");
          reset();
        }}
      >
        JOGAR NOVAMENTE
      </button>
    </div>
  );
}
