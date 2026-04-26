import logging
import numpy as np
from services.data_fetcher import get_historical_dataframe

logger = logging.getLogger(__name__)


def calculate_monte_carlo(symbol, num_simulations=1000, forecast_days=30, seed=None):
    """
    Monte Carlo Price Simulation using Geometric Brownian Motion (GBM):
    - 1000 vectorized simulated price paths for performance
    - Uses historical volatility and drift from past 252 trading days
    - Calculates Value at Risk (VaR) and expected shortfall (CVaR)
    - Output: probability of price being higher in 30 days, expected range
    - Score from -1 (strong sell) to +1 (strong buy)
    """
    try:
        df = get_historical_dataframe(symbol, period="1y")
        if df is None or len(df) < 60:
            return None

        closes = df["Close"].values

        # Calculate log returns for GBM (more accurate than simple returns)
        log_returns = np.diff(np.log(closes))

        # Historical parameters from log returns
        mu = np.mean(log_returns)  # daily drift
        sigma = np.std(log_returns, ddof=1)  # daily volatility

        current_price = closes[-1]

        # Vectorized GBM simulation (much faster than nested loops)
        # Mubashir - US12: Removed fixed seed so each request produces varied
        # results reflecting real uncertainty. Pass seed= for reproducible testing.
        if seed is not None:
            np.random.seed(seed)
        dt = 1  # 1 trading day

        # Generate all random shocks at once: (simulations x days)
        random_shocks = np.random.normal(size=(num_simulations, forecast_days))

        # GBM formula: S(t+dt) = S(t) * exp((mu - 0.5*sigma^2)*dt + sigma*sqrt(dt)*Z)
        drift = (mu - 0.5 * sigma**2) * dt
        diffusion = sigma * np.sqrt(dt) * random_shocks

        # Cumulative sum of log returns gives the full path
        cumulative_log_returns = np.cumsum(drift + diffusion, axis=1)
        simulated_prices = current_price * np.exp(cumulative_log_returns)

        # Final simulated prices (at forecast_days)
        final_prices = simulated_prices[:, -1]

        # Probability of price being higher
        prob_higher = np.mean(final_prices > current_price)

        # Expected range (5th to 95th percentile)
        p5 = np.percentile(final_prices, 5)
        p25 = np.percentile(final_prices, 25)
        p50 = np.percentile(final_prices, 50)
        p75 = np.percentile(final_prices, 75)
        p95 = np.percentile(final_prices, 95)

        # Expected return
        expected_return = (p50 - current_price) / current_price

        # Value at Risk (VaR) - 95% confidence
        # Maximum expected loss at 5th percentile
        var_95 = (current_price - p5) / current_price

        # Conditional VaR (Expected Shortfall) - average loss beyond VaR
        worst_5pct = final_prices[final_prices <= p5]
        cvar_95 = (current_price - np.mean(worst_5pct)) / current_price if len(worst_5pct) > 0 else var_95

        # Risk-adjusted score: combine probability with risk metrics
        # Base score from probability of price increase
        prob_score = (prob_higher - 0.5) * 4  # maps 0.5 → 0, 0.75 → 1, 0.25 → -1

        # Blend VaR and CVaR for the risk penalty — CVaR (Expected Shortfall)
        # captures tail risk beyond VaR and is a more conservative measure.
        combined_risk = 0.4 * var_95 + 0.6 * cvar_95
        risk_penalty = max(0, combined_risk - 0.10) * 2  # kicks in above 10%
        adjusted_score = prob_score - np.sign(prob_score) * risk_penalty

        score = float(np.clip(adjusted_score, -1, 1))

        if score > 0.2:
            signal = "BUY"
        elif score < -0.2:
            signal = "SELL"
        else:
            signal = "HOLD"

        details = (
            f"{prob_higher * 100:.0f}% prob higher in {forecast_days}d, "
            f"range ${p5:.2f}-${p95:.2f}, "
            f"VaR {var_95 * 100:.1f}%, CVaR {cvar_95 * 100:.1f}%"
        )

        return {
            "score": round(score, 2),
            "signal": signal,
            "details": details,
        }
    except Exception:
        logger.exception("Error calculating Monte Carlo for %s", symbol)
        return None
