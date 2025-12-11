# tests/conftest.py
import os
from types import SimpleNamespace

import pytest

# 1) Force a simple local Mongo URI for tests so db.py
#    does NOT try to connect to Atlas via mongodb+srv.
#    This is test-only; production still uses the real URI from your .env.
os.environ["MONGO_URI"] = "mongodb://localhost:27017"


class FakeInsertResult:
    def __init__(self, inserted_id="fake_id"):
        self.inserted_id = inserted_id


class FakeCollection:
    """
    Very small in-memory stand-in for the Mongo 'orders_collection'.
    """

    def __init__(self):
        self.inserted = []
        self.updated = []
        self.indexes_created = False

    def create_index(self, *args, **kwargs):
        # used by DatabaseDriver._ensure_indexes
        self.indexes_created = True

    def insert_one(self, doc):
        # used by DatabaseDriver.create_order / create_order_with_clover
        self.inserted.append(doc)
        return FakeInsertResult(inserted_id="mongo123")

    def update_one(self, filter_, update):
        # used when setting clover_order_id
        self.updated.append((filter_, update))

    def find_one(self, query, sort=None):
        # used by get_order_by_phone
        phone = query.get("phone")
        for doc in reversed(self.inserted):
            if doc.get("phone") == phone:
                return doc
        return None


@pytest.fixture
def fake_collection(monkeypatch):
    """
    Patch db.orders_collection so DatabaseDriver uses our in-memory FakeCollection.
    This prevents any real Mongo calls in tests.
    """
    import db  # safe now: MONGO_URI is already overridden above

    coll = FakeCollection()
    monkeypatch.setattr(db, "orders_collection", coll)
    return coll


@pytest.fixture
def fake_agent():
    """
    Minimal fake agent instance for tool factory tests in agent.py.
    """

    async def _terminate_call_after_delay():
        # In production this ends the call; in tests it's a no-op coroutine
        return None

    return SimpleNamespace(
        customer_name=None,
        caller_phone=None,
        order_placed=False,
        _terminate_call_after_delay=_terminate_call_after_delay,
    )
