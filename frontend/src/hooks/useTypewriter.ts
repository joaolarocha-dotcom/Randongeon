import { useEffect, useRef, useState } from "react";
import { audio } from "../components/audio/AudioEngine";

interface Options {
  /** Caracteres por segundo (default: ~33, ou seja, 30ms por caractere). */
  speed?: number;
  /** Toca sfx_dialog_blip a cada N caracteres (com throttle). */
  playBlip?: boolean;
  /** Callback ao terminar de digitar todo o texto. */
  onComplete?: () => void;
}

/**
 * Efeito de máquina de escrever. Retorna { displayed, done, skip }.
 *
 * - `displayed` é a substring atual do `text`.
 * - `done` vira true ao terminar (e o blip de cursor pode ser escondido).
 * - `skip()` força o texto inteiro a aparecer imediatamente.
 */
export function useTypewriter(text: string, options: Options = {}) {
  const { speed = 30, playBlip = true, onComplete } = options;
  const [displayed, setDisplayed] = useState("");
  const [done, setDone] = useState(false);
  const lastBlipRef = useRef<number>(0);
  const intervalRef = useRef<number | null>(null);
  const completedRef = useRef(false);

  useEffect(() => {
    // Reset síncrono dos estados ao mudar text/speed é intencional para reiniciar a digitação.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setDisplayed("");
    setDone(false);
    completedRef.current = false;

    if (!text) {
      setDone(true);
      onComplete?.();
      return;
    }

    let i = 0;
    const id = window.setInterval(() => {
      i++;
      setDisplayed(text.slice(0, i));

      if (playBlip) {
        const ch = text[i - 1];
        if (ch && ch !== " " && ch !== "\n") {
          const now = performance.now();
          if (now - lastBlipRef.current > 60) {
            audio.playSfx("sfx_dialog_blip", 0.15);
            lastBlipRef.current = now;
          }
        }
      }

      if (i >= text.length) {
        window.clearInterval(id);
        intervalRef.current = null;
        setDone(true);
        if (!completedRef.current) {
          completedRef.current = true;
          onComplete?.();
        }
      }
    }, speed);
    intervalRef.current = id;

    return () => {
      if (intervalRef.current !== null) {
        window.clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [text, speed]);

  const skip = () => {
    if (intervalRef.current !== null) {
      window.clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setDisplayed(text);
    setDone(true);
    if (!completedRef.current) {
      completedRef.current = true;
      onComplete?.();
    }
  };

  return { displayed, done, skip };
}
