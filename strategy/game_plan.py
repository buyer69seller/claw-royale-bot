class GamePlan:
    def __init__(self, bot):
        self.bot = bot

    def phase(self):
        turn = self.bot.state.turn
        if turn < 15:
            return "early"
        if turn < 40:
            return "mid"
        return "late"
