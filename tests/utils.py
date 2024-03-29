from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

CURRENT_TIME = datetime(2022, 12, 24, 12, 45, 0, 0, tzinfo=timezone.utc)
CURRENT_TIMESTAMP = CURRENT_TIME.timestamp()

MOVE_FORWARD_CURRENT_TIME = CURRENT_TIME + timedelta(weeks=156)

TOKEN_EXPIRATION_TIME = datetime(2024, 12, 24, 12, 45, tzinfo=timezone.utc)
TOKEN_EXPIRES_AT = TOKEN_EXPIRATION_TIME.strftime("%Y-%m-%dT%H:%M:%SZ")

NEW_TOKEN_EXPIRATION_TIME = datetime(2026, 12, 24, 12, 45, tzinfo=timezone.utc)
NEW_TOKEN_EXPIRES_AT = NEW_TOKEN_EXPIRATION_TIME.strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class LogLevel:
    """Loglevel name and numeric value"""

    name: str
    value: int
