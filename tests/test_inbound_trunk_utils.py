# testing/test_inbound_trunk_utils.py
def test_parse_allowed_numbers_from_env_empty(monkeypatch):
    import inbound_trunk

    monkeypatch.delenv("INBOUND_ALLOWED_NUMBERS", raising=False)
    assert inbound_trunk._parse_allowed_numbers_from_env() is None

    monkeypatch.setenv("INBOUND_ALLOWED_NUMBERS", "   ")
    assert inbound_trunk._parse_allowed_numbers_from_env() is None


def test_parse_allowed_numbers_from_env_single(monkeypatch):
    import inbound_trunk

    monkeypatch.setenv("INBOUND_ALLOWED_NUMBERS", "+911234567890")
    result = inbound_trunk._parse_allowed_numbers_from_env()
    assert result == ["+911234567890"]


def test_parse_allowed_numbers_from_env_multiple(monkeypatch):
    import inbound_trunk

    monkeypatch.setenv(
        "INBOUND_ALLOWED_NUMBERS",
        " +911234567890, +919876543210 ,  +910000000000 ",
    )
    result = inbound_trunk._parse_allowed_numbers_from_env()
    assert result == ["+911234567890", "+919876543210", "+910000000000"]
