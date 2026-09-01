class ConsumableManager:
    def __init__(self, bot):
        self.bot = bot

    def healing_items(self):
        return [
            x for x in (self.bot.state.me.get("inventory") or [])
            if any(k in str(x.get("name", x.get("itemName",""))).lower()
                   for k in ("medkit", "bandage", "heal", "food", "energy"))
        ]
