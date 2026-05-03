"""
Person 3 - US17: In-memory watchlist store.
Stores a list of stock symbols per user session (keyed by user_id).
Supports add, remove, and retrieve operations.
"""

_watchlists = {}  # {user_id: [symbol, ...]}


def get_watchlist(user_id="default"):
    """Return the current watchlist for the given user."""
    return list(_watchlists.get(user_id, []))


def add_to_watchlist(symbol, user_id="default"):
    """Add a symbol to the watchlist (no-op if already present)."""
    if user_id not in _watchlists:
        _watchlists[user_id] = []
    if symbol not in _watchlists[user_id]:
        _watchlists[user_id].append(symbol)


def remove_from_watchlist(symbol, user_id="default"):
    """Remove a symbol from the watchlist (no-op if not present)."""
    if user_id in _watchlists:
        _watchlists[user_id] = [s for s in _watchlists[user_id] if s != symbol]
