import json
import logging
import websocket

log = logging.getLogger(__name__)

class JoinSocket:
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers
        self.ws = None

    def connect(self):
        self.ws = websocket.create_connection(self.url, header=self.headers, timeout=40)
        return self.ws

    def send(self, payload):
        self.ws.send(json.dumps(payload, separators=(",", ":")))

    def recv(self):
        raw = self.ws.recv()
        if raw is None:
            return None
        return json.loads(raw)

    def close(self):
        try:
            if self.ws:
                self.ws.close()
        except Exception:
            pass
