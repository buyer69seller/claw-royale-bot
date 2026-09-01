import logging
from ai.possibility_engine import PossibilityEngine

log = logging.getLogger(__name__)

class DecisionEngine:
    def __init__(self, bot):
        self.bot = bot
        self.possibilities = PossibilityEngine(bot)
        self.last_candidates = []

    def choose(self):
        if not self.bot.state.alive:
            return None

        candidates = self.possibilities.generate()
        self.last_candidates = candidates
        if not candidates:
            return None

        # Safety overrides.
        me = self.bot.state.me
        region = self.bot.state.region

        if me.get("inCave") is True:
            exits = [c for c in candidates if c.action["type"] == "interact"]
            if exits:
                return exits[0].action

        if region.get("isDeathZone") is True:
            escapes = [c for c in candidates if c.action["type"] == "move" and c.survival >= 50]
            if escapes:
                return max(escapes, key=lambda c: c.score).action

        # Free actions should be performed without sacrificing a cooldown turn.
        free = [c for c in candidates if c.action["type"] in {"pickup", "equip"}]
        if free:
            # Prefer pickup/equipment before selecting the next turn action.
            for c in free:
                self.bot.executor.execute(c.action)

        cooldown = [c for c in candidates if c.action["type"] in
                    {"move","explore","attack","use_item","interact","rest"}]
        if not cooldown:
            return None

        best = max(cooldown, key=lambda c: c.score)
        log.info("Decision: %s score=%.2f reason=%s",
                 best.action["data"]["type"], best.score, best.reason)
        return {
            "type": best.action["data"]["type"],
            "data": best.action["data"],
            "thought": f"{best.reason}; score={best.score:.1f}; survival={best.survival:.1f}; risk={best.risk:.1f}"
        }

    def retry_after_target_dead(self):
        # TARGET_DEAD preserves canAct=true; recompute against the new visible set.
        self.bot.state.rejected_actions.add("target_dead")
        self.bot.decision_cycle()
