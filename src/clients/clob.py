from typing import Dict, List, Optional
import requests


CLOB_API_BASE = "https://clob.polymarket.com"


class ClobClient:
    def __init__(self, base_url: str = CLOB_API_BASE):
        self.base_url = base_url
        self.session = requests.Session()

    def get_prices(self, token_ids: List[str]) -> Dict[str, dict]:
        if not token_ids:
            return {}
        url = f"{self.base_url}/prices"
        try:
            response = self.session.get(
                url,
                params={"token_ids": ",".join(token_ids)},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return {}

    def get_book(self, token_id: str) -> Optional[dict]:
        url = f"{self.base_url}/book"
        try:
            response = self.session.get(
                url,
                params={"token_id": token_id},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None
