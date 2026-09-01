import json
import logging
import random
import time

from config.settings import Settings
from core.state import RuntimeState
from core.websocket import JoinSocket
from core.event_manager import EventManager
from core.action_executor import ActionExecutor
from ai.decision_engine import DecisionEngine
from inventory.loadout import LoadoutManager
from recovery.death_detector import DeathDetector
from recovery.reconnect import ReconnectManager
from recovery.auto_restart import AutoRestart
from memory.game_memory import GameMemory

class AutonomousBot:
    def __init__(self):
        self.settings = Settings()
        self.settings.validate()
        logging.basicConfig(level=self.settings.log_level,
                            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        self.log = logging.getLogger("AutonomousBot")
        self.state = RuntimeState()
        self.ws = None
        self.events = EventManager(self)
        self.executor = ActionExecutor(self)
        self.decision = DecisionEngine(self)
        self.loadout = LoadoutManager(self)
        self.death = DeathDetector(self)
        self.lifecycle = AutoRestart(self)
        self.reconnect = ReconnectManager(self)
        self.memory = GameMemory()

    def api_headers(self):
        return {
            "X-API-Key": self.settings.api_key,
            "X-Version": self.state.version,
            "Content-Type": "application/json",
        }

    def refresh_version(self):
        import requests
        r = requests.get(f"{self.settings.api_base}/version", timeout=15)
        r.raise_for_status()
        data = r.json().get("data", r.json())
        self.state.version = str(data["version"])
        self.log.info("API version=%s", self.state.version)

    def account(self):
        import requests
        r = requests.get(f"{self.settings.api_base}/accounts/me",
                         headers=self.api_headers(), timeout=15)
        r.raise_for_status()
        return r.json().get("data", r.json())

    def choose_entry(self, welcome):
        decision = welcome.get("decision")
        readiness = welcome.get("readiness", {})
        free_ok = bool(readiness.get("freeRoom", {}).get("ok"))
        paid_ok = bool(readiness.get("paidRoom", {}).get("ok"))

        if decision == "FREE_ONLY":
            return "free"
        if decision == "PAID_ONLY":
            if self.settings.paid_enabled and paid_ok:
                return "paid"
            raise RuntimeError("Server hanya menerima paid, tetapi paid disabled/not ready.")
        if decision == "ALREADY_IN_GAME":
            return None

        if self.settings.entry == "paid":
            if self.settings.paid_enabled and paid_ok:
                return "paid"
            raise RuntimeError("Paid diminta tetapi tidak ready.")
        if self.settings.entry == "free":
            if free_ok:
                return "free"
            if self.settings.paid_enabled and paid_ok:
                return "paid"
            raise RuntimeError("Free tidak ready dan paid tidak tersedia.")

        # auto: prefer paid only when explicitly enabled, otherwise free.
        if self.settings.paid_enabled and paid_ok:
            return "paid"
        if free_ok:
            return "free"
        raise RuntimeError("Tidak ada entry type yang ready.")

    def join_and_play(self):
        self.state.can_act = False
        headers = [
            f"X-Version: {self.state.version}",
            f"Authorization: mr-auth {self.settings.api_key}",
        ]
        self.ws = JoinSocket(self.settings.ws_join, headers)
        self.ws.connect()
        self.log.info("Connected /ws/join")

        while not self.lifecycle.end_session:
            frame = self.ws.recv()
            if frame is None:
                break
            typ = frame.get("type")
            if typ == "welcome":
                entry = self.choose_entry(frame)
                if entry:
                    self.state.entry_type = entry
                    self.ws.send({"type": "hello", "entryType": entry})
                continue
            if typ == "assigned" or typ == "joined":
                self.state.game_id = frame.get("gameId")
                self.log.info("Game assigned: %s", self.state.game_id)
                continue
            if typ == "sign_required":
                raise RuntimeError("Paid signing diperlukan. Signer EIP-712 belum dikonfigurasi.")
            self.events.dispatch(frame)
            if self.death.run_ended:
                break
            if self.lifecycle.game_finished:
                break

    def send(self, payload):
        if self.ws:
            self.ws.send(payload)
            self.log.debug("SEND %s", payload)

    def decision_cycle(self):
        action = self.decision.choose()
        if action:
            self.executor.execute(action)

    def run_forever(self):
        delay = 1.0
        while True:
            try:
                self.lifecycle.reset_session()
                self.refresh_version()
                self.state.rejected_actions.clear()
                self.join_and_play()
                self.memory.finish_game(self.state)
                delay = 1.0
                if not self.settings.auto_restart:
                    break
            except KeyboardInterrupt:
                self.log.info("Stopped.")
                break
            except Exception as exc:
                self.log.exception("Session failed: %s", exc)
                if not self.settings.auto_restart:
                    break
                time.sleep(delay)
                delay = min(30.0, delay * 2)
            finally:
                try:
                    if self.ws:
                        self.ws.close()
                except Exception:
                    pass
