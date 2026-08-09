import os
import sys

# Ensure backend directory is on the path so app imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.database import SessionLocal
from app.models import Match, User, Team


def run_weekly_query():
    """Queries Supabase database and prints simple metrics."""
    print("Connecting to Supabase...")
    
    # Verify environment
    if not os.getenv("DATABASE_URL"):
        print("Error: DATABASE_URL environment variable is not set.")
        sys.exit(1)

    db = SessionLocal()
    try:
        match_count = db.query(Match).count()
        team_count = db.query(Team).count()
        user_count = db.query(User).count()
        print("--- WEEKLY DATABASE SUMMARY ---")
        print(f"Total Matches Stored : {match_count}")
        print(f"Total Teams Stored   : {team_count}")
        print(f"Total Registered Users: {user_count}")
        print("-------------------------------")
    except Exception as e:
        print(f"Error querying database: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    run_weekly_query()