import time
from collections import defaultdict, deque
from typing import Tuple
from fastapi import HTTPException, status


class RateLimiter:
    def __init__(self, max_events: int, window_seconds: float):
        self.max_events = max_events
        self.window = window_seconds
        self.events = defaultdict(lambda: deque())

    def check(self, key: Tuple[str, ...]):
        now = time.time()
        q = self.events[key]
        # purge old
        while q and now - q[0] > self.window:
            q.popleft()
        if len(q) >= self.max_events:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit excedido")
        q.append(now)


# Para /asistencia: máx 4 eventos cada 10 segundos por (empleado_id, tipo)
asistencia_limiter = RateLimiter(max_events=4, window_seconds=10.0)

