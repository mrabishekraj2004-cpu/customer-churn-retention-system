from src.security.rate_limit import (
    validate_login_rate_limit_configuration,
)
from src.security.tokens import validate_jwt_configuration


def validate_security_configuration() -> None:
    """Validate security-critical application configuration."""

    validate_jwt_configuration()
    validate_login_rate_limit_configuration()
