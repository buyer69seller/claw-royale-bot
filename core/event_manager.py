import logging
log = logging.getLogger(__name__)

class EventManager:
    def __init__(self, bot):
        self.bot = bot

    def dispatch(self, frame):
        typ = frame.get("type")
        if not typ:
            return

        self.bot.state.push_event(frame)

        handler = getattr(self, f"on_{typ}", self.on_generic)
        handler(frame)

    def on_generic(self, frame):
        if frame.get("type") == "agent_died":
            return
        if frame.get("meta", {}).get("youDied") is True:
            self.bot.death.end_run("meta.youDied")

    def on_agent_view(self, frame):
        self.bot.state.update_view(frame)
        self.bot.decision_cycle()

    def on_turn_advanced(self, frame):
        self.bot.state.update_view(frame)
        if self.bot.state.alive:
            self.bot.decision_cycle()

    def on_can_act_changed(self, frame):
        self.bot.state.can_act = bool(frame.get("canAct"))
        self.bot.state.cooldown_ms = int(frame.get("cooldownRemainingMs") or 0)
        if self.bot.state.can_act and self.bot.state.alive:
            self.bot.decision_cycle()

    def on_action_result(self, frame):
        self.bot.state.can_act = bool(frame.get("canAct", self.bot.state.can_act))
        self.bot.state.cooldown_ms = int(frame.get("cooldownRemainingMs") or 0)
        err = frame.get("error") or {}
        code = err.get("code")
        if code == "AGENT_DEAD":
            self.bot.death.end_run("AGENT_DEAD")
        elif code == "TARGET_DEAD":
            self.bot.decision.retry_after_target_dead()
        elif code in {"ACTION_COOLDOWN", "COOLDOWN_ACTIVE"}:
            self.bot.state.can_act = False
        elif code == "VERSION_MISMATCH":
            self.bot.lifecycle.version_mismatch = True

    def on_action_received(self, frame):
        pass

    def on_agent_died(self, frame):
        if (frame.get("meta") or {}).get("youDied") is True:
            self.bot.death.end_run("agent_died.meta.youDied")

    def on_game_ended(self, frame):
        self.bot.lifecycle.game_finished = True

    def on_game_settled(self, frame):
        self.bot.lifecycle.game_settled = True

    def on_deathzone_warning(self, frame):
        self.bot.state.push_event(frame)

    def on_error(self, frame):
        log.warning("Server error frame: %s", frame)
