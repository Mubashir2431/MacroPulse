import numpy as np
from services.data_fetcher import get_historical_dataframe


def calculate_mean_reversion(symbol):
    """
    Z-Score Mean Reversion Strategy:
    - Z-score of current price vs 20-day rolling mean
    - Bollinger Band position (%B indicator)
    - Z < -2 → oversold (buy), Z > 2 → overbought (sell)
    - Score from -1 (strong sell) to +1 (strong buy)
    """
    try:
        df = get_historical_dataframe(symbol, period="6mo")
        if df is None or len(df) < 30:
            return None

        closes = df["Close"].values

        # 20-day rolling statistics
        window = 20
        rolling_mean = np.mean(closes[-window:])
        rolling_std = np.std(closes[-window:], ddof=1)

        if rolling_std == 0:
            return None

        current_price = closes[-1]

        # Z-score
        z_score = (current_price - rolling_mean) / rolling_std

        # Bollinger Bands
        upper_band = rolling_mean + 2 * rolling_std
        lower_band = rolling_mean - 2 * rolling_std
        band_width = upper_band - lower_band

        # %B indicator: position within Bollinger Bands (0 = lower, 1 = upper)
        pct_b = (current_price - lower_band) / band_width if band_width > 0 else 0.5

        # Mean reversion signal (inverted: oversold = buy opportunity)
        # Z < -2: strong buy, Z > 2: strong sell
        z_signal = float(np.clip(-z_score / 2.5, -1, 1))

        # %B signal (inverted: near lower band = buy)
        b_signal = float(np.clip((0.5 - pct_b) * 2, -1, 1))

        # Combined score
        score = 0.6 * z_signal + 0.4 * b_signal
        score = float(np.clip(score, -1, 1))

        if score > 0.2:
            signal = "BUY"
        elif score < -0.2:
            signal = "SELL"
        else:
            signal = "HOLD"

        # Zone description
        if z_score < -2:
            zone = "oversold"
        elif z_score > 2:
            zone = "overbought"
        elif abs(z_score) < 0.5:
            zone = "neutral zone"
        elif z_score > 0:
            zone = "slightly overbought"
        else:
            zone = "slightly oversold"

        details = f"Z-score: {z_score:.2f}, {zone}, %B: {pct_b:.2f}"

        return {
            "score": round(score, 2),
            "signal": signal,
            "details": details,
        }
    except Exception:
        return None
