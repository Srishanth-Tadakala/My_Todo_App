"""
DateTime and Timezone Utilities
Enforces UTC storage and user IANA timezone conversions.
"""

from datetime import datetime, time, timedelta, timezone
from typing import Optional, Union
import zoneinfo
from dateutil import parser


def now_utc() -> datetime:
    """Returns the current aware datetime in UTC."""
    return datetime.now(timezone.utc)


def parse_datetime(val: Union[str, datetime]) -> datetime:
    """Parses an ISO string or datetime into a UTC-aware datetime."""
    if isinstance(val, datetime):
        if val.tzinfo is None:
            return val.replace(tzinfo=timezone.utc)
        return val.astimezone(timezone.utc)
    parsed = parser.isoparse(val)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def parse_time(time_str: Union[str, time]) -> time:
    """Parses a time string (e.g. '09:00:00' or '09:00') into a time object."""
    if isinstance(time_str, time):
        return time_str
    parts = time_str.split(":")
    hour = int(parts[0])
    minute = int(parts[1])
    second = int(parts[2]) if len(parts) > 2 else 0
    return time(hour=hour, minute=minute, second=second)


def get_zoneinfo(tz_name: Optional[str]) -> zoneinfo.ZoneInfo:
    """Safely retrieves a ZoneInfo instance, falling back to UTC."""
    if not tz_name:
        return zoneinfo.ZoneInfo("UTC")
    try:
        return zoneinfo.ZoneInfo(tz_name)
    except Exception:
        return zoneinfo.ZoneInfo("UTC")


def to_user_timezone(dt_utc: datetime, tz_str: Optional[str]) -> datetime:
    """Converts a UTC datetime into the user's local timezone."""
    dt = parse_datetime(dt_utc)
    target_tz = get_zoneinfo(tz_str)
    return dt.astimezone(target_tz)


def from_user_timezone(local_dt: datetime, tz_str: Optional[str]) -> datetime:
    """Converts a local datetime to UTC."""
    target_tz = get_zoneinfo(tz_str)
    if local_dt.tzinfo is None:
        local_dt = local_dt.replace(tzinfo=target_tz)
    return local_dt.astimezone(timezone.utc)


def is_in_quiet_hours(
    dt_utc: datetime,
    tz_str: str,
    quiet_start_str: str,
    quiet_end_str: str,
) -> bool:
    """
    Determines whether a UTC datetime falls within the user's quiet hours window.
    Handles overnight spans (e.g. 22:00 -> 07:00).
    """
    local_dt = to_user_timezone(dt_utc, tz_str)
    t = local_dt.time()
    start_t = parse_time(quiet_start_str)
    end_t = parse_time(quiet_end_str)

    if start_t <= end_t:
        # Same day range (e.g., 13:00 to 15:00)
        return start_t <= t <= end_t
    else:
        # Overnight range (e.g., 22:00 to 07:00)
        return t >= start_t or t <= end_t


def adjust_for_quiet_hours(
    dt_utc: datetime,
    tz_str: str,
    quiet_start_str: str,
    quiet_end_str: str,
) -> datetime:
    """
    If dt_utc falls within quiet hours, shifts it to the next occurrence of quiet_end in UTC.
    """
    if not is_in_quiet_hours(dt_utc, tz_str, quiet_start_str, quiet_end_str):
        return dt_utc

    local_dt = to_user_timezone(dt_utc, tz_str)
    end_t = parse_time(quiet_end_str)

    # Calculate end datetime
    candidate = datetime.combine(local_dt.date(), end_t, tzinfo=get_zoneinfo(tz_str))
    if candidate <= local_dt:
        # Quiet end is on the next day
        candidate += timedelta(days=1)

    return candidate.astimezone(timezone.utc)
