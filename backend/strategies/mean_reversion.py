import logging
import numpy as np
from services.data_fetcher import get_historical_dataframe

logger = logging.getLogger(__name__)


def _calculate_rsi(closes, period=14):
    """Calculate RSI using Wilder's smoothing method. Returns RSI value or None."""
    if len(closes) < period + 1:
        return None
    deltas = np.diff(closes[-(period + 1):])
    gains = np.where(deltas > 0, deltas, 0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)
    avg_gain = np.mean(gains)
    avg_loss = np.mean(losses)
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def calculate_mean_reversion(symbol):
    """
    Z-Score Mean Reversion Strategy:
    - Z-score of current price vs 50-day mean / 20-day std
    - Bollinger Band position (%B indicator)
    - RSI (14-period): RSI < 30 → oversold, RSI > 70 → overbought
    - Z < -2 → oversold (buy), Z > 2 → overbought (sell)
    - Score from -1 (strong sell) to +1 (strong buy)
    """
    try:
        df = get_historical_dataframe(symbol, period="6mo")
        if df is None or len(df) < 30:
            return None

        closes = df["Close"].values

        # Use a 50-day lookback for the mean so a recent crash/spike is
        # measured against a longer baseline (more sensitive to reversions).
        # Keep the 20-day window for std to reflect recent volatility.
        window   = 20
        lookback = min(50, len(closes))
        rolling_mean = np.mean(closes[-lookback:])
        rolling_std  = np.std(closes[-window:], ddof=1)

        if rolling_std == 0:
            return {"score": 0.0, "signal": "HOLD",
                    "details": "Insufficient price variation"}

        current_price = closes[-1]

        # Z-score
        z_score = (current_price - rolling_mean) / rolling_std

        # Bollinger Bands
        upper_band = rolling_mean + 2 * rolling_std
        lower_band = rolling_mean - 2 * rolling_std
        band_width = upper_band - lower_band

        # %B indicator: position within Bollinger Bands (0 = lower, 1 = upper)
        pct_b = (current_price - lower_band) / band_width if band_width > 0 else 0.5

        # RSI signal (inverted: low RSI = oversold = buy)
        # RSI 30 → +1 (strong buy), RSI 50 → 0, RSI 70 → -1 (strong sell)
        rsi = _calculate_rsi(closes)
        rsi_signal = float(np.clip((50.0 - rsi) / 20.0, -1, 1)) if rsi is not None else None

        # Mean reversion signal (inverted: oversold = buy opportunity)
        # Z < -2: strong buy, Z > 2: strong sell
        z_signal = float(np.clip(-z_score / 2.5, -1, 1))

        # %B signal (inverted: near lower band = buy)
        b_signal = float(np.clip((0.5 - pct_b) * 2, -1, 1))

        # Combined score — include RSI if available, else fall back to original weights
        if rsi_signal is not None:
            score = 0.50 * z_signal + 0.30 * b_signal + 0.20 * rsi_signal
        else:
            score = 0.60 * z_signal + 0.40 * b_signal
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

        rsi_str = f", RSI: {rsi:.1f}" if rsi is not None else ""
        details = f"Z-score: {z_score:.2f}, {zone}, %B: {pct_b:.2f}{rsi_str}"

        return {
            "score": round(score, 2),
            "signal": signal,
            "details": details,
        }
    except Exception:
        logger.exception("Error calculating mean reversion for %s", symbol)
        return None
