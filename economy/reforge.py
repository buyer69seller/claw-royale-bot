import uuid, requests

class ReforgeManager:
    def __init__(self, bot):
        self.bot = bot

    def reforge(self, relic_id, item_key):
        payload = {
            "relicInstanceId": relic_id,
            "itemKey": item_key,
            "idempotencyKey": str(uuid.uuid4()),
        }
        r = requests.post(f"{self.bot.settings.api_base}/reforge",
                          headers=self.bot.api_headers(), json=payload, timeout=15)
        r.raise_for_status()
        return r.json().get("data", r.json())
