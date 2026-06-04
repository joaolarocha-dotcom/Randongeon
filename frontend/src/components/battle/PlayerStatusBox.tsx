import type { JogadorStatus } from "../../api/client";
import { PokeHPBar } from "./PokeHPBar";
import { StatusBadges } from "./StatusBadges";

interface Props {
  jogador: JogadorStatus;
  displayedHP: number;
}

function expPctForCurrentLevel(jogador: JogadorStatus): number {
  // Usa a curva REAL (xp_nivel_atual/total vindos da API). Fallback defensivo
  // para respostas antigas sem os campos.
  const atual = jogador.xp_nivel_atual ?? jogador.xp % 50;
  const total = jogador.xp_nivel_total ?? 50;
  if (total <= 0) return 0;
  return Math.min(100, (atual / total) * 100);
}

export function PlayerStatusBox({ jogador, displayedHP }: Props) {
  // Nível REAL do backend (curva triangular), não mais a estimativa xp/50.
  const lvl = jogador.nivel ?? 1;
  const expPct = expPctForCurrentLevel(jogador);

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
