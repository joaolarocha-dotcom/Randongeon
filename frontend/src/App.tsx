import { useGameStore } from "./store/gameStore";
import { TitleScreen } from "./screens/TitleScreen";
import { LoreScreen } from "./screens/LoreScreen";
import { MenuScreen } from "./screens/MenuScreen";
import { CombatScreen } from "./screens/CombatScreen";
import { ChestScreen } from "./screens/ChestScreen";
import { ShopScreen } from "./screens/ShopScreen";
import { GameOverScreen } from "./screens/GameOverScreen";
import "./styles/global.css";

function App() {
  const screen = useGameStore((s) => s.screen);

  return (
    <div className="game-container">
      {screen === "title" && <TitleScreen />}
      {screen === "lore" && <LoreScreen />}
      {screen === "menu" && <MenuScreen />}
      {screen === "combat" && <CombatScreen />}
      {screen === "chest" && <ChestScreen />}
      {screen === "shop" && <ShopScreen />}
      {screen === "game_over" && <GameOverScreen />}
    </div>
  );
}

export default App
