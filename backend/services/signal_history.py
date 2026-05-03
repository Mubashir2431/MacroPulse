# Author Kevin Ngo, 5/3/26 - in-memory signal history system to track BUY/SELL/HOLD recommendations per stock symbol over time

from collections import defaultdict  # Kevin Ngo, 5/3/26 - allows automatic creation of empty list for new symbols
from datetime import datetime, timezone  # Kevin Ngo, 5/3/26 - used to generate accurate UTC timestamps

_history = defaultdict(list)  # Kevin Ngo, 5/3/26 - stores signal history in format {symbol: [entries]}

MAX_HISTORY_PER_SYMBOL = 50  # Kevin Ngo, 5/3/26 - limits stored history per stock to prevent excessive memory usage


def record_signal(symbol, signal_data):
    # Kevin Ngo, 5/3/26 - records a new trading signal (BUY/SELL/HOLD) for a given stock symbol

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),  # Kevin Ngo, 5/3/26 - stores current time in standardized UTC format
        "signal": signal_data.get("signal"),  # Kevin Ngo, 5/3/26 - extracts signal type from input data
        "confidence": signal_data.get("confidence"),  # Kevin Ngo, 5/3/26 - stores confidence level of the signal
    }

    _history[symbol].append(entry)  # Kevin Ngo, 5/3/26 - adds new signal entry to the symbol's history list

    # Kevin Ngo, 5/3/26 - ensures history list does not exceed maximum allowed size
    if len(_history[symbol]) > MAX_HISTORY_PER_SYMBOL:
        _history[symbol] = _history[symbol][-MAX_HISTORY_PER_SYMBOL:]  # Kevin Ngo, 5/3/26 - keeps only most recent entries


def get_history(symbol):
    # Kevin Ngo, 5/3/26 - retrieves the full signal history for a given stock symbol in chronological order
    return list(_history[symbol])  # Kevin Ngo, 5/3/26 - returns a copy to prevent accidental modification of stored data
