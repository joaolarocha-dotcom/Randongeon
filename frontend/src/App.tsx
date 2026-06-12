import { useEffect } from "react";
import { useGameStore } from "./store/gameStore";
import { MainMenuScreen } from "./screens/MainMenuScreen";
import { TutorialsScreen } from "./screens/TutorialsScreen";
import { LoadGameScreen } from "./screens/LoadGameScreen";
import { SettingsScreen } from "./screens/SettingsScreen";
import { LeaderboardScreen } from "./screens/LeaderboardScreen";
import { TitleScreen } from "./screens/TitleScreen";
import { LoreScreen } from "./screens/LoreScreen";
import { MenuScreen } from "./screens/MenuScreen";
import { CombatScreen } from "./screens/CombatScreen";
import { ChestScreen } from "./screens/ChestScreen";
import { ShopScreen } from "./screens/ShopScreen";
import { GameOverScreen } from "./screens/GameOverScreen";
import { VictoryScreen } from "./screens/VictoryScreen";
import { FloorTransition } from "./components/transitions/FloorTransition";
import { useFullscreen } from "./hooks/useFullscreen";
import "./styles/global.css";

function App() {
  const screen = useGameStore((s) => s.screen);
  const floorTransitionAndar = useGameStore((s) => s.floorTransitionAndar);
  const { toggle: toggleFullscreen } = useFullscreen();

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "F11") {
        e.preventDefault();
        toggleFullscreen();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [toggleFullscreen]);

  return (
    <div className="game-container">
      {screen === "main_menu" && <MainMenuScreen />}
      {screen === "tutorials" && <TutorialsScreen />}
      {screen === "load_game" && <LoadGameScreen />}
      {screen === "settings" && <SettingsScreen />}
      {screen === "leaderboard" && <LeaderboardScreen />}
      {screen === "title" && <TitleScreen />}
      {screen === "lore" && <LoreScreen />}
      {screen === "menu" && <MenuScreen />}
      {screen === "combat" && <CombatScreen />}
      {screen === "chest" && <ChestScreen />}
      {screen === "shop" && <ShopScreen />}
      {screen === "game_over" && <GameOverScreen />}
      {screen === "victory" && <VictoryScreen />}

      {floorTransitionAndar !== null && <FloorTransition andar={floorTransitionAndar} />}
    </div>
  );
}

export default App;
