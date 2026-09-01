import requests

class ItemManager:
    def __init__(self, bot):
        self.bot = bot

    def relics(self):
        r = requests.get(f"{self.bot.settings.api_base}/inventory/relics?limit=50",
                         headers=self.bot.api_headers(), timeout=15)
        r.raise_for_status()
        return r.json().get("data", r.json())

    def packs(self):
        r = requests.get(f"{self.bot.settings.api_base}/inventory/packs?limit=50",
                         headers=self.bot.api_headers(), timeout=15)
        r.raise_for_status()
        return r.json().get("data", r.json())
