from datetime import datetime

from zoneinfo import ZoneInfo


def utczone() -> ZoneInfo:
    """Return the UTC time zone."""

    return ZoneInfo("Etc/UTC")


def utcnow() -> datetime:
    """Return the current datetime in UTC."""

    return datetime.now(utczone())


def stringify(dt: datetime) -> str:
    """Convert a datetime to a string in ISO 8601 format."""

    return dt.isoformat().replace("+00:00", "Z")
