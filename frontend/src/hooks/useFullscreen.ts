import { useCallback, useEffect, useState } from "react";

/**
 * Toggle de fullscreen baseado no Fullscreen API do navegador.
 *
 * Retorna `isFullscreen` reativo e `toggle()` que solicita/sai do modo.
 * Falhas silenciosas (alguns navegadores bloqueiam fora de gesto do usuário).
 */
export function useFullscreen() {
  const [isFullscreen, setIsFullscreen] = useState<boolean>(
    typeof document !== "undefined" && !!document.fullscreenElement
  );

  useEffect(() => {
    const onChange = () => setIsFullscreen(!!document.fullscreenElement);
    document.addEventListener("fullscreenchange", onChange);
    return () => document.removeEventListener("fullscreenchange", onChange);
  }, []);

  const toggle = useCallback(async () => {
    try {
      if (document.fullscreenElement) {
        await document.exitFullscreen();
      } else {
        await document.documentElement.requestFullscreen();
      }
    } catch {
      // ignore — alguns browsers bloqueiam sem gesto do usuário
    }
  }, []);

  return { isFullscreen, toggle };
}
