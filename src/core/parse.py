import json
from datetime import datetime, timezone
from typing import Any, Optional

from .models import MarketRecord


def safe_parse_json_or_list(value: Any) -> Optional[list]:
    if value is None:
        return None
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass
    return None


def parse_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def calculate_hours_to_close(end_date_str: Optional[str]) -> Optional[float]:
    if not end_date_str:
        return None
    try:
        end_date_str = end_date_str.replace("Z", "+00:00")
        end_date = datetime.fromisoformat(end_date_str)
        if end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        delta = end_date - now
        return round(delta.total_seconds() / 3600, 2)
    except (ValueError, TypeError):
        return None


def parse_market_data(raw: dict) -> MarketRecord:
    market_id = raw.get("id", "")

    outcomes = safe_parse_json_or_list(raw.get("outcomes"))
    outcome_prices = safe_parse_json_or_list(raw.get("outcomePrices"))
    clob_token_ids = safe_parse_json_or_list(raw.get("clobTokenIds"))

    invalid_reason = None
    price_note = None
    yes_token_id = None
    no_token_id = None
    yes_price = None
    no_price = None

    if outcomes is None:
        invalid_reason = "outcomes field missing or unparseable"
    elif len(outcomes) != 2:
        invalid_reason = f"not binary market (outcomes={len(outcomes)})"
    else:
        yes_idx = None
        no_idx = None

        for i, outcome in enumerate(outcomes):
            outcome_lower = str(outcome).lower()
            if outcome_lower == "yes":
                yes_idx = i
            elif outcome_lower == "no":
                no_idx = i

        if yes_idx is None or no_idx is None:
            invalid_reason = f"cannot identify YES/NO in outcomes: {outcomes}"
        else:
            if clob_token_ids and len(clob_token_ids) == 2:
                yes_token_id = str(clob_token_ids[yes_idx])
                no_token_id = str(clob_token_ids[no_idx])
            else:
                invalid_reason = "clobTokenIds missing or not length 2"

            if outcome_prices and len(outcome_prices) >= 2:
                yes_price = parse_float(outcome_prices[yes_idx])
                no_price = parse_float(outcome_prices[no_idx])
                if yes_price is None or no_price is None:
                    price_note = "outcomePrices contains unparseable values"
            else:
                price_note = "outcomePrices missing or insufficient length"

    end_date = raw.get("endDate")

    return MarketRecord(
        id=market_id,
        slug=raw.get("slug"),
        question=raw.get("question"),
        category=raw.get("category"),
        endDate=end_date,
        hours_to_close=calculate_hours_to_close(end_date),
        enableOrderBook=bool(raw.get("enableOrderBook", False)),
        active=bool(raw.get("active", False)),
        closed=bool(raw.get("closed", False)),
        yes_token_id=yes_token_id,
        no_token_id=no_token_id,
        yes_price=yes_price,
        no_price=no_price,
        invalid_reason=invalid_reason,
        price_note=price_note,
    )
