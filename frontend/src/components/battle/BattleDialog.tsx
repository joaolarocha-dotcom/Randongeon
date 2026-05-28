import { useEffect, useRef } from "react";
import { useGameStore } from "../../store/gameStore";
import { useTypewriter } from "../../hooks/useTypewriter";

interface Props {
  /** Se true, mostra cursor ▼ piscando ao terminar de digitar e clique avança o diálogo. */
  interactive?: boolean;
  /** Avanço automático após X ms ao terminar de digitar (default: não). */
  autoAdvanceMs?: number;
  /** Callback chamado quando a fila esvazia (nem dialogQueue, nem currentDialog). */
  onQueueEmpty?: () => void;
}

/**
 * Caixa de diálogo Pokemon-style. Lê currentDialog/dialogQueue do gameStore
 * e digita caractere a caractere. Avança ao clicar (modo interactive)
 * ou após autoAdvanceMs.
 *
 * `onQueueEmpty` é chamado apenas na TRANSIÇÃO de "tinha texto" para "vazio"
 * (não em renders subsequentes em que a fila já estava vazia).
 */
export function BattleDialog({ interactive = true, autoAdvanceMs, onQueueEmpty }: Props) {
  const currentDialog = useGameStore((s) => s.currentDialog);
  const dialogQueue = useGameStore((s) => s.dialogQueue);
  const nextDialog = useGameStore((s) => s.nextDialog);

  const text = currentDialog ?? "";
  const { displayed, done, skip } = useTypewriter(text, { speed: 28, playBlip: true });

  // Rastreia o último estado não-vazio para só notificar na transição "tinha → vazio"
  const hadContentRef = useRef<boolean>(false);

  useEffect(() => {
    const hasContent = !!currentDialog || dialogQueue.length > 0;
    if (hasContent) {
      hadContentRef.current = true;
    } else if (hadContentRef.current) {
      // Transição de "tinha conteúdo" para "vazio"
      hadContentRef.current = false;
      onQueueEmpty?.();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentDialog, dialogQueue.length]);

  // Avanço automático
  useEffect(() => {
    if (!done || !autoAdvanceMs) return;
    const id = setTimeout(() => {
      nextDialog();
    }, autoAdvanceMs);
    return () => clearTimeout(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [done, autoAdvanceMs, dialogQueue.length]);

  const handleClick = () => {
    if (!interactive) return;
    if (!done) {
      skip();
      return;
    }
    // Avança para próximo (ou seta currentDialog=null se fila vazia).
    // O useEffect acima vai detectar a transição e chamar onQueueEmpty UMA vez.
    nextDialog();
  };

  if (!currentDialog) {
    return null;
  }

  return (
    <div
      className="poke-dialog"
      onClick={handleClick}
      style={{
        cursor: interactive ? "pointer" : "default",
        userSelect: "none",
      }}
    >
      <span>{displayed}</span>
      {done && interactive && <span className="poke-dialog-cursor">▼</span>}
      {!done && <span className="blink">▌</span>}
    </div>
  );
}
