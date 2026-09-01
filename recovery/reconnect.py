import time

class ReconnectManager:
    def __init__(self, bot):
        self.bot = bot
        self.delay = 1.0

    def reset(self):
        self.delay = 1.0

    def wait(self):
        time.sleep(self.delay)
        self.delay = min(30.0, self.delay * 2)
