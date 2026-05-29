import pytest
from unittest.mock import AsyncMock, patch
from app.services.fallback_manager import execute_with_fallback
from app.providers.base import BaseProvider
from app.schemas.requests import RelayRequest

class MockProvider(BaseProvider):
    def __init__(self, name, should_fail=False, return_value="Success"):
        self._name = name
        self.should_fail = should_fail
        self.return_value = return_value
        self.call_count = 0

    @property
    def name(self) -> str:
        return self._name

    async def solve(self, request: RelayRequest) -> str:
        self.call_count += 1
        if self.should_fail:
            raise Exception(f"Provider {self.name} failed")
        return self.return_value

@pytest.mark.asyncio
async def test_fallback_success_first_try():
    p1 = MockProvider("p1")
    p2 = MockProvider("p2")
    chain = [p1, p2]
    req = RelayRequest(question="test")

    result = await execute_with_fallback(chain, req)

    assert result["success"] is True
    assert result["provider_used"] == "p1"
    assert p1.call_count == 1
    assert p2.call_count == 0

@pytest.mark.asyncio
async def test_fallback_retry_on_failure():
    p1 = MockProvider("p1", should_fail=True)
    p2 = MockProvider("p2")
    chain = [p1, p2]
    req = RelayRequest(question="test")

    result = await execute_with_fallback(chain, req)

    assert result["success"] is True
    assert result["provider_used"] == "p2"
    assert p1.call_count == 1
    assert p2.call_count == 1

@pytest.mark.asyncio
async def test_fallback_all_fail():
    p1 = MockProvider("p1", should_fail=True)
    p2 = MockProvider("p2", should_fail=True)
    chain = [p1, p2]
    req = RelayRequest(question="test")

    result = await execute_with_fallback(chain, req)

    assert result["success"] is False
    assert result["provider_used"] == "NONE"
    assert p1.call_count == 1
    assert p2.call_count == 1

@pytest.mark.asyncio
async def test_fallback_empty_response():
    p1 = MockProvider("p1", return_value="")
    p2 = MockProvider("p2")
    chain = [p1, p2]
    req = RelayRequest(question="test")

    result = await execute_with_fallback(chain, req)

    assert result["success"] is True
    assert result["provider_used"] == "p2"
    assert p1.call_count == 1
    assert p2.call_count == 1
