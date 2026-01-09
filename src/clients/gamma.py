from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional
import requests

from ..core.models import MarketRecord
from ..core.parse import parse_market_data


GAMMA_API_BASE = "https://gamma-api.polymarket.com"
DEFAULT_LIMIT = 100
MAX_MARKETS = 10000  # Fetch all active markets
CONCURRENT_REQUESTS = 20  # Fetch 20 pages at once


class GammaClient:
    def __init__(self, base_url: str = GAMMA_API_BASE):
        self.base_url = base_url
        self.session = requests.Session()

    def fetch_markets_page(
        self,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
        active: Optional[bool] = None,
        closed: Optional[bool] = None,
    ) -> List[dict]:
        url = f"{self.base_url}/markets"
        params = {"limit": limit, "offset": offset}
        if active is not None:
            params["active"] = str(active).lower()
        if closed is not None:
            params["closed"] = str(closed).lower()

        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    def fetch_all_markets(
        self,
        limit: int = DEFAULT_LIMIT,
        active: Optional[bool] = None,
        closed: Optional[bool] = None,
        max_markets: int = MAX_MARKETS,
    ) -> List[MarketRecord]:
        all_markets: List[MarketRecord] = []
        offsets = list(range(0, max_markets, limit))

        with ThreadPoolExecutor(max_workers=CONCURRENT_REQUESTS) as executor:
            futures = {
                executor.submit(
                    self.fetch_markets_page, limit, offset, active, closed
                ): offset
                for offset in offsets
            }

            for future in as_completed(futures):
                try:
                    raw_markets = future.result()
                    if not raw_markets:
                        continue
                    for raw in raw_markets:
                        all_markets.append(parse_market_data(raw))
                except Exception:
                    continue

        # Sort by id to maintain consistent order
        all_markets.sort(key=lambda m: m.id)
        return all_markets[:max_markets]
