from collections import defaultdict
from time import time

from config import SPAM_MAX_MESSAGES, SPAM_WINDOW_SECONDS

_timestamps: dict[int, list[float]] = defaultdict(list)


def is_spam(user_id: int) -> bool:
    now = time()
    history = _timestamps[user_id]
    history[:] = [t for t in history if now - t < 60]
    history.append(now)
    recent = [t for t in history if now - t < SPAM_WINDOW_SECONDS]
    return len(recent) > SPAM_MAX_MESSAGES
