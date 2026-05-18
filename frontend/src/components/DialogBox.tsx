import type { ReactNode } from "react";

interface Props {
  children: ReactNode;
  style?: React.CSSProperties;
}

export function DialogBox({ children, style }: Props) {
  return (
    <div
      className="pixel-box"
      style={{
        position: "absolute",
        bottom: 8,
        left: 8,
        right: 8,
        minHeight: 80,
        fontSize: "var(--font-size-sm)",
        ...style,
      }}
    >
      {children}
    </div>
  );
}
