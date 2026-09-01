from core.state import RuntimeState
from ai.possibility_engine import PossibilityEngine

class Dummy:
    pass

def test_generate_escape():
    bot = Dummy()
    bot.state = RuntimeState(
        can_act=True,
        last_view={
            "self": {"isAlive": True, "hp": 100, "maxHp": 100, "inventory": []},
            "currentRegion": {
                "isDeathZone": True,
                "connections": ["safe-1"],
                "items": [],
            },
            "pendingDeathzones": []
        }
    )
    p = PossibilityEngine(bot).generate()
    assert any(c.action["data"]["type"] == "move" for c in p)
