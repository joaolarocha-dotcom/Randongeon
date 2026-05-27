// frontend/src/screens/CombatScreen.tsx  — v3.1

import { useGameStore } from "../store/gameStore";
import type { CombatLog } from "../store/gameStore";
import { HPBar } from "../components/HPBar";
import { DialogBox } from "../components/DialogBox";

// ── Config visual por tipo especial ──────────────────────────────────────────

const ESPECIAL: Record<string, { emoji: string; label: string; cor: string }> = {
  vampiro: { emoji: "🧛", label: "Regen 20%",    cor: "#c0392b" },
  golem:   { emoji: "🗿", label: "Armadura +2",   cor: "#7f8c8d" },
  cacador: { emoji: "🏹", label: "+1 ATK/turno",  cor: "#d35400" },
  horda:   { emoji: "👺", label: "Horda",          cor: "#27ae60" },
  banshee: { emoji: "👻", label: "Atordoa 30%",   cor: "#8e44ad" },
};

function BadgeEspecial({ tipo }: { tipo: string }) {
  const cfg = ESPECIAL[tipo];
  if (!cfg) return null;
  return (
    <span style={{
      fontSize:   "var(--font-size-sm)",
      padding:    "1px 5px",
      border:     `2px solid ${cfg.cor}`,
      color:      cfg.cor,
      marginLeft: 6,
    }}>
      {cfg.emoji} {cfg.label}
    </span>
  );
}

// ── Linha de log ──────────────────────────────────────────────────────────────

function LogLine({ entry }: { entry: CombatLog }) {
  const cores: Record<CombatLog["tipo"], string> = {
    vitoria: "var(--hp-green)",
    derrota: "var(--hp-red)",
    fuga:    "var(--hp-yellow)",
    loot:    "var(--gold)",
    miss:    "var(--text-dim)",
    info:    "var(--text-dim)",
    dano:    "var(--text-color)",
  };
  return (
    <p style={{ color: cores[entry.tipo], marginBottom: 3, lineHeight: 1.6 }}>
      {entry.mensagem}
    </p>
  );
}

// ── Componente principal ──────────────────────────────────────────────────────

export function CombatScreen() {
  const {
    jogador, inimigo, combatLog,
    combatAttack, combatDodge, combatFlee,
    loading, jogadorAtordoado, ultimoLoot,
  } = useGameStore();

  if (!jogador || !inimigo) return null;

  const lastLog      = combatLog[combatLog.length - 1];
  const isCombatOver = !!lastLog && ["vitoria", "derrota", "fuga"].includes(lastLog.tipo);
  const tipo         = inimigo.tipo_especial ?? null;
  const cfgEspecial  = tipo ? ESPECIAL[tipo] : null;

  const spriteEmoji =
    tipo === "vampiro" ? "🧛" :
    tipo === "golem"   ? "🗿" :
    tipo === "cacador" ? "🏹" :
    tipo === "horda"   ? "👺" :
    tipo === "banshee" ? "👻" :
    inimigo.dificuldade === 3 ? "💀" :
    inimigo.dificuldade === 2 ? "☠️" : "👾";

  const spriteBg = cfgEspecial
    ? cfgEspecial.cor + "33"
    : inimigo.dificuldade === 3 ? "#c0392b33"
    : inimigo.dificuldade === 2 ? "#e67e2233" : "#2ecc7133";

  return (
    <div style={{ width:"100%", height:"100%", display:"flex",
                  flexDirection:"column", padding:12, gap:8 }}>

      {/* ── Área do inimigo ─────────────────────────────────────────────────── */}
      <div style={{ display:"flex", flexDirection:"column", alignItems:"center", gap:4 }}>

        {/* Nome + badge */}
        <div style={{ display:"flex", alignItems:"center", flexWrap:"wrap",
                      justifyContent:"center", gap:4 }}>
          <span style={{ fontSize:"var(--font-size-sm)",
                         color: inimigo.dificuldade === 3 ? "var(--hp-red)"
                               : inimigo.dificuldade === 2 ? "var(--hp-yellow)"
                               : "var(--hp-green)" }}>
            {inimigo.nome}
          </span>
          {tipo && <BadgeEspecial tipo={tipo} />}
        </div>

        {/* HP bar */}
        <HPBar current={inimigo.hp} max={inimigo.hp_max} />

        {/* Sprite */}
        <div style={{
          width:64, height:64, backgroundColor:spriteBg,
          border:`2px solid ${cfgEspecial?.cor ?? "var(--border-color)"}`,
          display:"flex", alignItems:"center", justifyContent:"center",
          fontSize:"28px",
        }}>
          {spriteEmoji}
        </div>
      </div>

      {/* ── HP do jogador ───────────────────────────────────────────────────── */}
      <div className="pixel-box" style={{ padding:8 }}>
        <HPBar current={jogador.hp} max={jogador.hp_max} label={jogador.nome} />
        <div style={{ display:"flex", gap:12, fontSize:"var(--font-size-sm)",
                      marginTop:4, color:"var(--text-dim)" }}>
          <span>ATK {jogador.atk}</span>
          <span>ESQ {Math.round(jogador.esq * 100)}%</span>
          <span style={{ color:"var(--gold)" }}>$ {jogador.moedas}</span>
        </div>
      </div>

      {/* ── Aviso de atordoamento ───────────────────────────────────────────── */}
      {jogadorAtordoado && !isCombatOver && (
        <div style={{
          textAlign:"center", fontSize:"var(--font-size-sm)",
          color:"#8e44ad", border:"2px solid #8e44ad", padding:"3px 8px",
          animation:"flash 0.8s steps(1) infinite",
        }}>
          💀 ATORDOADO — próximo ataque bloqueado
        </div>
      )}

      {/* ── Banner de loot ──────────────────────────────────────────────────── */}
      {ultimoLoot && isCombatOver && (
        <div style={{
          textAlign:"center", fontSize:"var(--font-size-sm)",
          color:"var(--gold)", border:"2px solid var(--gold)",
          padding:"3px 8px",
        }}>
          ✨ Drop: {ultimoLoot.nome}
          {ultimoLoot.bonus_hp  > 0 && ` · HP +${ultimoLoot.bonus_hp}`}
          {ultimoLoot.bonus_atk > 0 && ` · ATK +${ultimoLoot.bonus_atk}`}
          {ultimoLoot.bonus_esq > 0 && ` · ESQ +${Math.round(ultimoLoot.bonus_esq*100)}%`}
        </div>
      )}

      {/* ── Log de combate ──────────────────────────────────────────────────── */}
      <div style={{ flex:1, overflow:"auto", fontSize:"var(--font-size-sm)", padding:"2px 0" }}>
        {combatLog.map((entry, i) => (
          <LogLine key={i} entry={entry} />
        ))}
      </div>

      {/* ── Ações ───────────────────────────────────────────────────────────── */}
      {!isCombatOver && (
        <DialogBox style={{ position:"relative", bottom:0, left:0, right:0 }}>
          <div style={{ display:"flex", gap:8, justifyContent:"center", flexWrap:"wrap" }}>
            <button
              className="pixel-btn"
              onClick={combatAttack}
              disabled={loading}
              style={{ opacity: jogadorAtordoado ? 0.55 : 1 }}
              title={jogadorAtordoado ? "Atordoado — perderá este turno" : "Atacar"}
            >
              {jogadorAtordoado ? "💀 ATACAR" : "ATACAR"}
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

      {/* ── Resultado final ─────────────────────────────────────────────────── */}
      {isCombatOver && (
        <div style={{ textAlign:"center", fontSize:"var(--font-size-sm)",
                      color: lastLog.tipo === "vitoria" ? "var(--hp-green)"
                           : lastLog.tipo === "derrota" ? "var(--hp-red)"
                           : "var(--hp-yellow)" }}>
          {lastLog.mensagem}
        </div>
      )}
    </div>
  );
}