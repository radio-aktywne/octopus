from datetime import datetime
from zoneinfo import ZoneInfo


def utczone() -> ZoneInfo:
    return ZoneInfo("Etc/UTC")


def utcnow() -> datetime:
    return datetime.now(utczone())


def stringify(dt: datetime) -> str:
    """Convert a datetime to a string in ISO 8601 format"""

    return dt.isoformat().replace("+00:00", "Z")
