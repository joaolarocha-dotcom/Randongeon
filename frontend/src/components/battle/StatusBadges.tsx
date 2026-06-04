import type { JogadorStatus } from "../../api/client";

/**
 * Lote 5 — Badges de status do jogador na tela de combate.
 *
 * Mostra os efeitos temporários ativos (veneno/fraqueza/esquiva-reduzida, com os
 * turnos restantes) e o dom escolhido (passivo permanente — cobre lifesteal/Ágil
 * etc.). Os dados vêm do JogadorStatus (campos `efeitos` e `dom`), expostos pela
 * API no Lote 5.
 */

const EFEITO_INFO: Record<string, { icon: string; label: string; color: string }> = {
  veneno:           { icon: "☠️", label: "VENENO", color: "#7CFC00" },
  fraqueza:         { icon: "💪", label: "FRACO",  color: "#ffae42" },
  esquiva_reduzida: { icon: "💫", label: "ZONZO",  color: "#c084fc" },
};

const DOM_LABEL: Record<string, string> = {
  bruto:       "Bruto",
  resistente:  "Resistente",
  agil:        "Ágil",
  sortudo:     "Sortudo",
  sanguessuga: "Sanguessuga",
};

function Pill({ icon, label, color }: { icon: string; label: string; color: string }) {
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 2,
        fontSize: 9,
        lineHeight: 1,
        padding: "2px 4px",
        border: `1px solid ${color}`,
        borderRadius: 3,
        color,
        background: "rgba(0,0,0,0.45)",
        whiteSpace: "nowrap",
      }}
    >
      <span>{icon}</span>
      <span>{label}</span>
    </span>
  );
}

export function StatusBadges({ jogador }: { jogador: JogadorStatus }) {
  const efeitos = jogador.efeitos ?? [];
  const dom = jogador.dom ?? null;

  if (efeitos.length === 0 && !dom) return null;

  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: 3, marginTop: 4 }}>
      {efeitos.map((e, i) => {
        const info =
          EFEITO_INFO[e.tipo] ?? { icon: "✦", label: e.tipo.toUpperCase(), color: "#dddddd" };
        const label = e.turnos > 0 ? `${info.label} ${e.turnos}` : info.label;
        return <Pill key={`${e.tipo}-${i}`} icon={info.icon} label={label} color={info.color} />;
      })}
      {dom && <Pill icon="⭐" label={DOM_LABEL[dom] ?? dom} color="#ffd700" />}
    </div>
  );
}
