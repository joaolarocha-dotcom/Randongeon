import { useEffect, useState } from "react";
import { useGameStore } from "../store/gameStore";
import { PokeHPBar } from "../components/battle/PokeHPBar";
import { PLAYER_SPRITE, COIN_ICON, FALLBACK_SPRITE_PATH } from "../assets/spriteMap";
import { getArenaBg } from "../assets/bgMap";
import { audio } from "../components/audio/AudioEngine";
import { api } from "../api/client";
import { SAVE_SLOTS, type SaveSlot, putSave, exportSaveToFile } from "../services/saveService";

type ExitMode = null | "menu" | "exit-save" | "exit-confirm";

export function MenuScreen() {
  const { jogador, advance, quit, loading, descricaoSala, sessionId, exitToMainMenu } =
    useGameStore();
  const [playerSrc, setPlayerSrc] = useState(PLAYER_SPRITE.src);
  const [coinSrc, setCoinSrc] = useState(COIN_ICON.src);
  const [savePickerOpen, setSavePickerOpen] = useState(false);
  const [saveMsg, setSaveMsg] = useState<string | null>(null);
  const [exitMode, setExitMode] = useState<ExitMode>(null);

  useEffect(() => {
    audio.playMusic("bgm_dungeon");
  }, []);

  const doSave = async (slot: SaveSlot) => {
    if (!sessionId) return;
    try {
      const state = await api.saveGame(sessionId);
      putSave(slot, state);
      setSaveMsg(`Jogo salvo em ${slot.toUpperCase()}.`);
      audio.playSfx("sfx_item_get");
    } catch (e) {
      setSaveMsg(`Falha ao salvar: ${(e as Error).message}`);
    } finally {
      setSavePickerOpen(false);
    }
  };

  const doExportFile = async () => {
    if (!sessionId) return;
    try {
      const state = await api.saveGame(sessionId);
      exportSaveToFile(state);
      setSaveMsg("Run exportada para um arquivo .txt (confira seus downloads).");
      audio.playSfx("sfx_item_get");
    } catch (e) {
      setSaveMsg(`Falha ao exportar: ${(e as Error).message}`);
    } finally {
      setSavePickerOpen(false);
    }
  };

  const doSaveAndExit = async (slot: SaveSlot) => {
    if (!sessionId) {
      await exitToMainMenu();
      return;
    }
    try {
      const state = await api.saveGame(sessionId);
      putSave(slot, state);
      audio.playSfx("sfx_item_get");
      await exitToMainMenu();
    } catch (e) {
      setSaveMsg(`Falha ao salvar: ${(e as Error).message}`);
      setExitMode(null);
    }
  };

  const doExitWithoutSave = async () => {
    audio.playSfx("sfx_menu_cancel");
    await exitToMainMenu();
  };

  if (!jogador) return null;

  const bg = getArenaBg(jogador.andar);
  const lvl = Math.max(1, Math.floor(jogador.xp / 50) + 1);

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        background: "var(--poke-bg)",
      }}
    >
      {/* Cenário superior com sprite do herói */}
      <div
        className="poke-arena"
        style={{
          backgroundImage: `url(${bg})`,
          backgroundSize: "115%",
          backgroundPosition: "center 60%",
          flex: "0 0 55%",
          position: "relative",
        }}
      >
        <img
          src={playerSrc}
          alt="Herói"
          onError={() => {
            if (playerSrc !== FALLBACK_SPRITE_PATH) setPlayerSrc(FALLBACK_SPRITE_PATH);
          }}
          style={{
            position: "absolute",
            left: "22%",
            bottom: "16%",
            transform: "translateX(-50%)",
            width: PLAYER_SPRITE.w * 3,
            height: PLAYER_SPRITE.h * 3,
            imageRendering: "pixelated",
          }}
          draggable={false}
        />
        <div
          className="platform-shadow"
          style={{
            position: "absolute",
            left: "22%",
            bottom: "12%",
            transform: "translateX(-50%)",
            width: PLAYER_SPRITE.w * 3.5,
            height: 16,
          }}
        />

        {/* Indicador de andar no canto superior direito */}
        <div className="poke-status" style={{ position: "absolute", top: 8, right: 8 }}>
          <span>ANDAR {jogador.andar}</span>
        </div>
      </div>

      {/* Painel inferior */}
      <div style={{ flex: "1 1 45%", padding: 8, display: "flex", flexDirection: "column", gap: 6 }}>
        {/* Status do jogador */}
        <div className="poke-box" style={{ padding: "6px 10px" }}>
          <div className="poke-status-name" style={{ marginBottom: 4 }}>
            <span>{jogador.nome.toUpperCase()}</span>
            <span className="poke-status-lvl">:L{lvl}</span>
          </div>
          <PokeHPBar current={jogador.hp} max={jogador.hp_max} showText />
          <div
            style={{
              display: "flex",
              gap: 12,
              fontSize: 7,
              color: "#000",
              marginTop: 4,
              alignItems: "center",
              flexWrap: "wrap",
            }}
          >
            <span>ATK:{jogador.atk}</span>
            <span>ESQ:{Math.round(jogador.esq * 100)}%</span>
            <span>XP:{jogador.xp}</span>
            <span style={{ display: "inline-flex", alignItems: "center", gap: 3 }}>
              <img
                src={coinSrc}
                alt="$"
                onError={() => {
                  if (coinSrc !== FALLBACK_SPRITE_PATH) setCoinSrc(FALLBACK_SPRITE_PATH);
                }}
                width={10}
                height={10}
                style={{ imageRendering: "pixelated" }}
              />
              {jogador.moedas}
            </span>
          </div>
        </div>

        {/* Descrição da sala */}
        {descricaoSala && (
          <div
            className="poke-dialog"
            style={{ fontSize: 7, padding: "6px 8px", minHeight: 30 }}
          >
            {descricaoSala}
          </div>
        )}

        {saveMsg && (
          <div
            className="poke-dialog"
            style={{ fontSize: "var(--font-size-xs)", padding: "4px 8px" }}
            onClick={() => setSaveMsg(null)}
          >
            {saveMsg}
          </div>
        )}

        {/* Botões */}
        <div style={{ display: "flex", justifyContent: "center", gap: 6, marginTop: "auto", flexWrap: "wrap" }}>
          <button
            className="poke-btn"
            onClick={() => {
              audio.playSfx("sfx_menu_select");
              advance();
            }}
            disabled={loading}
            style={{ minWidth: 80 }}
          >
            AVANÇAR
          </button>
          <button
            className="poke-btn"
            onClick={() => {
              audio.playSfx("sfx_menu_select");
              setSavePickerOpen(!savePickerOpen);
              setSaveMsg(null);
            }}
            disabled={loading}
            style={{ minWidth: 80 }}
          >
            SALVAR
          </button>
          <button
            className="poke-btn"
            onClick={() => {
              audio.playSfx("sfx_menu_select");
              setExitMode("menu");
            }}
            disabled={loading}
            style={{ minWidth: 80 }}
          >
            MENU
          </button>
          <button
            className="poke-btn"
            onClick={() => {
              audio.playSfx("sfx_menu_cancel");
              quit();
            }}
            disabled={loading}
            style={{ minWidth: 80 }}
          >
            DESISTIR
          </button>
        </div>

        {savePickerOpen && (
          <div style={{ display: "flex", justifyContent: "center", gap: 6, marginTop: 6 }}>
            {SAVE_SLOTS.map((slot) => (
              <button
                key={slot}
                className="poke-btn"
                onClick={() => doSave(slot)}
                disabled={loading}
                style={{ padding: "4px 8px", fontSize: "var(--font-size-xs)" }}
              >
                {slot.toUpperCase()}
              </button>
            ))}
            <button
              className="poke-btn"
              onClick={doExportFile}
              disabled={loading}
              style={{ padding: "4px 8px", fontSize: "var(--font-size-xs)" }}
              title="Baixar a run atual como arquivo .txt"
            >
              ⬇ .TXT
            </button>
            <button
              className="poke-btn"
              onClick={() => setSavePickerOpen(false)}
              style={{ padding: "4px 8px", fontSize: "var(--font-size-xs)" }}
            >
              ✕
            </button>
          </div>
        )}
      </div>

      {exitMode !== null && (
        <ExitOverlay
          mode={exitMode}
          onChangeMode={setExitMode}
          onSaveAndExit={doSaveAndExit}
          onExit={doExitWithoutSave}
          loading={loading}
        />
      )}
    </div>
  );
}

interface ExitOverlayProps {
  mode: Exclude<ExitMode, null>;
  onChangeMode: (m: ExitMode) => void;
  onSaveAndExit: (slot: SaveSlot) => void;
  onExit: () => void;
  loading: boolean;
}

function ExitOverlay({ mode, onChangeMode, onSaveAndExit, onExit, loading }: ExitOverlayProps) {
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        background: "rgba(0,0,0,0.55)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 10,
      }}
      onClick={() => onChangeMode(null)}
    >
      <div
        className="poke-box"
        style={{ padding: 14, minWidth: 220, display: "flex", flexDirection: "column", gap: 8 }}
        onClick={(e) => e.stopPropagation()}
      >
        {mode === "menu" && (
          <>
            <div style={{ fontSize: "var(--font-size-sm)", textAlign: "center", marginBottom: 6 }}>
              MENU
            </div>
            <button className="poke-btn" onClick={() => onChangeMode(null)}>
              CONTINUAR
            </button>
            <button className="poke-btn" onClick={() => onChangeMode("exit-save")} disabled={loading}>
              SALVAR E SAIR
            </button>
            <button className="poke-btn" onClick={() => onChangeMode("exit-confirm")} disabled={loading}>
              SAIR SEM SALVAR
            </button>
          </>
        )}

        {mode === "exit-save" && (
          <>
            <div style={{ fontSize: "var(--font-size-sm)", textAlign: "center", marginBottom: 6 }}>
              SALVAR EM QUAL SLOT?
            </div>
            {SAVE_SLOTS.map((slot) => (
              <button
                key={slot}
                className="poke-btn"
                onClick={() => onSaveAndExit(slot)}
                disabled={loading}
              >
                {slot.toUpperCase()}
              </button>
            ))}
            <button className="poke-btn" onClick={() => onChangeMode("menu")}>
              ◀ VOLTAR
            </button>
          </>
        )}

        {mode === "exit-confirm" && (
          <>
            <div style={{ fontSize: "var(--font-size-sm)", textAlign: "center", marginBottom: 6 }}>
              SAIR SEM SALVAR?
              <br />
              <span style={{ fontSize: "var(--font-size-xs)", color: "#666" }}>
                Todo o progresso desta run será perdido.
              </span>
            </div>
            <button className="poke-btn" onClick={onExit} disabled={loading}>
              SIM, SAIR
            </button>
            <button className="poke-btn" onClick={() => onChangeMode("menu")}>
              ◀ VOLTAR
            </button>
          </>
        )}
      </div>
    </div>
  );
}
