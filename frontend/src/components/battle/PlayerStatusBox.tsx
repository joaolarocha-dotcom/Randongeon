import type { JogadorStatus } from "../../api/client";
import { PokeHPBar } from "./PokeHPBar";
import { StatusBadges } from "./StatusBadges";

interface Props {
  jogador: JogadorStatus;
  displayedHP: number;
}

function lvlFromXp(xp: number): number {
  return Math.max(1, Math.floor(xp / 50) + 1);
}

function expPctForCurrentLevel(xp: number): number {
  // 0–50, 50–100, etc. Mostra progresso dentro do nível atual.
  const inLevel = xp % 50;
  return (inLevel / 50) * 100;
}

export function PlayerStatusBox({ jogador, displayedHP }: Props) {
  const lvl = lvlFromXp(jogador.xp);
  const expPct = expPctForCurrentLevel(jogador.xp);

  return (
    <div className="poke-status">
      <div className="poke-status-name">
        <span>{jogador.nome.toUpperCase()}</span>
        <span className="poke-status-lvl">:L{lvl}</span>
      </div>
      <PokeHPBar current={displayedHP} max={jogador.hp_max} showText />
      <div className="poke-exp-bar">
        <div className="poke-exp-fill" style={{ width: `${expPct}%` }} />
      </div>
      <StatusBadges jogador={jogador} />
    </div>
  );
}
