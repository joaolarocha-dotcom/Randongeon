import { useEffect, useState } from "react";
import { useGameStore } from "../store/gameStore";
import { LOGO_SPRITE, FALLBACK_SPRITE_PATH } from "../assets/spriteMap";
import { audio } from "../components/audio/AudioEngine";

export function MainMenuScreen() {
  const goToTitle = useGameStore((s) => s.goToTitle);
  const goToTutorials = useGameStore((s) => s.goToTutorials);
  const goToLoadGame = useGameStore((s) => s.goToLoadGame);
  const goToSettings = useGameStore((s) => s.goToSettings);
  const goToLeaderboard = useGameStore((s) => s.goToLeaderboard);
  const [logoSrc, setLogoSrc] = useState(LOGO_SPRITE.src);

  useEffect(() => {
    audio.playMusic("bgm_title");
  }, []);

  const click = (fn: () => void) => () => {
    audio.playSfx("sfx_menu_select");
    fn();
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
        style={{ width: 240, maxWidth: "70%", imageRendering: "pixelated" }}
        draggable={false}
      />
      <p style={{ fontSize: "var(--font-size-sm)", color: "#000", textShadow: "1px 1px 0 #fff" }}>
        A Masmorra Sem Fim
      </p>

      <div style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: 8, minWidth: 220 }}>
        <button className="poke-btn" onClick={click(() => goToTitle("story"))}>
          NOVO JOGO
        </button>
        <button className="poke-btn" onClick={click(() => goToTitle("infinite"))}>
          MODO INFINITO
        </button>
        <button className="poke-btn" onClick={click(goToLoadGame)}>
          CARREGAR JOGO
        </button>
        <button className="poke-btn" onClick={click(goToTutorials)}>
          TUTORIAIS
        </button>
        <button className="poke-btn" onClick={click(goToLeaderboard)}>
          VER PLACAR
        </button>
        <button className="poke-btn" onClick={click(goToSettings)}>
          CONFIGURAÇÕES
        </button>
      </div>
    </div>
  );
}
