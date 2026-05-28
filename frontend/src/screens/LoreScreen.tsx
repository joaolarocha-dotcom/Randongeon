import { useEffect, useState } from "react";
import { useGameStore } from "../store/gameStore";
import { TypewriterText } from "../components/TypewriterText";
import { audio } from "../components/audio/AudioEngine";

export function LoreScreen() {
  const { loreLinhas, fetchLore, goToMenu } = useGameStore();
  const [currentLine, setCurrentLine] = useState(0);
  const [showSkip, setShowSkip] = useState(true);

  useEffect(() => {
    fetchLore();
    audio.playMusic("bgm_dungeon");
    // fetchLore vem do Zustand store e é estável; rodar uma vez no mount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleLineComplete = () => {
    if (currentLine < loreLinhas.length - 1) {
      setTimeout(() => setCurrentLine((l) => l + 1), 300);
    } else {
      setShowSkip(true);
    }
  };

  if (loreLinhas.length === 0) return null;

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        padding: 18,
        gap: 8,
        background: "linear-gradient(180deg, #0a0a1a 0%, #1a1a2e 100%)",
      }}
    >
      <div className="poke-dialog" style={{ flex: 1, overflow: "auto" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
          {loreLinhas.slice(0, currentLine + 1).map((linha, i) => (
            <div key={i} style={{ fontSize: "var(--font-size-sm)", minHeight: 16, color: "#000" }}>
              {i === currentLine ? (
                <TypewriterText text={linha || " "} speed={30} onComplete={handleLineComplete} />
              ) : (
                <span style={{ color: "#444" }}>{linha || " "}</span>
              )}
            </div>
          ))}
        </div>
      </div>

      {showSkip && (
        <div style={{ textAlign: "center" }}>
          <button
            className="poke-btn"
            onClick={() => {
              audio.playSfx("sfx_menu_select");
              goToMenu();
            }}
          >
            CONTINUAR
          </button>
        </div>
      )}
    </div>
  );
}
