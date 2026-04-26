"""
Person 3 - US16: In-memory signal history store.
Records each BUY/SELL/HOLD signal generated per symbol so users can
view a log of how the recommendation has changed over time.
"""

from collections import defaultdict
from datetime import datetime, timezone

_history = defaultdict(list)
MAX_HISTORY_PER_SYMBOL = 50


def record_signal(symbol, signal_data):
    """Append a new signal entry to the history for the given symbol."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "signal": signal_data.get("signal"),
        "confidence": signal_data.get("confidence"),
    }
    _history[symbol].append(entry)
    # Keep only the most recent entries to cap memory usage
    if len(_history[symbol]) > MAX_HISTORY_PER_SYMBOL:
        _history[symbol] = _history[symbol][-MAX_HISTORY_PER_SYMBOL:]


def get_history(symbol):
    """Return the recorded signal history for a symbol (oldest first)."""
    return list(_history[symbol])
