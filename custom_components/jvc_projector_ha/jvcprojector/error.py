"""Custom errors for a JVC Projector."""


class JvcProjectorError(Exception):
    """Projector Error."""


class JvcProjectorConnectError(JvcProjectorError):
    """Projector Connect Timeout."""


class JvcProjectorCommandError(JvcProjectorError):
    """Projector Command Error."""


class JvcProjectorAuthError(JvcProjectorError):
    """Projector Password Invalid Error."""

    def __init__(self, message: str | None = None) -> None:
        """Initialize the auth error with a helpful message."""
        if message is None:
            message = "Projector rejected the password"
        super().__init__(message)
