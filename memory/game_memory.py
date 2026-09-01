import json
from pathlib import Path

class GameMemory:
    def __init__(self, path="context.json"):
        self.path = Path(path)
        self.data = {"games": [], "stats": {"games": 0, "deaths": 0}}

    def finish_game(self, state):
        self.data["stats"]["games"] += 1
        if not state.alive:
            self.data["stats"]["deaths"] += 1
        self.data["games"].append({
            "gameId": state.game_id,
            "entryType": state.entry_type,
            "turn": state.turn,
            "alive": state.alive,
            "kills": state.me.get("kills"),
        })
        self.data["games"] = self.data["games"][-100:]
        try:
            self.path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")
        except Exception:
            pass
