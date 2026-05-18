interface Props {
  current: number;
  max: number;
  label?: string;
}

export function HPBar({ current, max, label }: Props) {
  const pct = Math.max(0, Math.min(100, (current / max) * 100));
  const colorClass = pct > 50 ? "hp-green" : pct > 25 ? "hp-yellow" : "hp-red";

  return (
    <div style={{ width: "100%" }}>
      {label && (
        <div style={{ fontSize: "var(--font-size-sm)", marginBottom: 4 }}>
          {label}: {current}/{max}
        </div>
      )}
      <div className="hp-bar-container">
        <div className={`hp-bar-fill ${colorClass}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
