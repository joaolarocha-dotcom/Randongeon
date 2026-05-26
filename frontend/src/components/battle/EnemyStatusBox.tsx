import type { InimigoInfo } from "../../api/client";
import { PokeHPBar } from "./PokeHPBar";

interface Props {
  inimigo: InimigoInfo;
  /** HP exibido (anima rumo a inimigo.hp). */
  displayedHP: number;
}

function levelFromDifficulty(dificuldade: number): number {
  // Mapeia dificuldade do backend para LVL Pokemon-style
  if (dificuldade === 3) return 30;
  if (dificuldade === 2) return 15;
  return 5;
}

export function EnemyStatusBox({ inimigo, displayedHP }: Props) {
  const lvl = levelFromDifficulty(inimigo.dificuldade);
  return (
    <div className="poke-status">
      <div className="poke-status-name">
        <span>{inimigo.nome.toUpperCase()}</span>
        <span className="poke-status-lvl">:L{lvl}</span>
      </div>
      <PokeHPBar current={displayedHP} max={inimigo.hp_max} showText={false} />
    </div>
  );
}
