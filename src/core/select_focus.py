import re
from typing import List, Optional, Tuple
from .models import MarketRecord


# Use word boundary patterns for short keywords to avoid false positives
CRYPTO_PATTERNS = [
    r"\bcrypto\b", r"\bbitcoin\b", r"\bbtc\b", r"\bethereum\b", r"\beth\b",
    r"\bsolana\b", r"\bsol\b", r"\bblockchain\b", r"\bdefi\b", r"\bnft\b",
    r"\btoken\b", r"\bcoin\b", r"\baltcoin\b"
]

SPORTS_PATTERNS = [
    r"\bsports\b", r"\bnfl\b", r"\bnba\b", r"\bmlb\b", r"\bnhl\b",
    r"\bsoccer\b", r"\bfootball\b", r"\bbasketball\b", r"\bbaseball\b",
    r"\bhockey\b", r"\btennis\b", r"\bgolf\b", r"\bufc\b", r"\bboxing\b",
    r"\bmma\b", r"\bolympics\b", r"world cup", r"premier league",
    r"\bfc\b", r"\bwin on\b", r"\bend in a draw\b", r"\bvs\.\b"
]


def _get_searchable_text(market: MarketRecord) -> str:
    parts = []
    if market.category:
        parts.append(market.category)
    if market.question:
        parts.append(market.question)
    return " ".join(parts).lower()


def is_crypto_market(market: MarketRecord) -> bool:
    text = _get_searchable_text(market)
    return any(re.search(p, text) for p in CRYPTO_PATTERNS)


def is_sports_market(market: MarketRecord) -> bool:
    text = _get_searchable_text(market)
    return any(re.search(p, text) for p in SPORTS_PATTERNS)


def select_focus_markets(
    candidates: List[MarketRecord],
) -> Tuple[Optional[MarketRecord], Optional[MarketRecord]]:
    crypto_market = None
    sports_market = None

    for market in candidates:
        if crypto_market is None and is_crypto_market(market):
            crypto_market = market
        if sports_market is None and is_sports_market(market):
            sports_market = market
        if crypto_market and sports_market:
            break

    return crypto_market, sports_market
