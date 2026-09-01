import uuid, requests

class ShopManager:
    def __init__(self, bot):
        self.bot = bot

    def listings(self):
        r = requests.get(f"{self.bot.settings.api_base}/shop/listings", timeout=15)
        r.raise_for_status()
        return r.json().get("data", r.json())

    def purchase(self, listing_id, quantity=1):
        h = self.bot.api_headers()
        h["Idempotency-Key"] = str(uuid.uuid4())
        r = requests.post(f"{self.bot.settings.api_base}/shop/purchase",
                          headers=h, json={"listingId": listing_id, "quantity": quantity}, timeout=15)
        r.raise_for_status()
        return r.json().get("data", r.json())
