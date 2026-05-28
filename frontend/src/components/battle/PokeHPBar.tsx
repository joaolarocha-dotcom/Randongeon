interface Props {
  current: number;
  max: number;
  /** Mostra label HP e contador a direita */
  showText?: boolean;
}

/**
 * Barra de HP estilo Pokemon Gen 1: label "HP:" amarelo + barra fininha verde→amarelo→vermelho.
 * Cor calculada a partir do pct (não-animada via CSS por classe — animada via prop em useAnimatedHP).
 */
export function PokeHPBar({ current, max, showText = true }: Props) {
  const safeMax = Math.max(1, max);
  const safeCurrent = Math.max(0, Math.min(current, safeMax));
  const pct = (safeCurrent / safeMax) * 100;

  let colorClass = "";
  if (pct <= 20) colorClass = "is-red";
  else if (pct <= 50) colorClass = "is-yellow";

  return (
    <div>
      <div className="poke-hp-row">
        <span className="poke-hp-label">HP:</span>
        <div className="poke-hp-bar">
          <div className={`poke-hp-fill ${colorClass}`} style={{ width: `${pct}%` }} />
        </div>
      </div>
      {showText && (
        <div className="poke-hp-text">
          {safeCurrent}/{safeMax}
        </div>
      )}
    </div>
  );
}
