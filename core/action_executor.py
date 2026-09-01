import logging
log = logging.getLogger(__name__)

COOLDOWN_ACTIONS = {"move", "explore", "attack", "use_item", "interact", "rest"}
FREE_ACTIONS = {"pickup", "drop", "equip", "talk", "whisper", "broadcast"}

class ActionExecutor:
    def __init__(self, bot):
        self.bot = bot

    def execute(self, action):
        typ = action.get("type")
        data = action.get("data", {})
        if typ not in COOLDOWN_ACTIONS | FREE_ACTIONS:
            log.warning("Unsupported action blocked: %s", typ)
            return False

        if typ in COOLDOWN_ACTIONS:
            if not self.bot.state.alive or not self.bot.state.can_act:
                return False

        payload = {"type": "action", "data": data}
        thought = action.get("thought")
        if thought:
            payload["thought"] = thought[:700]

        self.bot.send(payload)
        if typ in COOLDOWN_ACTIONS:
            self.bot.state.can_act = False
        return True
