# tests/test_agent_tools.py
import asyncio
import pytest


@pytest.mark.asyncio
async def test_create_order_tool_uses_caller_phone_and_saves_order(
    monkeypatch, fake_agent
):
    import agent

    called = {}

    # Fake db driver to avoid real Mongo/Clover
    class FakeDriver:
        async def create_order_with_clover(
            self, phone, items, name=None, address=None
        ):
            # record what was passed in so the test can assert on it
            called["phone"] = phone
            called["items"] = items
            return {"_id": "mongo123", "phone": phone, "items": items}

    def fake_get_db_driver():
        return FakeDriver()

    monkeypatch.setattr(agent, "get_db_driver", fake_get_db_driver)

    fake_agent.caller_phone = "+911234567890"
    fake_agent.order_placed = False

    tool = agent.create_order_tool_factory(fake_agent)

    items = [agent.OrderItem(name="Chicken Biryani", quantity=1, price=12.99)]
    response = await tool(items=items, phone=None, name="Test User", address=None)

    # Give the event loop a chance to run save_order_async()
    await asyncio.sleep(0)

    # 1) Tool should return a success message
    assert "Order placed successfully" in response

    # 2) DB driver should have been called with caller_phone and items (as dicts)
    assert called.get("phone") == "+911234567890"
    assert called.get("items") is not None
    assert len(called["items"]) == 1

    first_item = called["items"][0]
    assert first_item["name"] == "Chicken Biryani"
    assert first_item["quantity"] == 1
    assert first_item["price"] == 12.99
