from abc import ABC, abstractmethod
from app.schemas.requests import RelayRequest


class BaseProvider(ABC):
    """
    Every provider adapter must implement `solve`.
    Returns the AI's plain-text answer as a string.
    Raises an exception on any failure — the FallbackManager catches it.
    """

    @abstractmethod
    async def solve(self, request: RelayRequest) -> str:
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable provider name used in logs and RelayResponse."""
        ...
