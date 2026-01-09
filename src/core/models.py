from dataclasses import dataclass
from typing import Optional


@dataclass
class MarketRecord:
    id: str
    slug: Optional[str] = None
    question: Optional[str] = None
    category: Optional[str] = None
    endDate: Optional[str] = None
    hours_to_close: Optional[float] = None
    enableOrderBook: bool = False
    active: bool = False
    closed: bool = False
    yes_token_id: Optional[str] = None
    no_token_id: Optional[str] = None
    yes_price: Optional[float] = None
    no_price: Optional[float] = None
    invalid_reason: Optional[str] = None
    price_note: Optional[str] = None  # Explains why prices may be missing

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "slug": self.slug,
            "question": self.question,
            "category": self.category,
            "endDate": self.endDate,
            "hours_to_close": self.hours_to_close,
            "enableOrderBook": self.enableOrderBook,
            "active": self.active,
            "closed": self.closed,
            "yes_token_id": self.yes_token_id,
            "no_token_id": self.no_token_id,
            "yes_price": self.yes_price,
            "no_price": self.no_price,
            "invalid_reason": self.invalid_reason,
            "price_note": self.price_note,
        }

    def has_valid_prices(self) -> bool:
        return (
            self.yes_price is not None
            and self.no_price is not None
            and isinstance(self.yes_price, (int, float))
            and isinstance(self.no_price, (int, float))
        )
