import { useEffect, useState } from "react";
import { useGameStore } from "../store/gameStore";
import { TypewriterText } from "../components/TypewriterText";

export function LoreScreen() {
  const { loreLinhas, fetchLore, goToMenu } = useGameStore();
  const [currentLine, setCurrentLine] = useState(0);
  const [showSkip, setShowSkip] = useState(true);

  useEffect(() => {
    fetchLore();
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
        padding: 24,
        overflow: "hidden",
      }}
    >
      <div style={{ flex: 1, overflow: "hidden", display: "flex", flexDirection: "column", gap: 4 }}>
        {loreLinhas.slice(0, currentLine + 1).map((linha, i) => (
          <div key={i} style={{ fontSize: "var(--font-size-sm)", minHeight: 16 }}>
            {i === currentLine ? (
              <TypewriterText text={linha || " "} speed={30} onComplete={handleLineComplete} />
            ) : (
              <span style={{ color: "var(--text-dim)" }}>{linha || " "}</span>
            )}
          </div>
        ))}
      </div>

      {showSkip && (
        <div style={{ textAlign: "center", paddingTop: 8 }}>
          <button className="pixel-btn" onClick={goToMenu}>
            CONTINUAR
          </button>
        </div>
      )}
    </div>
  );
}
