import { useEffect, useState } from "react";

interface Props {
  text: string;
  speed?: number;
  onComplete?: () => void;
}

export function TypewriterText({ text, speed = 40, onComplete }: Props) {
  const [displayed, setDisplayed] = useState("");
  const [done, setDone] = useState(false);

  useEffect(() => {
    // Reset síncrono ao mudar text/speed é intencional: sem ele o componente
    // mostraria o texto antigo enquanto o novo digita.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setDisplayed("");
    setDone(false);
    let i = 0;
    const interval = setInterval(() => {
      i++;
      setDisplayed(text.slice(0, i));
      if (i >= text.length) {
        clearInterval(interval);
        setDone(true);
        onComplete?.();
      }
    }, speed);
    return () => clearInterval(interval);
    // onComplete intencionalmente fora das deps para evitar re-disparo a cada render
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [text, speed]);

  const skip = () => {
    if (!done) {
      setDisplayed(text);
      setDone(true);
      onComplete?.();
    }
  };

  return (
    <p onClick={skip} style={{ cursor: done ? "default" : "pointer", lineHeight: "1.8" }}>
      {displayed}
      {!done && <span className="blink">▌</span>}
    </p>
  );
}
