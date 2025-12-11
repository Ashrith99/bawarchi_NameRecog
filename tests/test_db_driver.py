# testing/test_db_driver.py
import pytest


@pytest.mark.asyncio
async def test_create_order_replaces_unknown_phone(fake_collection):
    import db

    driver = db.DatabaseDriver()
    items = [{"name": "Chicken Biryani", "price": 12.99, "quantity": 1}]

    # phone is "unknown" -> should be replaced with call_<timestamp>
    order = driver.create_order(phone="unknown", items=items, name="Test User")

    assert order is not None
    assert order["phone"].startswith("call_")
    assert order["status"] == "confirmed"
    assert "created_at" in order

    # Mongo fake got the insert
    assert len(fake_collection.inserted) == 1
    inserted_doc = fake_collection.inserted[0]
    assert inserted_doc["phone"] == order["phone"]
    assert inserted_doc["items"] == items


@pytest.mark.asyncio
async def test_create_order_with_clover_when_clover_disabled(fake_collection, monkeypatch):
    import db

    # For this unit test we force Clover disabled so it skips real HTTP
    monkeypatch.setattr(db, "CLOVER_ENABLED", False)

    driver = db.DatabaseDriver()
    items = [{"name": "Mutton Curry", "price": 15.99, "quantity": 2}]

    order = await driver.create_order_with_clover(
        phone="+1234567890",
        items=items,
        name="Test User",
    )

    assert order is not None
    assert order["phone"] == "+1234567890"
    # clover_order_id will not be set because Clover is disabled
    assert "clover_order_id" not in order
    assert len(fake_collection.inserted) == 1


@pytest.mark.asyncio
async def test_get_customer_name_by_phone_uses_clover_client(monkeypatch, fake_collection):
    import db

    # Fake Clover client with known response
    class FakeCloverClient:
        async def get_customer_by_phone(self, phone):
            return {"firstName": "John", "lastName": "Doe"}

    monkeypatch.setattr(db, "CLOVER_ENABLED", True)
    monkeypatch.setattr(db, "get_clover_client", lambda: FakeCloverClient())

    driver = db.DatabaseDriver()
    name = await driver.get_customer_name_by_phone("+123")
    assert name == "John Doe"


def test_get_order_by_phone(fake_collection):
    import db

    driver = db.DatabaseDriver()

    first = driver.create_order("+111", [{"name": "A", "price": 1.0, "quantity": 1}])
    second = driver.create_order("+111", [{"name": "B", "price": 2.0, "quantity": 2}])

    latest = driver.get_order_by_phone("+111")
    assert latest is not None
    assert latest["items"][0]["name"] == "B"
