import { useState } from "react";
import { PLAYER_SPRITE, FALLBACK_SPRITE_PATH } from "../../assets/spriteMap";

interface Props {
  animClass?: string;
  scale?: number;
}

/**
 * Sprite do protagonista (Zeppeli) de costas, posicionado na metade inferior-esquerda da arena.
 */
export function PlayerSprite({ animClass = "", scale = 3 }: Props) {
  const [src, setSrc] = useState(PLAYER_SPRITE.src);
  const w = PLAYER_SPRITE.w * scale;
  const h = PLAYER_SPRITE.h * scale;

  return (
    <div
      style={{
        position: "absolute",
        left: "14%",
        bottom: "10%",
        width: w,
        height: h,
        display: "flex",
        alignItems: "flex-end",
        justifyContent: "center",
      }}
    >
      <div
        className="platform-shadow"
        style={{
          width: w * 1.1,
          height: 16,
          bottom: -10,
          left: "-5%",
          position: "absolute",
        }}
      />
      <img
        src={src}
        alt="Protagonista"
        className={animClass}
        onError={() => {
          if (src !== FALLBACK_SPRITE_PATH) setSrc(FALLBACK_SPRITE_PATH);
        }}
        style={{
          width: w,
          height: h,
          imageRendering: "pixelated",
          display: "block",
        }}
        draggable={false}
      />
    </div>
  );
}
