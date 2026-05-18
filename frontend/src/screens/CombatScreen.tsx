import { useGameStore } from "../store/gameStore";
import { HPBar } from "../components/HPBar";
import { DialogBox } from "../components/DialogBox";

export function CombatScreen() {
  const { jogador, inimigo, combatLog, combatAttack, combatDodge, combatFlee, loading } =
    useGameStore();

  if (!jogador || !inimigo) return null;

  const lastLog = combatLog[combatLog.length - 1];
  const isCombatOver = lastLog && ["vitoria", "derrota", "fuga"].includes(lastLog.tipo);

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        padding: 12,
        gap: 8,
      }}
    >
      {/* Enemy area */}
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
        <span style={{ fontSize: "var(--font-size-sm)", color: getDifficultyColor(inimigo.dificuldade) }}>
          {inimigo.nome}
        </span>
        <HPBar current={inimigo.hp} max={inimigo.hp_max} />
        {/* Placeholder sprite area */}
        <div
          className={lastLog?.tipo === "dano" && lastLog.mensagem.includes("causou") ? "shake" : ""}
          style={{
            width: 64,
            height: 64,
            backgroundColor: getDifficultyColor(inimigo.dificuldade),
            opacity: 0.7,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "24px",
          }}
        >
          {inimigo.dificuldade === 3 ? "👹" : inimigo.dificuldade === 2 ? "💀" : "👾"}
        </div>
      </div>

      {/* Player HP */}
      <div className="pixel-box" style={{ padding: 8 }}>
        <HPBar current={jogador.hp} max={jogador.hp_max} label={jogador.nome} />
      </div>

      {/* Combat log */}
      <div
        style={{
          flex: 1,
          overflow: "auto",
          fontSize: "var(--font-size-sm)",
          padding: "4px 0",
        }}
      >
        {combatLog.map((log, i) => (
          <p
            key={i}
            style={{
              color: getLogColor(log.tipo),
              marginBottom: 4,
            }}
          >
            {log.mensagem}
          </p>
        ))}
      </div>

      {/* Actions */}
      {!isCombatOver && (
        <DialogBox style={{ position: "relative", bottom: 0, left: 0, right: 0 }}>
          <div style={{ display: "flex", gap: 8, justifyContent: "center", flexWrap: "wrap" }}>
            <button className="pixel-btn" onClick={combatAttack} disabled={loading}>
              ATACAR
            </button>
            <button className="pixel-btn" onClick={combatDodge} disabled={loading}>
              ESQUIVAR
            </button>
            <button className="pixel-btn" onClick={combatFlee} disabled={loading}>
              FUGIR
            </button>
          </div>
        </DialogBox>
      )}

      {isCombatOver && (
        <div style={{ textAlign: "center", fontSize: "var(--font-size-sm)", color: getLogColor(lastLog.tipo) }}>
          {lastLog.mensagem}
        </div>
      )}
    </div>
  );
}

function getDifficultyColor(d: number): string {
  if (d === 3) return "var(--hp-red)";
  if (d === 2) return "var(--hp-yellow)";
  return "var(--hp-green)";
}

function getLogColor(tipo: string): string {
  switch (tipo) {
    case "vitoria": return "var(--hp-green)";
    case "derrota": return "var(--hp-red)";
    case "fuga": return "var(--hp-yellow)";
    case "dano": return "var(--text-color)";
    default: return "var(--text-dim)";
  }
}
