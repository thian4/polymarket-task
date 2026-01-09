from typing import List
from .models import MarketRecord

# Configurable time window (hours)
MAX_HOURS_TO_CLOSE = 48


def filter_candidates(markets: List[MarketRecord], max_hours: int = MAX_HOURS_TO_CLOSE) -> List[MarketRecord]:
    """
    Filter criteria:
    1. enableOrderBook == True
    2. active == True and closed == False
    3. 0 < hours_to_close <= max_hours
    4. Valid YES/NO token IDs
    """
    candidates = []

    for market in markets:
        if not market.enableOrderBook:
            continue
        if not market.active or market.closed:
            continue
        if market.hours_to_close is None:
            continue
        if market.hours_to_close <= 0 or market.hours_to_close > max_hours:
            continue
        if not market.yes_token_id or not market.no_token_id:
            continue
        if market.invalid_reason:
            continue

        candidates.append(market)

    candidates.sort(key=lambda m: m.hours_to_close or float("inf"))
    return candidates
