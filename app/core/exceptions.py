class RelayError(Exception):
    """Base error for relay-level failures."""
    pass


class AllProvidersExhaustedError(RelayError):
    """Raised when every provider in a fallback chain has failed."""
    pass


class InvalidMediaError(RelayError):
    """Raised when media bytes cannot be decoded or preprocessed."""
    pass
