import logging
from strategies.momentum import calculate_momentum
from strategies.mean_reversion import calculate_mean_reversion
from strategies.monte_carlo import calculate_monte_carlo
from strategies.factor_model import calculate_factor_model


logger = logging.getLogger(__name__)

# Strategy weights for ensemble voting
WEIGHTS = {
    "momentum": 0.30,
    "mean_reversion": 0.25,
    "monte_carlo": 0.25,
    "factor_model": 0.20,
}


def get_aggregated_signal(symbol):
    """
    Weighted ensemble combining all strategies into BUY/SELL/HOLD with confidence %.

    - Runs all 4 strategies independently
    - Combines scores using predefined weights
    - Redistributes weight if a strategy returns None (missing data)
    - Confidence: 30-100% based on score magnitude and strategy agreement

    Returns:
        {
            "symbol": "AAPL",
            "signal": "BUY" | "SELL" | "HOLD",
            "confidence": 0-100,
            "breakdown": { ... }
        }
    """
    symbol = symbol.upper()

    # Run all strategies and track execution
    strategy_runners = {
        "momentum": calculate_momentum,
        "mean_reversion": calculate_mean_reversion,
        "monte_carlo": calculate_monte_carlo,
        "factor_model": calculate_factor_model,
    }

    results = {}
    for name, runner in strategy_runners.items():
        try:
            results[name] = runner(symbol)
            logger.info(f"Strategy {name} completed for {symbol}")
        except Exception as e:
            logger.warning(f"Strategy {name} failed for {symbol}: {e}")
            results[name] = None

    # Calculate weighted score from available strategies
    weighted_sum = 0
    total_weight = 0
    breakdown = {}
    active_strategies = 0

    for strategy_name, result in results.items():
        if result is not None:
            weight = WEIGHTS[strategy_name]
            weighted_sum += result["score"] * weight
            total_weight += weight
            breakdown[strategy_name] = result
            active_strategies += 1
        else:
            breakdown[strategy_name] = {
                "score": 0,
                "signal": "N/A",
                "details": "Insufficient data",
            }

    if total_weight == 0:
        return None

    # Normalize score (redistributes weight from missing strategies)
    final_score = weighted_sum / total_weight

    # Determine signal
    if final_score > 0.15:
        signal = "BUY"
    elif final_score < -0.15:
        signal = "SELL"
    else:
        signal = "HOLD"

    # Confidence calculation:
    # Base confidence from score magnitude
    base_confidence = abs(final_score) * 100 + 40

    # Agreement bonus: magnitude-weighted — a strategy with score 0.9 agreeing
    # carries more weight than one with score 0.05 agreeing.
    if active_strategies >= 2:
        total_magnitude = sum(
            abs(r["score"]) for r in results.values() if r is not None
        )
        if total_magnitude > 0:
            aligned_magnitude = sum(
                abs(r["score"]) for r in results.values()
                if r is not None and (
                    (r["score"] > 0 and final_score > 0) or
                    (r["score"] < 0 and final_score < 0)
                )
            )
            agreement_ratio = aligned_magnitude / total_magnitude
        else:
            agreement_ratio = 0
        # Up to 10% bonus for full magnitude-weighted agreement
        agreement_bonus = agreement_ratio * 10
    else:
        agreement_bonus = 0

    # Coverage penalty: fewer strategies = less confidence
    coverage_ratio = active_strategies / len(WEIGHTS)
    coverage_penalty = (1 - coverage_ratio) * 15

    confidence = min(int(base_confidence + agreement_bonus - coverage_penalty), 100)
    confidence = max(confidence, 30)

    return {
        "symbol": symbol,
        "signal": signal,
        "confidence": confidence,
        "breakdown": breakdown,
    }
