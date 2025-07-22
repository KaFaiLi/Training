import asyncio
import time
from collections import deque

class RateLimiter:
    """Limits the number of calls within a specific time period."""
    def __init__(self, max_calls: int, period: int):
        self.max_calls = max_calls
        self.period = period
        self.calls = deque()

    async def __aenter__(self):
        while len(self.calls) >= self.max_calls:
            elapsed = time.monotonic() - self.calls[0]
            if elapsed < self.period:
                await asyncio.sleep(self.period - elapsed)
            else:
                self.calls.popleft()
        self.calls.append(time.monotonic())
        return self

    async def __aexit__(self, exc_type, exc_val, tb):
        pass 