import { useGameStore } from "../store/gameStore";

export function ShopScreen() {
  const { jogador, loja, shopBuy, shopLeave, loading } = useGameStore();

  if (!jogador || !loja) return null;

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        padding: 16,
        gap: 12,
      }}
    >
      {/* Merchant header */}
      <div style={{ textAlign: "center" }}>
        <div style={{ fontSize: "32px", marginBottom: 8 }}>🧙</div>
        <p style={{ fontSize: "var(--font-size-sm)", color: "var(--text-dim)" }}>
          Um mercador encapuzado oferece seus itens...
        </p>
      </div>

      {/* Player coins */}
      <div style={{ textAlign: "center", fontSize: "var(--font-size-sm)", color: "var(--gold)" }}>
        Moedas: {jogador.moedas}
      </div>

      {/* Items */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 8 }}>
        {loja.ofertas.map((oferta, i) => (
          <div
            key={i}
            className="pixel-box"
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              padding: 10,
            }}
          >
            <div style={{ fontSize: "var(--font-size-sm)" }}>
              <p style={{ marginBottom: 4 }}>{oferta.nome}</p>
              <p style={{ color: "var(--text-dim)" }}>
                {oferta.bonus_atk > 0 && `ATK+${oferta.bonus_atk} `}
                {oferta.bonus_hp > 0 && `HP+${oferta.bonus_hp} `}
                {oferta.bonus_esq > 0 && `ESQ+${Math.round(oferta.bonus_esq * 100)}% `}
              </p>
            </div>
            <button
              className="pixel-btn"
              onClick={() => shopBuy(i)}
              disabled={loading || jogador.moedas < oferta.preco}
              style={{ fontSize: "var(--font-size-sm)" }}
            >
              <span style={{ color: "var(--gold)" }}>{oferta.preco}$</span>
            </button>
          </div>
        ))}
      </div>

      {/* Leave */}
      <div style={{ textAlign: "center" }}>
        <button className="pixel-btn" onClick={shopLeave} disabled={loading}>
          SAIR DA LOJA
        </button>
      </div>
    </div>
  );
}
