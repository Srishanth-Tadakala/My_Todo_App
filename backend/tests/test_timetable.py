"""
Timetable, Recurring Schedule, Conflict Detection, and Exceptions Tests
"""

import pytest


@pytest.mark.asyncio
async def test_timetable_and_schedule_items(client, auth_headers):
    # 1. Create Timetable
    tt_res = await client.post(
        "/api/v1/timetable",
        json={"name": "Fall Semester 2026", "academic_year": "2026-2027", "semester": "Semester 5"},
        headers=auth_headers,
    )
    assert tt_res.status_code == 201
    timetable_id = tt_res.json()["id"]

    # 2. Create Schedule Item (Monday 10:00 - 11:00)
    item_res = await client.post(
        "/api/v1/timetable/items",
        json={
            "timetable_id": timetable_id,
            "title": "Operating Systems Lecture",
            "type": "CLASS",
            "day_of_week": 0,  # Monday
            "start_time": "10:00:00",
            "end_time": "11:00:00",
            "building": "Tech Block",
            "room": "LH-201",
        },
        headers=auth_headers,
    )
    assert item_res.status_code == 201
    item_id = item_res.json()["id"]

    # 3. Conflict Detection
    # A. Conflicting time (Monday 10:30 to 11:30)
    conflict_check_1 = await client.get(
        f"/api/v1/timetable/conflicts/check?timetable_id={timetable_id}&day_of_week=0&start_time=10:30:00&end_time=11:30:00",
        headers=auth_headers,
    )
    assert conflict_check_1.status_code == 200
    assert conflict_check_1.json()["has_conflict"] is True
    assert len(conflict_check_1.json()["conflicts"]) == 1
    assert conflict_check_1.json()["conflicts"][0]["conflicting_item_id"] == item_id

    # B. Non-conflicting time on same day (Monday 11:00 to 12:00)
    conflict_check_2 = await client.get(
        f"/api/v1/timetable/conflicts/check?timetable_id={timetable_id}&day_of_week=0&start_time=11:00:00&end_time=12:00:00",
        headers=auth_headers,
    )
    assert conflict_check_2.status_code == 200
    assert conflict_check_2.json()["has_conflict"] is False

    # C. Non-conflicting day (Tuesday 10:00 to 11:00)
    conflict_check_3 = await client.get(
        f"/api/v1/timetable/conflicts/check?timetable_id={timetable_id}&day_of_week=1&start_time=10:00:00&end_time=11:00:00",
        headers=auth_headers,
    )
    assert conflict_check_3.status_code == 200
    assert conflict_check_3.json()["has_conflict"] is False


@pytest.mark.asyncio
async def test_occurrences_and_exception_handling(client, auth_headers):
    # Create Timetable & Monday Class
    tt_res = await client.post(
        "/api/v1/timetable",
        json={"name": "Spring 2027", "is_active": True},
        headers=auth_headers,
    )
    timetable_id = tt_res.json()["id"]

    item_res = await client.post(
        "/api/v1/timetable/items",
        json={
            "timetable_id": timetable_id,
            "title": "Database Lab",
            "day_of_week": 0,  # Monday
            "start_time": "14:00:00",
            "end_time": "16:00:00",
        },
        headers=auth_headers,
    )
    item_id = item_res.json()["id"]

    # 2026-09-07 is Monday, 2026-09-14 is Monday
    occ_res = await client.get(
        f"/api/v1/timetable/occurrences?start_date=2026-09-01&end_date=2026-09-15&timetable_id={timetable_id}",
        headers=auth_headers,
    )
    assert occ_res.status_code == 200
    occs = occ_res.json()
    assert len(occs) == 2
    assert occs[0]["date"] == "2026-09-07"
    assert occs[1]["date"] == "2026-09-14"

    # Add Exception: Cancel class on 2026-09-07
    ex_res = await client.post(
        "/api/v1/timetable/exceptions",
        json={
            "schedule_item_id": item_id,
            "date": "2026-09-07",
            "exception_type": "CANCELLED",
            "notes": "Professor attending conference",
        },
        headers=auth_headers,
    )
    assert ex_res.status_code == 201

    # Verify occurrence on 2026-09-07 is now excluded
    occ_after = await client.get(
        f"/api/v1/timetable/occurrences?start_date=2026-09-01&end_date=2026-09-15&timetable_id={timetable_id}",
        headers=auth_headers,
    )
    assert occ_after.status_code == 200
    occs_after = occ_after.json()
    assert len(occs_after) == 1
    assert occs_after[0]["date"] == "2026-09-14"
