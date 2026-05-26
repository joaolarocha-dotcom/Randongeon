import { useEffect, useState } from "react";
import { useGameStore } from "../store/gameStore";
import { audio } from "../components/audio/AudioEngine";
import { useFullscreen } from "../hooks/useFullscreen";

const SETTINGS_KEY = "randongeon_settings";

interface Settings {
  musicVolume: number;
  sfxVolume: number;
  muted: boolean;
}

const DEFAULTS: Settings = { musicVolume: 0.35, sfxVolume: 0.5, muted: false };

function loadSettings(): Settings {
  try {
    const raw = localStorage.getItem(SETTINGS_KEY);
    if (!raw) return DEFAULTS;
    return { ...DEFAULTS, ...JSON.parse(raw) };
  } catch {
    return DEFAULTS;
  }
}

function saveSettings(s: Settings) {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(s));
}

export function SettingsScreen() {
  const goToMainMenu = useGameStore((s) => s.goToMainMenu);
  const { isFullscreen, toggle } = useFullscreen();
  const [settings, setSettings] = useState<Settings>(loadSettings);

  // Aplica config no audio engine sempre que muda
  useEffect(() => {
    audio.setMusicVolume(settings.musicVolume);
    audio.setSfxVolume(settings.sfxVolume);
    audio.setMuted(settings.muted);
    saveSettings(settings);
  }, [settings]);

  const update = (patch: Partial<Settings>) => setSettings({ ...settings, ...patch });

  const back = () => {
    audio.playSfx("sfx_menu_cancel");
    goToMainMenu();
  };

  const onResetSaves = () => {
    if (!confirm("Apagar TODOS os saves? Esta ação não pode ser desfeita.")) return;
    for (let i = 1; i <= 9; i++) {
      localStorage.removeItem(`randongeon_save_slot_${i}`);
    }
    alert("Saves apagados.");
  };

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        padding: 12,
        gap: 10,
        background: "var(--poke-bg)",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2 style={{ fontSize: "var(--font-size-md)", color: "#000" }}>CONFIGURAÇÕES</h2>
        <button className="poke-btn" onClick={back} style={{ padding: "4px 10px" }}>
          VOLTAR
        </button>
      </div>

      <div className="poke-box" style={{ padding: "10px 12px" }}>
        <Row label="Tela cheia">
          <button className="poke-btn" onClick={toggle} style={{ padding: "4px 10px" }}>
            {isFullscreen ? "DESLIGAR" : "LIGAR"}
          </button>
          <span style={{ fontSize: "var(--font-size-xs)", marginLeft: 8, color: "#555" }}>
            (F11)
          </span>
        </Row>

        <Row label={`Volume música: ${Math.round(settings.musicVolume * 100)}%`}>
          <input
            type="range"
            min={0}
            max={1}
            step={0.05}
            value={settings.musicVolume}
            onChange={(e) => update({ musicVolume: Number(e.target.value) })}
            style={{ flex: 1 }}
          />
        </Row>

        <Row label={`Volume efeitos: ${Math.round(settings.sfxVolume * 100)}%`}>
          <input
            type="range"
            min={0}
            max={1}
            step={0.05}
            value={settings.sfxVolume}
            onChange={(e) => update({ sfxVolume: Number(e.target.value) })}
            style={{ flex: 1 }}
          />
        </Row>

        <Row label="Mudo">
          <button
            className="poke-btn"
            onClick={() => update({ muted: !settings.muted })}
            style={{ padding: "4px 10px" }}
          >
            {settings.muted ? "DESLIGAR" : "LIGAR"}
          </button>
        </Row>
      </div>

      <div className="poke-box" style={{ padding: "10px 12px" }}>
        <button className="poke-btn" onClick={onResetSaves}>
          APAGAR TODOS OS SAVES
        </button>
      </div>
    </div>
  );
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        gap: 12,
        margin: "8px 0",
        fontSize: "var(--font-size-sm)",
        color: "#000",
      }}
    >
      <span>{label}</span>
      <div style={{ display: "flex", alignItems: "center", gap: 6, minWidth: "55%" }}>
        {children}
      </div>
    </div>
  );
}
