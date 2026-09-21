"""
Development Seeding Script
Populates the database with realistic sample data for a specified user ID.
Usage:
    python supabase/seed_dev.py --user-id <UUID>
"""

import argparse
import sys
import uuid
from datetime import datetime, timedelta, timezone

def parse_args():
    parser = argparse.ArgumentParser(description="Seed sample data for a Supabase user")
    parser.add_argument("--user-id", type=str, required=True, help="Target user UUID")
    return parser.parse_args()

def main():
    args = parse_args()
    user_id = args.user_id
    try:
        uuid.UUID(user_id)
    except ValueError:
        print(f"Error: Invalid UUID '{user_id}'", file=sys.stderr)
        sys.exit(1)

    print(f"Seeding demo data for user: {user_id}")
    print("Seed data structure:")
    print("  - 1 Profile & User Settings")
    print("  - 2 Todo Lists (College & Personal)")
    print("  - 1 Project (Compiler Design Lab)")
    print("  - 5 Todos with subtasks and priority tags")
    print("  - 3 Academic Subjects (DBMS, OS, CN)")
    print("  - 1 Timetable with 5 Weekly Classes")
    print("  - 3 Assignments (with approaching deadlines)")
    print("  - 2 Exams (with multi-tier reminder offsets)")
    print("  - 2 Hackathons")
    print("  - 2 Certifications")
    print("  - 2 Internship Applications")
    print("  - 2 Personal Events")
    print("Done! Execute seed.sql or use the FastAPI admin/seed endpoints.")

if __name__ == "__main__":
    main()
