import { useEffect, useMemo, useState } from "react";
import { useGameStore } from "../store/gameStore";
import { BattleStage } from "../components/battle/BattleStage";
import { EnemySprite } from "../components/battle/EnemySprite";
import { PlayerSprite } from "../components/battle/PlayerSprite";
import { EnemyStatusBox } from "../components/battle/EnemyStatusBox";
import { PlayerStatusBox } from "../components/battle/PlayerStatusBox";
import { BattleDialog } from "../components/battle/BattleDialog";
import { BattleMenu } from "../components/battle/BattleMenu";
import { getArenaBg } from "../assets/bgMap";
import { useAnimatedHP } from "../hooks/useAnimatedHP";

/**
 * Tela de combate em estilo Pokemon Gen 1.
 *
 * Layout:
 *   ┌─────────────────────────────────────┐
 *   │ [ENEMY STATUS]        [enemy sprite]│  60% arena
 *   │ [player sprite]      [PLAYER STATUS]│
 *   ├─────────────────────────────────────┤
 *   │  [BattleDialog OR BattleMenu]       │  40% UI
 *   └─────────────────────────────────────┘
 */
export function CombatScreen() {
  const jogador = useGameStore((s) => s.jogador);
  const inimigo = useGameStore((s) => s.inimigo);
  const bossEnraged = useGameStore((s) => s.bossEnraged);
  const animPhase = useGameStore((s) => s.animPhase);
  const currentDialog = useGameStore((s) => s.currentDialog);
  const dialogQueue = useGameStore((s) => s.dialogQueue);
  const combatAttack = useGameStore((s) => s.combatAttack);
  const combatDodge = useGameStore((s) => s.combatDodge);
  const combatFlee = useGameStore((s) => s.combatFlee);
  const combatUseItem = useGameStore((s) => s.combatUseItem);
  const loading = useGameStore((s) => s.loading);
  const setAnimPhase = useGameStore((s) => s.setAnimPhase);
  const enqueueDialog = useGameStore((s) => s.enqueueDialog);
  const [showInventory, setShowInventory] = useState(false);

  // HPs animados
  const animatedPlayerHP = useAnimatedHP(jogador?.hp ?? 0, { duration: 700, playTickSound: true });
  const animatedEnemyHP = useAnimatedHP(inimigo?.hp ?? 0, { duration: 700, playTickSound: true });

  // Estado local de animação dos sprites
  const [enemyAnim, setEnemyAnim] = useState<string>("slide-in-right");
  const [playerAnim, setPlayerAnim] = useState<string>("slide-in-left");

  // Limpar slide-in após 600ms
  useEffect(() => {
    const t1 = setTimeout(() => setEnemyAnim(""), 700);
    const t2 = setTimeout(() => setPlayerAnim(""), 700);
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
    };
  }, []);

  // Reage a mudanças de animPhase para animar sprites.
  // Aplicar classes de animação como efeito colateral síncrono ao mudar a fase
  // é intencional aqui — animação dura ~700ms e o cleanup limpa.
  useEffect(() => {
    if (animPhase === "player_action") {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setPlayerAnim("attack-bounce");
      const t = setTimeout(() => setEnemyAnim("flash-white shake"), 180);
      const t2 = setTimeout(() => {
        setPlayerAnim("");
        setEnemyAnim("");
      }, 700);
      return () => {
        clearTimeout(t);
        clearTimeout(t2);
      };
    }
    if (animPhase === "enemy_action") {
      setEnemyAnim("attack-bounce-rev");
      const t = setTimeout(() => setPlayerAnim("flash-white shake"), 180);
      const t2 = setTimeout(() => {
        setEnemyAnim("");
        setPlayerAnim("");
      }, 700);
      return () => {
        clearTimeout(t);
        clearTimeout(t2);
      };
    }
    if (animPhase === "victory") {
      setEnemyAnim("faint-down");
    }
    if (animPhase === "defeat") {
      setPlayerAnim("faint-down");
    }
    if (animPhase === "flee") {
      setPlayerAnim("flee-out-left");
    }
  }, [animPhase]);

  // Disparar o início do combate: enfileira mensagens do intro
  useEffect(() => {
    if (animPhase === "intro" && !currentDialog && dialogQueue.length > 0) {
      // O store já enfileirou — força o início chamando nextDialog via enqueue de nada
      // (alternativa: chamar advance da fila diretamente)
      // Aqui não fazemos nada: nextDialog é chamado pela BattleDialog quando termina cada texto
    }
  }, [animPhase, currentDialog, dialogQueue.length]);

  const bgImage = useMemo(() => {
    if (!jogador) return getArenaBg(1);
    return getArenaBg(jogador.andar, inimigo?.dificuldade === 3 ? "boss" : undefined);
    // jogador é referenciado só por .andar, que já está nas deps; evita re-cálculo a cada update
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jogador?.andar, inimigo?.dificuldade]);

  if (!jogador || !inimigo) return null;

  // Decidir se mostra BattleMenu ou BattleDialog
  const hasDialog = !!currentDialog || dialogQueue.length > 0;
  const showMenu = animPhase === "idle" && !hasDialog && !loading;

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
      <BattleStage bgImage={bgImage}>
        {/* Status do inimigo no topo-esquerdo */}
        <div style={{ position: "absolute", top: 8, left: 8 }}>
          <EnemyStatusBox inimigo={inimigo} displayedHP={animatedEnemyHP} enraged={bossEnraged} />
        </div>

        {/* Sprite do inimigo no topo-direito — escala menor para criar perspectiva */}
        <EnemySprite inimigo={inimigo} animClass={enemyAnim} scale={2.5} />

        {/* Sprite do jogador no meio-esquerdo — escala maior para parecer "à frente" */}
        <PlayerSprite animClass={playerAnim} scale={4} />

        {/* Status do jogador no meio-direito */}
        <div style={{ position: "absolute", bottom: 8, right: 8 }}>
          <PlayerStatusBox jogador={jogador} displayedHP={animatedPlayerHP} />
        </div>
      </BattleStage>

      {/* Metade inferior: UI */}
      <div
        style={{
          flex: "1 1 32%",
          padding: 8,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          background: "transparent",
        }}
      >
        {showMenu ? (
          showInventory ? (
            <BattleMenu
              prompt="USAR ITEM"
              items={[
                ...jogador.inventario.map((it, idx) => ({
                  label: `${it.nome.toUpperCase()}`,
                  onClick: async () => {
                    setShowInventory(false);
                    await combatUseItem(idx);
                  },
                  disabled: loading,
                })),
                {
                  label: "VOLTAR",
                  onClick: () => setShowInventory(false),
                  disabled: loading,
                },
              ]}
            />
          ) : (
            <BattleMenu
              prompt={`O que ${jogador.nome.toUpperCase()} vai fazer?`}
              items={[
                {
                  label: "LUTAR",
                  onClick: combatAttack,
                  disabled: loading,
                },
                {
                  label: "ITEM",
                  onClick: () => {
                    if (jogador.inventario.length === 0) {
                      enqueueDialog("Inventário vazio.");
                      return;
                    }
                    setShowInventory(true);
                  },
                  disabled: loading,
                },
                {
                  label: "ESQUIVAR",
                  onClick: combatDodge,
                  disabled: loading,
                },
                {
                  label: "FUGIR",
                  onClick: combatFlee,
                  disabled: loading,
                },
              ]}
            />
          )
        ) : (
          <BattleDialog
            interactive
            onQueueEmpty={() => {
              // Libera o menu de ações quando todos os diálogos foram consumidos
              // (apenas para fases intermediárias; victory/defeat/flee são tratados via setTimeout no store)
              if (animPhase === "intro" || animPhase === "enemy_action" || animPhase === "player_action") {
                setAnimPhase("idle");
              }
            }}
          />
        )}
      </div>
    </div>
  );
}
