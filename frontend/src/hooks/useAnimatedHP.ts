import { useEffect, useRef, useState } from "react";
import { audio } from "../components/audio/AudioEngine";

interface Options {
  /** Duração total da animação em ms (default: 800). */
  duration?: number;
  /** Se true, toca sfx_hp_tick durante a animação. */
  playTickSound?: boolean;
  /** Callback ao terminar a animação. */
  onComplete?: () => void;
}

/**
 * Anima um valor numérico (typically HP) rumo ao `target`, em steps de 1 unidade,
 * com intervalo proporcional para casar a duração total ao tempo desejado.
 *
 * Retorna o valor "exibido" no momento, que pode ser plugado em barras de HP.
 */
export function useAnimatedHP(target: number, options: Options = {}) {
  const { duration = 800, playTickSound = true, onComplete } = options;
  const [displayed, setDisplayed] = useState(target);
  const lastTickRef = useRef<number>(0);
  const completedRef = useRef(false);

  useEffect(() => {
    completedRef.current = false;
    if (displayed === target) {
      onComplete?.();
      return;
    }

    const diff = Math.abs(displayed - target);
    if (diff === 0) return;
    const step = displayed < target ? 1 : -1;
    const intervalMs = Math.max(20, duration / diff);

    const id = setInterval(() => {
      setDisplayed((curr) => {
        const next = curr + step;
        const reached = step > 0 ? next >= target : next <= target;
        if (reached) {
          clearInterval(id);
          if (!completedRef.current) {
            completedRef.current = true;
            onComplete?.();
          }
          return target;
        }
        // throttle de som
        if (playTickSound) {
          const now = performance.now();
          if (now - lastTickRef.current > 40) {
            audio.playSfx("sfx_hp_tick", 0.25);
            lastTickRef.current = now;
          }
        }
        return next;
      });
    }, intervalMs);

    return () => clearInterval(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [target, duration]);

  return displayed;
}
