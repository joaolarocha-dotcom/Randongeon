import { useState } from "react";
import { useGameStore } from "../store/gameStore";
import {
  CHEST_CLOSED,
  CHEST_OPEN,
  FALLBACK_SPRITE_PATH,
} from "../assets/spriteMap";
import { BG } from "../assets/bgMap";
import { audio } from "../components/audio/AudioEngine";

export function ChestScreen() {
  const { descricaoSala, item, openChest, ignoreChest, loading } = useGameStore();
  const [opened, setOpened] = useState(false);
  const [chestSrc, setChestSrc] = useState(CHEST_CLOSED.src);

  const handleOpen = () => {
    setOpened(true);
    setChestSrc(CHEST_OPEN.src);
    openChest();
  };

  const handleIgnore = () => {
    audio.playSfx("sfx_menu_cancel");
    ignoreChest();
  };

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        background: "var(--poke-bg)",
      }}
    >
      {/* Cenário superior */}
      <div
        className="poke-arena"
        style={{
          backgroundImage: `url(${BG.chestRoom})`,
          flex: "0 0 55%",
          position: "relative",
        }}
      >
        <img
          src={chestSrc}
          alt="Baú"
          onError={() => {
            if (chestSrc !== FALLBACK_SPRITE_PATH) setChestSrc(FALLBACK_SPRITE_PATH);
          }}
          style={{
            position: "absolute",
            left: "50%",
            bottom: "10%",
            transform: "translateX(-50%)",
            width: CHEST_CLOSED.w * 3,
            height: CHEST_CLOSED.h * 3,
            imageRendering: "pixelated",
          }}
          draggable={false}
        />
        <div
          className="platform-shadow"
          style={{
            position: "absolute",
            left: "50%",
            bottom: "8%",
            transform: "translateX(-50%)",
            width: CHEST_CLOSED.w * 3.3,
            height: 14,
          }}
        />
      </div>

      {/* Painel inferior */}
      <div
        style={{
          flex: "1 1 45%",
          padding: 10,
          display: "flex",
          flexDirection: "column",
          gap: 8,
        }}
      >
        <div className="poke-dialog" style={{ fontSize: 7, padding: "8px 10px" }}>
          {descricaoSala || "Um baú repousa diante de você. Abrir?"}
        </div>

        {opened && item && (
          <div className="poke-box" style={{ fontSize: 7, padding: "6px 8px" }}>
            <p style={{ color: "#d8a000", marginBottom: 4 }}>{item.nome}</p>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", color: "#000" }}>
              {item.bonus_atk > 0 && <span>ATK +{item.bonus_atk}</span>}
              {item.bonus_hp > 0 && <span>HP +{item.bonus_hp}</span>}
              {item.bonus_esq > 0 && <span>ESQ +{Math.round(item.bonus_esq * 100)}%</span>}
            </div>
          </div>
        )}

        <div style={{ display: "flex", justifyContent: "center", gap: 12, marginTop: "auto" }}>
          {!opened ? (
            <>
              <button
                className="poke-btn"
                onClick={handleOpen}
                disabled={loading}
                style={{ minWidth: 100 }}
              >
                ABRIR
              </button>
              <button
                className="poke-btn"
                onClick={handleIgnore}
                disabled={loading}
                style={{ minWidth: 100 }}
              >
                IGNORAR
              </button>
            </>
          ) : (
            <div style={{ fontSize: 7, color: "#000" }}>
              {loading ? "..." : ""}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
