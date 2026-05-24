import { useEffect, useState } from "react";
import { useGameStore } from "../store/gameStore";
import { PokeHPBar } from "../components/battle/PokeHPBar";
import { PLAYER_SPRITE, COIN_ICON, FALLBACK_SPRITE_PATH } from "../assets/spriteMap";
import { getArenaBg } from "../assets/bgMap";
import { audio } from "../components/audio/AudioEngine";

export function MenuScreen() {
  const { jogador, advance, quit, loading, descricaoSala } = useGameStore();
  const [playerSrc, setPlayerSrc] = useState(PLAYER_SPRITE.src);
  const [coinSrc, setCoinSrc] = useState(COIN_ICON.src);

  useEffect(() => {
    audio.playMusic("bgm_dungeon");
  }, []);

  if (!jogador) return null;

  const bg = getArenaBg(jogador.andar);
  const lvl = Math.max(1, Math.floor(jogador.xp / 50) + 1);

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
      {/* Cenário superior com sprite do herói */}
      <div
        className="poke-arena"
        style={{
          backgroundImage: `url(${bg})`,
          flex: "0 0 55%",
          position: "relative",
        }}
      >
        <img
          src={playerSrc}
          alt="Herói"
          onError={() => {
            if (playerSrc !== FALLBACK_SPRITE_PATH) setPlayerSrc(FALLBACK_SPRITE_PATH);
          }}
          style={{
            position: "absolute",
            left: "50%",
            bottom: "8%",
            transform: "translateX(-50%)",
            width: PLAYER_SPRITE.w * 3,
            height: PLAYER_SPRITE.h * 3,
            imageRendering: "pixelated",
          }}
          draggable={false}
        />
        <div
          className="platform-shadow"
          style={{
            position: "absolute",
            left: "50%",
            bottom: "5%",
            transform: "translateX(-50%)",
            width: PLAYER_SPRITE.w * 3.5,
            height: 16,
          }}
        />

        {/* Indicador de andar no canto superior direito */}
        <div className="poke-status" style={{ position: "absolute", top: 8, right: 8 }}>
          <span>ANDAR {jogador.andar}</span>
        </div>
      </div>

      {/* Painel inferior */}
      <div style={{ flex: "1 1 45%", padding: 8, display: "flex", flexDirection: "column", gap: 6 }}>
        {/* Status do jogador */}
        <div className="poke-box" style={{ padding: "6px 10px" }}>
          <div className="poke-status-name" style={{ marginBottom: 4 }}>
            <span>{jogador.nome.toUpperCase()}</span>
            <span className="poke-status-lvl">:L{lvl}</span>
          </div>
          <PokeHPBar current={jogador.hp} max={jogador.hp_max} showText />
          <div
            style={{
              display: "flex",
              gap: 12,
              fontSize: 7,
              color: "#000",
              marginTop: 4,
              alignItems: "center",
              flexWrap: "wrap",
            }}
          >
            <span>ATK:{jogador.atk}</span>
            <span>ESQ:{Math.round(jogador.esq * 100)}%</span>
            <span>XP:{jogador.xp}</span>
            <span style={{ display: "inline-flex", alignItems: "center", gap: 3 }}>
              <img
                src={coinSrc}
                alt="$"
                onError={() => {
                  if (coinSrc !== FALLBACK_SPRITE_PATH) setCoinSrc(FALLBACK_SPRITE_PATH);
                }}
                width={10}
                height={10}
                style={{ imageRendering: "pixelated" }}
              />
              {jogador.moedas}
            </span>
          </div>
        </div>

        {/* Descrição da sala */}
        {descricaoSala && (
          <div
            className="poke-dialog"
            style={{ fontSize: 7, padding: "6px 8px", minHeight: 30 }}
          >
            {descricaoSala}
          </div>
        )}

        {/* Botões */}
        <div style={{ display: "flex", justifyContent: "center", gap: 12, marginTop: "auto" }}>
          <button
            className="poke-btn"
            onClick={() => {
              audio.playSfx("sfx_menu_select");
              advance();
            }}
            disabled={loading}
            style={{ minWidth: 110 }}
          >
            AVANÇAR
          </button>
          <button
            className="poke-btn"
            onClick={() => {
              audio.playSfx("sfx_menu_cancel");
              quit();
            }}
            disabled={loading}
            style={{ minWidth: 110 }}
          >
            DESISTIR
          </button>
        </div>
      </div>
    </div>
  );
}
