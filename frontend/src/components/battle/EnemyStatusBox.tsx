import type { InimigoInfo } from "../../api/client";
import { PokeHPBar } from "./PokeHPBar";

interface Props {
  inimigo: InimigoInfo;
  /** HP exibido (anima rumo a inimigo.hp). */
  displayedHP: number;
  /** Lote 4b: boss em 2ª fase/fúria (Coração da Masmorra renasceu). */
  enraged?: boolean;
}

function levelFromDifficulty(dificuldade: number): number {
  // Mapeia dificuldade do backend para LVL Pokemon-style
  if (dificuldade === 3) return 30;
  if (dificuldade === 2) return 15;
  return 5;
}

export function EnemyStatusBox({ inimigo, displayedHP, enraged = false }: Props) {
  const lvl = levelFromDifficulty(inimigo.dificuldade);
  return (
    <div className="poke-status">
      <div className="poke-status-name">
        <span>{inimigo.nome.toUpperCase()}</span>
        <span className="poke-status-lvl">:L{lvl}</span>
        {enraged && (
          <span
            className="enemy-fury-badge"
            title="2ª fase: o boss renasceu em fúria"
            style={{
              marginLeft: 6,
              color: "#ff4d4d",
              fontWeight: "bold",
              textShadow: "0 0 4px rgba(255,0,0,0.7)",
            }}
          >
            🔥 FÚRIA
          </span>
        )}
      </div>
      <PokeHPBar current={displayedHP} max={inimigo.hp_max} showText={false} />
    </div>
  );
}
