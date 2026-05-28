interface Props {
  andar: number;
}

/**
 * Overlay preto com texto "ANDAR N" — usa a animação CSS .floor-overlay
 * que faz fade-in e fade-out em 1s total.
 */
export function FloorTransition({ andar }: Props) {
  return (
    <div className="floor-overlay">
      <span className="floor-overlay-text">ANDAR {andar}</span>
    </div>
  );
}
