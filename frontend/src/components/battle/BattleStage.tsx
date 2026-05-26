import type { ReactNode } from "react";

interface Props {
  bgImage: string;
  children: ReactNode;
}

/**
 * Metade superior da CombatScreen: background da arena + sprites posicionados absolutamente.
 */
export function BattleStage({ bgImage, children }: Props) {
  return (
    <div
      className="poke-arena fade-in"
      style={{
        backgroundImage: `url(${bgImage})`,
        backgroundSize: "115%",
        backgroundPosition: "center 60%",
        flex: "0 0 68%",
        position: "relative",
      }}
    >
      {children}
    </div>
  );
}
