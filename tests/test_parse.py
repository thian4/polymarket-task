from src.core.parse import safe_parse_json_or_list, parse_market_data


def test_parse_json_string_to_list():
    assert safe_parse_json_or_list('["Yes", "No"]') == ["Yes", "No"]
    assert safe_parse_json_or_list(["Yes", "No"]) == ["Yes", "No"]
    assert safe_parse_json_or_list("invalid") is None


def test_parse_valid_binary_market():
    raw = {
        "id": "123",
        "outcomes": ["Yes", "No"],
        "outcomePrices": ["0.6", "0.4"],
        "clobTokenIds": ["token1", "token2"],
    }
    record = parse_market_data(raw)
    assert record.yes_price == 0.6
    assert record.no_price == 0.4
    assert record.invalid_reason is None


def test_parse_json_string_fields():
    raw = {
        "id": "123",
        "outcomes": '["Yes", "No"]',
        "outcomePrices": '["0.5", "0.5"]',
        "clobTokenIds": '["t1", "t2"]',
    }
    record = parse_market_data(raw)
    assert record.yes_price == 0.5
    assert record.invalid_reason is None


def test_invalid_non_binary_market():
    raw = {"id": "123", "outcomes": ["Yes", "No", "Maybe"]}
    record = parse_market_data(raw)
    assert "not binary" in record.invalid_reason


def test_price_note_when_prices_missing():
    raw = {
        "id": "123",
        "outcomes": ["Yes", "No"],
        "clobTokenIds": ["t1", "t2"],
        # No outcomePrices
    }
    record = parse_market_data(raw)
    assert record.yes_price is None
    assert record.no_price is None
    assert record.price_note == "outcomePrices missing or insufficient length"
    assert record.invalid_reason is None  # Not invalid, just missing prices


def test_price_note_when_prices_unparseable():
    raw = {
        "id": "123",
        "outcomes": ["Yes", "No"],
        "outcomePrices": ["not_a_number", "0.5"],
        "clobTokenIds": ["t1", "t2"],
    }
    record = parse_market_data(raw)
    assert record.yes_price is None
    assert record.no_price == 0.5
    assert record.price_note == "outcomePrices contains unparseable values"
