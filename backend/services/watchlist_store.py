Author: # Kevin Ngo, 5/2/26 - in-memory watchlist storage system that keeps track of stock symbols for each user session


_watchlists = {}  # Kevin Ngo, 5/2/26 - dictionary storing watchlists in format {user_id: [symbol, symbol, ...]}


def get_watchlist(user_id="default"):
    # Kevin Ngo, 5/2/26 - returns a copy of the user's watchlist so original data is not modified directly
    return list(_watchlists.get(user_id, []))  # Kevin Ngo, 5/2/26 - returns empty list if user has no watchlist


def add_to_watchlist(symbol, user_id="default"):
    # Kevin Ngo, 5/2/26 - adds a stock symbol to the user's watchlist if it is not already included

    if user_id not in _watchlists:
        _watchlists[user_id] = []  # Kevin Ngo, 5/2/26 - initialize a new watchlist for the user if none exists

    if symbol not in _watchlists[user_id]:
        _watchlists[user_id].append(symbol)  # Kevin Ngo, 5/2/26 - append symbol to list to track user's selected stocks


def remove_from_watchlist(symbol, user_id="default"):
    # Kevin Ngo, 5/2/26 - removes a stock symbol from the user's watchlist if it exists

    if user_id in _watchlists:
        # Kevin Ngo, 5/2/26 - rebuilds list excluding the symbol to safely remove it
        _watchlists[user_id] = [s for s in _watchlists[user_id] if s != symbol]
