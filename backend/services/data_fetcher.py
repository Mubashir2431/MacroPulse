import os
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Simple TTL cache: { key: (timestamp, data) }
_cache = {}
# Person 3 - US7/US9: TTL and timeout configurable via environment variables
_DEFAULT_TTL = int(os.environ.get("CACHE_TTL", 300))
_REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", 10))

# Flag: set to True when yfinance is working
_yfinance_available = None


def _cache_get(key, ttl=_DEFAULT_TTL):
    if key in _cache:
        ts, data = _cache[key]
        if time.time() - ts < ttl:
            return data
        del _cache[key]
    return None


def _cache_set(key, data):
    _cache[key] = (time.time(), data)


def _check_yfinance():
    """Check if yfinance can actually reach Yahoo Finance."""
    global _yfinance_available
    if _yfinance_available is not None:
        return _yfinance_available

    try:
        import yfinance as yf
        ticker = yf.Ticker("AAPL")
        hist = ticker.history(period="5d", timeout=_REQUEST_TIMEOUT)
        _yfinance_available = not hist.empty
    except Exception:
        _yfinance_available = False

    return _yfinance_available


# ========== MOCK DATA (fallback when Yahoo Finance is unavailable) ==========

_MOCK_STOCKS = {
    "AAPL": {"name": "Apple Inc.", "price": 189.50, "prev_close": 187.20, "volume": 54000000, "market_cap": 2.95e12, "high52w": 199.62, "low52w": 143.90, "pe": 28.5, "fwd_pe": 26.1, "roe": 0.175, "margin": 0.26, "sector": "Technology", "industry": "Consumer Electronics"},
    "MSFT": {"name": "Microsoft Corp.", "price": 415.30, "prev_close": 411.80, "volume": 22000000, "market_cap": 3.08e12, "high52w": 430.82, "low52w": 309.45, "pe": 35.2, "fwd_pe": 31.8, "roe": 0.39, "margin": 0.36, "sector": "Technology", "industry": "Software"},
    "GOOGL": {"name": "Alphabet Inc.", "price": 153.80, "prev_close": 152.10, "volume": 28000000, "market_cap": 1.92e12, "high52w": 160.95, "low52w": 120.21, "pe": 24.6, "fwd_pe": 21.3, "roe": 0.28, "margin": 0.24, "sector": "Technology", "industry": "Internet Content"},
    "AMZN": {"name": "Amazon.com Inc.", "price": 198.20, "prev_close": 195.90, "volume": 45000000, "market_cap": 2.04e12, "high52w": 201.20, "low52w": 151.61, "pe": 58.3, "fwd_pe": 38.5, "roe": 0.22, "margin": 0.08, "sector": "Consumer Cyclical", "industry": "Internet Retail"},
    "NVDA": {"name": "NVIDIA Corp.", "price": 870.50, "prev_close": 855.10, "volume": 42000000, "market_cap": 2.14e12, "high52w": 974.00, "low52w": 473.20, "pe": 64.8, "fwd_pe": 35.2, "roe": 0.91, "margin": 0.55, "sector": "Technology", "industry": "Semiconductors"},
    "TSLA": {"name": "Tesla Inc.", "price": 235.60, "prev_close": 240.80, "volume": 95000000, "market_cap": 748e9, "high52w": 299.29, "low52w": 152.37, "pe": 62.1, "fwd_pe": 55.0, "roe": 0.22, "margin": 0.11, "sector": "Consumer Cyclical", "industry": "Auto Manufacturers"},
    "META": {"name": "Meta Platforms Inc.", "price": 524.80, "prev_close": 520.10, "volume": 18000000, "market_cap": 1.35e12, "high52w": 542.81, "low52w": 350.32, "pe": 26.8, "fwd_pe": 22.1, "roe": 0.33, "margin": 0.29, "sector": "Technology", "industry": "Internet Content"},
    "JPM": {"name": "JPMorgan Chase & Co.", "price": 198.40, "prev_close": 196.80, "volume": 9000000, "market_cap": 571e9, "high52w": 205.88, "low52w": 162.43, "pe": 11.8, "fwd_pe": 12.5, "roe": 0.15, "margin": 0.34, "sector": "Financial Services", "industry": "Banks"},
    "V": {"name": "Visa Inc.", "price": 287.50, "prev_close": 285.30, "volume": 7000000, "market_cap": 587e9, "high52w": 293.07, "low52w": 252.70, "pe": 31.2, "fwd_pe": 27.1, "roe": 0.47, "margin": 0.54, "sector": "Financial Services", "industry": "Credit Services"},
    "JNJ": {"name": "Johnson & Johnson", "price": 156.80, "prev_close": 157.50, "volume": 6500000, "market_cap": 378e9, "high52w": 168.85, "low52w": 143.13, "pe": 20.5, "fwd_pe": 14.8, "roe": 0.21, "margin": 0.20, "sector": "Healthcare", "industry": "Drug Manufacturers"},
    "WMT": {"name": "Walmart Inc.", "price": 172.30, "prev_close": 171.10, "volume": 8000000, "market_cap": 463e9, "high52w": 175.90, "low52w": 149.20, "pe": 28.1, "fwd_pe": 25.3, "roe": 0.19, "margin": 0.025, "sector": "Consumer Defensive", "industry": "Discount Stores"},
    "DIS": {"name": "Walt Disney Co.", "price": 98.50, "prev_close": 97.80, "volume": 11000000, "market_cap": 180e9, "high52w": 123.74, "low52w": 83.91, "pe": 42.3, "fwd_pe": 19.8, "roe": 0.04, "margin": 0.06, "sector": "Communication Services", "industry": "Entertainment"},
    "SPY": {"name": "SPDR S&P 500 ETF", "price": 500.20, "prev_close": 497.80, "volume": 70000000, "market_cap": 500e9, "high52w": 510.13, "low52w": 410.34, "pe": 22.0, "fwd_pe": 20.0, "roe": None, "margin": None, "sector": "N/A", "industry": "ETF"},
}


def _generate_mock_history(mock, period="1y"):
    """Generate realistic-looking price history from mock base data."""
    period_days = {"1mo": 22, "3mo": 63, "6mo": 126, "1y": 252, "2y": 504, "5y": 1260}
    days = period_days.get(period, 252)

    np.random.seed(hash(mock["name"]) % 2**31)
    base_price = mock["price"]
    # Walk backwards from current price with random daily returns
    daily_vol = 0.015  # ~1.5% daily vol
    returns = np.random.normal(0.0003, daily_vol, days)  # slight upward drift
    prices = np.zeros(days)
    prices[-1] = base_price
    for i in range(days - 2, -1, -1):
        prices[i] = prices[i + 1] / (1 + returns[i + 1])

    records = []
    start_date = datetime.now() - timedelta(days=days * 1.4)  # account for weekends
    trading_day = 0
    current = start_date
    while trading_day < days:
        if current.weekday() < 5:  # skip weekends
            p = prices[trading_day]
            daily_range = p * daily_vol
            records.append({
                "date": current.strftime("%Y-%m-%d"),
                "open": round(p - daily_range * 0.3, 2),
                "high": round(p + daily_range * 0.5, 2),
                "low": round(p - daily_range * 0.5, 2),
                "close": round(p, 2),
                "volume": int(mock["volume"] * (0.7 + np.random.random() * 0.6)),
            })
            trading_day += 1
        current += timedelta(days=1)

    return records


def _mock_history_as_df(mock, period="1y"):
    """Convert mock history to DataFrame for strategies."""
    records = _generate_mock_history(mock, period)
    df = pd.DataFrame(records)
    df["Date"] = pd.to_datetime(df["date"])
    df = df.set_index("Date")
    df = df.rename(columns={"open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume"})
    df = df.drop(columns=["date"])
    return df


# ========== PUBLIC API ==========

def _format_market_cap(market_cap):
    if not market_cap or market_cap == 0:
        return "N/A"
    if market_cap >= 1e12:
        return f"{market_cap / 1e12:.2f}T"
    elif market_cap >= 1e9:
        return f"{market_cap / 1e9:.2f}B"
    elif market_cap >= 1e6:
        return f"{market_cap / 1e6:.2f}M"
    return str(int(market_cap))


def search_stocks(query):
    """Search for stocks matching a query string."""
    cache_key = f"search:{query.upper()}"
    cached = _cache_get(cache_key, ttl=600)
    if cached is not None:
        return cached

    results = []

    # Try yfinance first
    if _check_yfinance():
        try:
            import yfinance as yf
            search_result = yf.Search(query, max_results=8)
            if hasattr(search_result, "quotes") and search_result.quotes:
                for quote in search_result.quotes:
                    sym = quote.get("symbol", "")
                    if sym:
                        results.append({
                            "symbol": sym,
                            "name": quote.get("shortname") or quote.get("longname", sym),
                            "exchange": quote.get("exchange", "N/A"),
                        })
        except Exception:
            pass

    # Fallback to mock data search
    if not results:
        query_upper = query.upper().strip()
        query_lower = query.lower().strip()
        for sym, data in _MOCK_STOCKS.items():
            if sym == "SPY":
                continue  # don't show SPY in search
            if query_upper in sym or query_lower in data["name"].lower():
                results.append({
                    "symbol": sym,
                    "name": data["name"],
                    "exchange": "NASDAQ" if data["sector"] == "Technology" else "NYSE",
                })

    _cache_set(cache_key, results)
    return results


def get_stock_info(symbol):
    """Get current stock info for a symbol."""
    cache_key = f"info:{symbol.upper()}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    symbol_upper = symbol.upper()

    # Try yfinance first
    if _check_yfinance():
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol_upper)
            fi = ticker.fast_info
            if hasattr(fi, "last_price") and fi.last_price is not None:
                price = fi.last_price
                prev_close = getattr(fi, "previous_close", 0) or 0
                change = round(price - prev_close, 2) if prev_close else 0
                change_pct = round((change / prev_close) * 100, 2) if prev_close else 0

                data = {
                    "symbol": symbol_upper,
                    "name": symbol_upper,
                    "price": round(price, 2),
                    "change": change,
                    "changePercent": change_pct,
                    "volume": int(getattr(fi, "last_volume", 0) or 0),
                    "marketCap": _format_market_cap(getattr(fi, "market_cap", 0)),
                    "high52w": round(getattr(fi, "year_high", 0) or 0, 2),
                    "low52w": round(getattr(fi, "year_low", 0) or 0, 2),
                    "pe_ratio": None, "forward_pe": None,
                    "roe": None, "profit_margin": None,
                    "sector": "N/A", "industry": "N/A",
                }
                try:
                    info = ticker.info
                    if info:
                        data["name"] = info.get("shortName") or info.get("longName", symbol_upper)
                        data["pe_ratio"] = info.get("trailingPE")
                        data["forward_pe"] = info.get("forwardPE")
                        data["roe"] = info.get("returnOnEquity")
                        data["profit_margin"] = info.get("profitMargins")
                        data["sector"] = info.get("sector", "N/A")
                        data["industry"] = info.get("industry", "N/A")
                except Exception:
                    pass
                _cache_set(cache_key, data)
                return data
        except Exception:
            pass

    # Fallback to mock data
    mock = _MOCK_STOCKS.get(symbol_upper)
    if not mock:
        return None

    price = mock["price"]
    prev_close = mock["prev_close"]
    change = round(price - prev_close, 2)
    change_pct = round((change / prev_close) * 100, 2) if prev_close else 0

    data = {
        "symbol": symbol_upper,
        "name": mock["name"],
        "price": price,
        "change": change,
        "changePercent": change_pct,
        "volume": mock["volume"],
        "marketCap": _format_market_cap(mock["market_cap"]),
        "high52w": mock["high52w"],
        "low52w": mock["low52w"],
        "pe_ratio": mock["pe"],
        "forward_pe": mock["fwd_pe"],
        "roe": mock["roe"],
        "profit_margin": mock["margin"],
        "sector": mock["sector"],
        "industry": mock["industry"],
    }

    _cache_set(cache_key, data)
    return data


def get_stock_history(symbol, period="1y"):
    """Get historical OHLCV data for a symbol."""
    cache_key = f"history:{symbol.upper()}:{period}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    symbol_upper = symbol.upper()

    # Try yfinance first
    if _check_yfinance():
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol_upper)
            # Person 3 - US9: Apply request timeout to external API call
            hist = ticker.history(period=period, timeout=_REQUEST_TIMEOUT)
            if not hist.empty:
                records = []
                for date, row in hist.iterrows():
                    records.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "open": round(row["Open"], 2),
                        "high": round(row["High"], 2),
                        "low": round(row["Low"], 2),
                        "close": round(row["Close"], 2),
                        "volume": int(row["Volume"]),
                    })
                data = {"symbol": symbol_upper, "history": records}
                _cache_set(cache_key, data)
                return data
        except Exception:
            pass

    # Fallback to mock data
    mock = _MOCK_STOCKS.get(symbol_upper)
    if not mock:
        return None

    records = _generate_mock_history(mock, period)
    data = {"symbol": symbol_upper, "history": records}
    _cache_set(cache_key, data)
    return data


def get_historical_dataframe(symbol, period="1y"):
    """Get historical data as a pandas DataFrame (for strategies)."""
    cache_key = f"df:{symbol.upper()}:{period}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    symbol_upper = symbol.upper()

    # Try yfinance first
    if _check_yfinance():
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol_upper)
            # Person 3 - US9: Apply request timeout to external API call
            df = ticker.history(period=period, timeout=_REQUEST_TIMEOUT)
            if not df.empty:
                _cache_set(cache_key, df)
                return df
        except Exception:
            pass

    # Fallback to mock data
    mock = _MOCK_STOCKS.get(symbol_upper)
    if not mock:
        return None

    df = _mock_history_as_df(mock, period)
    _cache_set(cache_key, df)
    return df


def get_ticker_info_raw(symbol):
    """Get raw ticker info dict (for factor model)."""
    cache_key = f"raw_info:{symbol.upper()}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    symbol_upper = symbol.upper()

    # Try yfinance first
    if _check_yfinance():
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol_upper)
            info = ticker.info
            if info and (info.get("symbol") or info.get("shortName")):
                _cache_set(cache_key, info)
                return info
        except Exception:
            pass

    # Fallback to mock data
    mock = _MOCK_STOCKS.get(symbol_upper)
    if not mock:
        return None

    fallback = {
        "symbol": symbol_upper,
        "shortName": mock["name"],
        "currentPrice": mock["price"],
        "trailingPE": mock["pe"],
        "forwardPE": mock["fwd_pe"],
        "returnOnEquity": mock["roe"],
        "profitMargins": mock["margin"],
        "marketCap": mock["market_cap"],
        "sector": mock["sector"],
    }
    _cache_set(cache_key, fallback)
    return fallback
