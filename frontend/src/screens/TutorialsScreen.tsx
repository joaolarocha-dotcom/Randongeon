import { useState } from "react";
import { useGameStore } from "../store/gameStore";
import { TUTORIAIS } from "../data/tutorials";
import { audio } from "../components/audio/AudioEngine";

export function TutorialsScreen() {
  const goToMainMenu = useGameStore((s) => s.goToMainMenu);
  const [page, setPage] = useState(0);

  const total = TUTORIAIS.length;
  const t = TUTORIAIS[page];

  const next = () => {
    audio.playSfx("sfx_menu_select");
    if (page < total - 1) setPage(page + 1);
  };
  const prev = () => {
    audio.playSfx("sfx_menu_cancel");
    if (page > 0) setPage(page - 1);
  };
  const back = () => {
    audio.playSfx("sfx_menu_cancel");
    goToMainMenu();
  };

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        padding: 16,
        gap: 12,
        background: "var(--poke-bg)",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontSize: "var(--font-size-sm)", color: "#000" }}>
          {page + 1}/{total}
        </span>
        <button className="poke-btn" onClick={back} style={{ padding: "4px 10px" }}>
          VOLTAR
        </button>
      </div>

      <div className="poke-dialog" style={{ flex: 1, overflowY: "auto" }}>
        <h2 style={{ fontSize: "var(--font-size-md)", marginBottom: 8 }}>{t.titulo}</h2>
        {t.paragrafos.map((p, i) => (
          <p key={i} style={{ fontSize: "var(--font-size-sm)", marginBottom: 8, lineHeight: 1.6 }}>
            {p}
          </p>
        ))}
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
        <button className="poke-btn" onClick={prev} disabled={page === 0} style={{ minWidth: 100 }}>
          ◀ ANTERIOR
        </button>
        <button
          className="poke-btn"
          onClick={next}
          disabled={page === total - 1}
          style={{ minWidth: 100 }}
        >
          PRÓXIMO ▶
        </button>
      </div>
    </div>
  );
}
