from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class Candidate:
    action: Dict[str, Any]
    reason: str
    base_score: float = 0.0
    risk: float = 0.0
    survival: float = 0.0
    reward: float = 0.0
    information: float = 0.0

    @property
    def score(self):
        return self.base_score + self.survival + self.reward + self.information - self.risk

class PossibilityEngine:
    """Enumerates all actions that can be justified from the currently visible state."""

    def __init__(self, bot):
        self.bot = bot

    def generate(self) -> List[Candidate]:
        s = self.bot.state
        me, region = s.me, s.region
        out = []

        # Free actions: they do not consume the turn.
        for item in region.get("items") or []:
            iid = item.get("id") or item.get("itemId") or item.get("instanceId")
            if iid:
                out.append(Candidate(
                    {"type":"pickup","data":{"type":"pickup","itemId":iid}},
                    "ground loot available", reward=8, information=1))

        for item in me.get("inventory") or []:
            category = str(item.get("category", item.get("type",""))).lower()
            iid = item.get("id") or item.get("itemId") or item.get("instanceId")
            if iid and ("weapon" in category or "armor" in category):
                out.append(Candidate(
                    {"type":"equip","data":{"type":"equip","itemId":iid}},
                    "candidate equipment", reward=3))

        # Cooldown actions.
        if s.can_act:
            for dest in region.get("connections") or []:
                out.append(Candidate(
                    {"type":"move","data":{"type":"move","regionId":dest}},
                    "adjacent region", survival=5, risk=self.move_risk(dest)))

            if region.get("isDeathZone") is True:
                for dest in region.get("connections") or []:
                    out.append(Candidate(
                        {"type":"move","data":{"type":"move","regionId":dest}},
                        "escape death zone", survival=60, risk=self.move_risk(dest)))

            if me.get("inCave") is True:
                for x in region.get("interactables") or []:
                    iid = x.get("interactableId") or x.get("id")
                    if iid:
                        out.append(Candidate(
                            {"type":"interact","data":{"type":"interact","interactableId":iid}},
                            "exit cave", survival=80, risk=0))

            hp = float(me.get("hp", 0) or 0)
            max_hp = float(me.get("maxHp", 100) or 100)
            if hp < max_hp * 0.55:
                for item in me.get("inventory") or []:
                    name = str(item.get("name", item.get("itemName",""))).lower()
                    iid = item.get("id") or item.get("itemId") or item.get("instanceId")
                    if iid and any(k in name for k in ("medkit","bandage","food","energy","heal")):
                        out.append(Candidate(
                            {"type":"use_item","data":{"type":"use_item","itemId":iid}},
                            "low HP recovery", survival=50, risk=max(0, 25-hp)))

            for enemy in self._targets():
                tid = enemy.get("id") or enemy.get("agentId") or enemy.get("instanceId")
                if tid:
                    out.append(Candidate(
                        {"type":"attack","data":{"type":"attack","targetId":tid}},
                        "visible target", reward=20,
                        risk=self.attack_risk(enemy),
                        survival=self.attack_survival(enemy)))

            if self._can_explore():
                out.append(Candidate(
                    {"type":"explore","data":{"type":"explore"}},
                    "ruin progress", reward=20, risk=self.explore_risk(),
                    information=4))

            out.append(Candidate(
                {"type":"rest","data":{"type":"rest"}},
                "recover EP", survival=8, risk=2))

        return out

    def _targets(self):
        targets = []
        for x in self.bot.state.view.get("visibleAgents") or []:
            if x.get("isAlive") is not False and not x.get("isGuardian"):
                targets.append(x)
        for x in self.bot.state.view.get("visibleMonsters") or []:
            if x.get("isAlive") is not False:
                targets.append(x)
        return targets

    def _can_explore(self):
        r = self.bot.state.region
        return (
            not r.get("isDeathZone")
            and (r.get("ruinGauge") is not None)
            and r.get("ruinOccupant") in (None, "")
        )

    def move_risk(self, dest):
        pending = {
            x.get("id") for x in self.bot.state.view.get("pendingDeathzones", [])
            if isinstance(x, dict)
        }
        return 35 if dest in pending else 5

    def attack_risk(self, enemy):
        me = self.bot.state.me
        hp = float(me.get("hp", 0) or 0)
        enemy_atk = float(enemy.get("atk", 0) or 0)
        if hp <= enemy_atk:
            return 45
        return max(2, enemy_atk * 0.5)

    def attack_survival(self, enemy):
        hp = float(enemy.get("hp", 100) or 100)
        return max(0, 20 - hp / 10)

    def explore_risk(self):
        alert = float(self.bot.state.me.get("alertGauge", 0) or 0)
        return 5 + alert * 2
