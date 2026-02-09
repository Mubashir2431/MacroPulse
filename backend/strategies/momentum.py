import numpy as np
from services.data_fetcher import get_historical_dataframe


def calculate_momentum(symbol):
    """
    Dual Momentum Strategy:
    - Absolute momentum: 12-month return > 0 → bullish
    - Relative momentum: Compare ROC vs SPY benchmark
    - Score from -1 (strong sell) to +1 (strong buy)
    """
    try:
        df = get_historical_dataframe(symbol, period="1y")
        if df is None or len(df) < 60:
            return None

        closes = df["Close"].values

        # Absolute momentum: total return over available period
        total_return = (closes[-1] - closes[0]) / closes[0]

        # Rate of Change (ROC) - multiple timeframes
        roc_20 = (closes[-1] - closes[-20]) / closes[-20] if len(closes) >= 20 else 0
        roc_60 = (closes[-1] - closes[-60]) / closes[-60] if len(closes) >= 60 else 0

        # Relative momentum vs SPY benchmark
        spy_df = get_historical_dataframe("SPY", period="1y")
        relative_score = 0
        if spy_df is not None and len(spy_df) >= 60:
            spy_closes = spy_df["Close"].values
            spy_return = (spy_closes[-1] - spy_closes[0]) / spy_closes[0]
            relative_score = total_return - spy_return

        # Combine signals
        # Absolute: positive return = bullish
        abs_signal = np.clip(total_return * 2, -1, 1)

        # ROC combined (short + medium term)
        roc_signal = np.clip((roc_20 * 3 + roc_60 * 2) / 2, -1, 1)

        # Relative: outperforming benchmark = bullish
        rel_signal = np.clip(relative_score * 3, -1, 1)

        # Weighted combination
        score = 0.4 * abs_signal + 0.3 * roc_signal + 0.3 * rel_signal
        score = float(np.clip(score, -1, 1))

        if score > 0.2:
            signal = "BUY"
        elif score < -0.2:
            signal = "SELL"
        else:
            signal = "HOLD"

        # Build detail string
        details = f"12m return {total_return * 100:+.1f}%"
        if spy_df is not None:
            spy_return_val = (spy_df["Close"].values[-1] - spy_df["Close"].values[0]) / spy_df["Close"].values[0]
            comparison = "above" if total_return > spy_return_val else "below"
            details += f", {comparison} SPY ({spy_return_val * 100:+.1f}%)"

        return {
            "score": round(score, 2),
            "signal": signal,
            "details": details,
        }
    except Exception as e:
        return None
