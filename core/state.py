from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Set

@dataclass
class RuntimeState:
    version: str = ""
    entry_type: Optional[str] = None
    game_id: Optional[str] = None
    alive: bool = True
    can_act: bool = False
    cooldown_ms: int = 0
    turn: int = 0
    last_view: Dict[str, Any] = field(default_factory=dict)
    recent_events: list = field(default_factory=list)
    rejected_actions: Set[str] = field(default_factory=set)

    def update_view(self, frame: Dict[str, Any]):
        self.game_id = frame.get("gameId", self.game_id)
        self.turn = int(frame.get("turn", self.turn) or self.turn)
        self.last_view = frame.get("view") or {}
        self.alive = self.last_view.get("self", {}).get("isAlive", True) is not False
        if "canAct" in frame:
            self.can_act = bool(frame["canAct"])
        if "cooldownRemainingMs" in frame:
            self.cooldown_ms = int(frame.get("cooldownRemainingMs") or 0)

    @property
    def view(self):
        return self.last_view

    @property
    def me(self):
        return self.view.get("self", {})

    @property
    def region(self):
        return self.view.get("currentRegion", {})

    def push_event(self, frame):
        self.recent_events.append(frame)
        self.recent_events = self.recent_events[-50:]
