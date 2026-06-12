import type { InimigoInfo } from "../../api/client";
import { getEnemySprite, FALLBACK_SPRITE_PATH } from "../../assets/spriteMap";

interface Props {
  inimigo: InimigoInfo;
  /** Classe de animação ativa (shake, flash-white, faint-down, slide-in-right). */
  animClass?: string;
  /** Escala em x. Default: 3. */
  scale?: number;
}

/**
 * Sprite do inimigo com plataforma elíptica abaixo.
 * Usa onError para cair para o goblin caso o arquivo não exista.
 * O `key` no <img> garante remount quando o inimigo muda — assim o src acompanha.
 */
export function EnemySprite({ inimigo, animClass = "", scale = 3 }: Props) {
  const sprite = getEnemySprite(inimigo.nome, inimigo.dificuldade);
  const w = sprite.w * scale;
  const h = sprite.h * scale;

  return (
    <div
      style={{
        position: "absolute",
        right: "10%",
        top: "18%",
        width: w,
        height: h,
        display: "flex",
        alignItems: "flex-end",
        justifyContent: "center",
      }}
    >
      {/* Plataforma sob os pés */}
      <div
        className="platform-shadow"
        style={{
          width: w * 0.95,
          height: 14,
          bottom: -8,
          left: "2.5%",
          position: "absolute",
        }}
      />
      <img
        key={sprite.src}
        src={sprite.src}
        alt={inimigo.nome}
        className={animClass}
        onError={(e) => {
          const target = e.currentTarget;
          if (target.src.endsWith(FALLBACK_SPRITE_PATH)) return;
          target.src = FALLBACK_SPRITE_PATH;
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
