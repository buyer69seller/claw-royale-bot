import uuid
import requests

class LoadoutManager:
    def __init__(self, bot):
        self.bot = bot

    def headers(self):
        h = self.bot.api_headers()
        h["Idempotency-Key"] = str(uuid.uuid4())
        return h

    def get(self):
        r = requests.get(f"{self.bot.settings.api_base}/loadout",
                         headers=self.bot.api_headers(), timeout=15)
        r.raise_for_status()
        return r.json().get("data", r.json())

    def configure_full_set(self, main_pack, sub_pack, relics):
        if not main_pack or not sub_pack or len(relics) != 3:
            raise ValueError("FullSet membutuhkan Main + Sub + 3 relic.")
        # The exact mutation calls are kept explicit and idempotent.
        requests.put(f"{self.bot.settings.api_base}/loadout/pack",
                     headers=self.headers(), json={"packInstanceId": main_pack}, timeout=15).raise_for_status()
        requests.put(f"{self.bot.settings.api_base}/loadout/sub-pack",
                     headers=self.headers(), json={"packInstanceId": sub_pack}, timeout=15).raise_for_status()
        for idx, relic in enumerate(relics):
            requests.put(f"{self.bot.settings.api_base}/loadout/slot/{idx}",
                         headers=self.headers(), json={"relicInstanceId": relic}, timeout=15).raise_for_status()
