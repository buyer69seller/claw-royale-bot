class EquipmentManager:
    def __init__(self, bot):
        self.bot = bot

    def upgrades(self):
        me = self.bot.state.me
        return [
            x for x in (me.get("inventory") or [])
            if any(k in str(x.get("category", x.get("type",""))).lower()
                   for k in ("weapon", "armor"))
        ]
