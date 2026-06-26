from collections import defaultdict
from time import time

from config import SPAM_MAX_MESSAGES, SPAM_WINDOW_SECONDS

_timestamps: dict[int, list[float]] = defaultdict(list)
_CLEANUP_INTERVAL = 300
_last_cleanup: float = 0.0


def _global_cleanup() -> None:
    global _last_cleanup
    now = time()
    if now - _last_cleanup < _CLEANUP_INTERVAL:
        return
    _last_cleanup = now
    stale = [uid for uid, ts in _timestamps.items() if not ts or now - ts[-1] > 60]
    for uid in stale:
        del _timestamps[uid]


def is_spam(user_id: int) -> bool:
    now = time()
    _global_cleanup()
    history = _timestamps[user_id]
    history[:] = [t for t in history if now - t < SPAM_WINDOW_SECONDS]
    history.append(now)
    return len(history) > SPAM_MAX_MESSAGES
