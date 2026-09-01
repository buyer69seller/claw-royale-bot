import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    api_key: str = os.getenv("CLAW_API_KEY", "")
    api_base: str = os.getenv("CLAW_API_BASE", "https://cdn.clawroyale.ai/api")
    ws_join: str = os.getenv("CLAW_WS_JOIN", "wss://cdn.clawroyale.ai/ws/join")
    entry: str = os.getenv("CLAW_ENTRY", "free").lower()
    paid_enabled: bool = os.getenv("CLAW_PAID_ENABLED", "false").lower() == "true"
    auto_restart: bool = os.getenv("CLAW_AUTO_RESTART", "true").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()

    def validate(self):
        if not self.api_key:
            raise RuntimeError("CLAW_API_KEY belum diisi.")
        if self.entry not in {"free", "paid", "auto"}:
            raise RuntimeError("CLAW_ENTRY harus free, paid, atau auto.")
        if self.entry == "paid" and not self.paid_enabled:
            raise RuntimeError("CLAW_ENTRY=paid tetapi CLAW_PAID_ENABLED=false.")
