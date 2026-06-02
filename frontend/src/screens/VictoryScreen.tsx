import { useEffect, useState } from "react";
import { useGameStore } from "../store/gameStore";
import { PLAYER_SPRITE, FALLBACK_SPRITE_PATH } from "../assets/spriteMap";
import { audio } from "../components/audio/AudioEngine";

/**
 * Tela de vitória da campanha (Lote G).
 * Disparada quando o backend retorna resultado="vitoria_campanha" (boss final
 * do andar 20 derrotado). Mostra o herói, os status finais e a pontuação.
 */
export function VictoryScreen() {
  const { jogador, victoryMsg, reset } = useGameStore();
  const [playerSrc, setPlayerSrc] = useState(PLAYER_SPRITE.src);

  useEffect(() => {
    audio.playJingle("bgm_victory");
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
        gap: 14,
        padding: 24,
        background: "linear-gradient(180deg, #2a2410 0%, #0a0a14 100%)",
      }}
    >
      <div style={{ fontSize: 56, lineHeight: 1 }}>🏆</div>

      <h2
        style={{
          fontSize: "var(--font-size-lg)",
          color: "#ffd84d",
          textShadow: "2px 2px 0 #a06000",
          letterSpacing: 2,
          textAlign: "center",
        }}
      >
        VITÓRIA!
      </h2>

      <img
        src={playerSrc}
        alt="Herói vitorioso"
        className="fade-in"
        onError={() => {
          if (playerSrc !== FALLBACK_SPRITE_PATH) setPlayerSrc(FALLBACK_SPRITE_PATH);
        }}
        style={{
          width: PLAYER_SPRITE.w * 2,
          height: PLAYER_SPRITE.h * 2,
          imageRendering: "pixelated",
          filter: "drop-shadow(0 0 8px #ffd84d)",
        }}
        draggable={false}
      />

      <p style={{ fontSize: "var(--font-size-sm)", color: "#eee", textAlign: "center", maxWidth: 420 }}>
        {victoryMsg || "A masmorra foi conquistada!"}
      </p>

      {jogador && (
        <div className="poke-box" style={{ fontSize: 7, textAlign: "center", color: "#000", minWidth: 180 }}>
          <p style={{ color: "#a06000" }}>{jogador.nome} — Andar 20 conquistado</p>
          <p>Nível: {jogador.nivel}</p>
          <p>XP total: {jogador.xp}</p>
          <p style={{ color: "#d8a000" }}>Moedas: {jogador.moedas}</p>
          <p style={{ color: "#1a7f3c" }}>Pontuação: {jogador.pontuacao}</p>
        </div>
      )}

      <button
        className="poke-btn"
        onClick={() => {
          audio.playSfx("sfx_menu_select");
          reset();
        }}
      >
        MENU PRINCIPAL
      </button>
    </div>
  );
}
