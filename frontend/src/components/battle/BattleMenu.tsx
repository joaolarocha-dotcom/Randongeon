import { useState, useEffect } from "react";
import { audio } from "../audio/AudioEngine";

interface MenuItem {
  label: string;
  onClick: () => void;
  disabled?: boolean;
  /** Tooltip ou hint mostrado quando hover/active */
  hint?: string;
}

interface Props {
  items: MenuItem[];
  /** Mostra um prompt acima do menu, tipo "O que ZEPPELI vai fazer?" */
  prompt?: string;
}

/**
 * Menu Pokemon-style 2x2 com cursor ▶ navegável por teclado (setas + Enter).
 */
export function BattleMenu({ items, prompt }: Props) {
  const [active, setActive] = useState(0);

  // Navegação por teclado
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (items.length === 0) return;
      const cols = 2;
      let next: number;
      if (e.key === "ArrowRight") next = (active + 1) % items.length;
      else if (e.key === "ArrowLeft") next = (active - 1 + items.length) % items.length;
      else if (e.key === "ArrowDown") next = (active + cols) % items.length;
      else if (e.key === "ArrowUp") next = (active - cols + items.length) % items.length;
      else if (e.key === "Enter" || e.key === " ") {
        const item = items[active];
        if (item && !item.disabled) {
          e.preventDefault();
          item.onClick();
        }
        return;
      } else {
        return;
      }
      if (next !== active) {
        audio.playSfx("sfx_menu_move", 0.3);
        setActive(next);
        e.preventDefault();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [active, items]);

  return (
    <div className="poke-dialog" style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      {prompt && (
        <div style={{ fontSize: "var(--font-size-sm)" }}>{prompt}</div>
      )}
      <div className="poke-action-grid">
        {items.map((item, i) => (
          <button
            key={i}
            className="poke-btn"
            data-active={i === active}
            disabled={item.disabled}
            onMouseEnter={() => {
              if (i !== active) {
                setActive(i);
                audio.playSfx("sfx_menu_move", 0.25);
              }
            }}
            onClick={() => {
              if (!item.disabled) item.onClick();
            }}
            title={item.hint}
          >
            {item.label}
          </button>
        ))}
      </div>
    </div>
  );
}
