"""
Exams Tests
"""

import pytest


@pytest.mark.asyncio
async def test_exam_crud_and_reminders(client, auth_headers):
    payload = {
        "title": "DBMS Final Exam",
        "exam_date": "2026-11-10",
        "start_time": "10:00:00",
        "end_time": "13:00:00",
        "building": "Main Auditorium",
        "room": "Hall B",
        "syllabus": "Modules 1 to 5",
        "reminder_offsets": [10080, 1440, 120],  # 7d, 1d, 2h
    }
    res = await client.post("/api/v1/exams", json=payload, headers=auth_headers)
    assert res.status_code == 201
    exam = res.json()
    assert exam["title"] == "DBMS Final Exam"
    exam_id = exam["id"]

    # Verify multi-tier reminder offsets stored
    assert len(exam["reminder_offsets"]) == 3

    # Update Exam
    up_res = await client.put(
        f"/api/v1/exams/{exam_id}",
        json={"room": "Hall A (Relocated)"},
        headers=auth_headers,
    )
    assert up_res.status_code == 200
    assert up_res.json()["room"] == "Hall A (Relocated)"

    # Delete Exam
    del_res = await client.delete(f"/api/v1/exams/{exam_id}", headers=auth_headers)
    assert del_res.status_code == 200
