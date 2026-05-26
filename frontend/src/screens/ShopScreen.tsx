import { useEffect, useState } from "react";
import { useGameStore } from "../store/gameStore";
import { MERCHANT_SPRITE, COIN_ICON, FALLBACK_SPRITE_PATH } from "../assets/spriteMap";
import { BG } from "../assets/bgMap";
import { audio } from "../components/audio/AudioEngine";

export function ShopScreen() {
  const { jogador, loja, shopBuy, shopLeave, loading } = useGameStore();
  const [merchSrc, setMerchSrc] = useState(MERCHANT_SPRITE.src);
  const [coinSrc, setCoinSrc] = useState(COIN_ICON.src);

  useEffect(() => {
    audio.playMusic("bgm_shop");
  }, []);

  if (!jogador || !loja) return null;

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
      {/* Cenário superior */}
      <div
        className="poke-arena"
        style={{
          backgroundImage: `url(${BG.shopInterior})`,
          flex: "0 0 40%",
          position: "relative",
        }}
      >
        <img
          src={merchSrc}
          alt="Mercador"
          onError={() => {
            if (merchSrc !== FALLBACK_SPRITE_PATH) setMerchSrc(FALLBACK_SPRITE_PATH);
          }}
          style={{
            position: "absolute",
            left: "50%",
            bottom: "5%",
            transform: "translateX(-50%)",
            width: MERCHANT_SPRITE.w * 2.5,
            height: MERCHANT_SPRITE.h * 2.5,
            imageRendering: "pixelated",
          }}
          draggable={false}
        />
        {/* Indicador de moedas */}
        <div
          className="poke-status"
          style={{
            position: "absolute",
            top: 8,
            right: 8,
            fontSize: 7,
            display: "flex",
            alignItems: "center",
            gap: 4,
          }}
        >
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
        </div>
      </div>

      {/* Painel de ofertas */}
      <div
        style={{
          flex: "1 1 60%",
          padding: 8,
          display: "flex",
          flexDirection: "column",
          gap: 6,
          overflow: "hidden",
        }}
      >
        <div className="poke-dialog" style={{ fontSize: 7, padding: "6px 8px", minHeight: 0 }}>
          O mercador oferece itens. O que vai comprar?
        </div>

        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            gap: 4,
            overflow: "auto",
          }}
        >
          {loja.ofertas.map((oferta, i) => {
            const podeComprar = !loading && jogador.moedas >= oferta.preco;
            return (
              <div
                key={i}
                className="poke-box"
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  padding: "5px 8px",
                  fontSize: 7,
                }}
              >
                <div style={{ flex: 1 }}>
                  <p style={{ marginBottom: 2, fontWeight: "bold" }}>{oferta.nome}</p>
                  <p style={{ color: "#444" }}>
                    {oferta.bonus_atk > 0 && `ATK+${oferta.bonus_atk} `}
                    {oferta.bonus_hp > 0 && `HP+${oferta.bonus_hp} `}
                    {oferta.bonus_esq > 0 && `ESQ+${Math.round(oferta.bonus_esq * 100)}% `}
                  </p>
                </div>
                <button
                  className="poke-btn"
                  onClick={() => {
                    audio.playSfx("sfx_menu_select");
                    shopBuy(i);
                  }}
                  disabled={!podeComprar}
                  style={{ fontSize: 7, padding: "4px 8px", color: "#d8a000" }}
                >
                  {oferta.preco}$
                </button>
              </div>
            );
          })}
        </div>

        <div style={{ textAlign: "center" }}>
          <button className="poke-btn" onClick={shopLeave} disabled={loading}>
            SAIR DA LOJA
          </button>
        </div>
      </div>
    </div>
  );
}
