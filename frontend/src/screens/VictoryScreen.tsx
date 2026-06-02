import { useEffect, useRef, useState } from "react";
import { useGameStore } from "../store/gameStore";
import { PLAYER_SPRITE, FALLBACK_SPRITE_PATH } from "../assets/spriteMap";
import { audio } from "../components/audio/AudioEngine";
import { recordScore } from "../services/leaderboard";

/**
 * Tela de vitória da campanha (Lote G).
 * Disparada quando o backend retorna resultado="vitoria_campanha" (boss final
 * do andar 20 derrotado). Mostra o herói, os status finais, a pontuação e o
 * score da run (Lote H), registrando-a no placar.
 */
export function VictoryScreen() {
  const { jogador, victoryMsg, reset, modo } = useGameStore();
  const [playerSrc, setPlayerSrc] = useState(PLAYER_SPRITE.src);
  const [novoRecorde, setNovoRecorde] = useState(false);
  const registrado = useRef(false);

  useEffect(() => {
    audio.playJingle("bgm_victory");
    if (!registrado.current && jogador) {
      registrado.current = true;
      const r = recordScore({
        nome: jogador.nome,
        score: jogador.score,
        andar: jogador.andar,
        modo,
        data: new Date().toISOString(),
      });
      setNovoRecorde(r.novoRecorde);
    }
    return () => {
      audio.stopMusic();
    };
  }, [jogador, modo]);

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
          <p style={{ color: "#1a7f3c" }}>PONTUAÇÃO (score): {jogador.score}</p>
        </div>
      )}

      {novoRecorde && (
        <p style={{ fontSize: "var(--font-size-sm)", color: "#ffd84d", textShadow: "1px 1px 0 #a06000" }}>
          🏆 NOVO RECORDE!
        </p>
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
