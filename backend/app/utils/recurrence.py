"""
Recurrence Expansion and Conflict Detection Utilities
"""

from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Optional, Tuple
from app.utils.datetime import parse_time


def check_time_conflict(
    start1: time,
    end1: time,
    start2: time,
    end2: time,
) -> bool:
    """
    Checks if two time ranges overlap on the same day:
    existing.start < new.end AND existing.end > new.start
    """
    return start1 < end2 and end1 > start2


def expand_schedule_item_occurrences(
    item: Dict[str, Any],
    start_d: date,
    end_d: date,
    exceptions: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """
    Generates occurrences of a weekly recurring schedule item within [start_d, end_d],
    applying any date-specific exceptions.
    """
    occurrences = []
    item_day = item.get("day_of_week")  # 0 = Monday, 6 = Sunday
    base_start = parse_time(item["start_time"])
    base_end = parse_time(item["end_time"])

    # Map exceptions by date string
    exception_map: Dict[str, Dict[str, Any]] = {}
    if exceptions:
        for ex in exceptions:
            if str(ex.get("schedule_item_id")) == str(item["id"]):
                exception_map[str(ex.get("date"))] = ex

    cur = start_d
    while cur <= end_d:
        if cur.weekday() == item_day:
            date_str = cur.isoformat()
            ex = exception_map.get(date_str)

            # Check if cancelled
            if ex and ex.get("exception_type") == "CANCELLED":
                cur += timedelta(days=1)
                continue

            # Check if rescheduled / modified
            occ_start = base_start
            occ_end = base_end
            building = item.get("building")
            floor = item.get("floor")
            room = item.get("room")
            notes = item.get("notes")

            if ex:
                if ex.get("new_start_time"):
                    occ_start = parse_time(ex["new_start_time"])
                if ex.get("new_end_time"):
                    occ_end = parse_time(ex["new_end_time"])
                if ex.get("new_building"):
                    building = ex["new_building"]
                if ex.get("new_floor"):
                    floor = ex["new_floor"]
                if ex.get("new_room"):
                    room = ex["new_room"]
                if ex.get("notes"):
                    notes = f"{notes or ''} [Exception: {ex['notes']}]".strip()

            occurrences.append({
                "id": f"{item['id']}_{date_str}",
                "schedule_item_id": item["id"],
                "timetable_id": item.get("timetable_id"),
                "subject_id": item.get("subject_id"),
                "title": item.get("title"),
                "type": item.get("type"),
                "date": date_str,
                "start_time": occ_start.strftime("%H:%M:%S"),
                "end_time": occ_end.strftime("%H:%M:%S"),
                "building": building,
                "floor": floor,
                "room": room,
                "teacher": item.get("teacher"),
                "is_exception": ex is not None,
                "exception_type": ex.get("exception_type") if ex else None,
                "notes": notes,
            })

        cur += timedelta(days=1)

    return occurrences
