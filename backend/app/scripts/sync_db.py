import os
import sys
from datetime import datetime, timedelta
from sqlalchemy.dialects.postgresql import insert

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import SessionLocal
from app.models import Team, Match, Competition
from app.services.football_api import FootballAPIClient

def sync_data():
    db = SessionLocal()
    client = FootballAPIClient()
    
    #Find the last date in the DB
    last_match = db.query(Match).order_by(Match.utc_date.desc()).first()
    if last_match:
        # Go back 2 days to catch late score updates
        start_date = (last_match.utc_date - timedelta(days=2)).strftime("%Y-%m-%d")
        print(f"🔍 Last match: {last_match.utc_date}. Syncing from {start_date}...")
    else:
        start_date = "2024-08-01" # Default start for a new DB
        print(f"DB empty. Starting fresh from {start_date}...")

    processed_matches, _ = client.fetch_all_matches(date_from=start_date)
    
    for m in processed_matches:
        try:
            # UPDATE COMPETITION
            comp_stmt = insert(Competition).values(
                id=m['competition']['id'],
                external_id=m['competition']['id'],
                name=m['competition']['name'],
                code=m['competition']['code']
            ).on_conflict_do_update(
                index_elements=['external_id'],
                set_={'name': m['competition']['name'], 'code': m['competition']['code']}
            )
            db.execute(comp_stmt)

            # 3. UPDATE TEAMS (Home & Away)
            for side in ['home_team', 'away_team']:
                team_data = m[side]
                team_stmt = insert(Team).values(
                    id=team_data['id'],
                    external_id=team_data['id'],
                    name=team_data['name'],
                    short_name=team_data['short_name'],
                    tla=team_data['tla']
                ).on_conflict_do_update(
                    index_elements=['external_id'],
                    set_={'name': team_data['name'], 'short_name': team_data['short_name'], 'tla': team_data['tla']}
                )
                db.execute(team_stmt)

            # 4. UPDATE MATCH
            match_stmt = insert(Match).values(
                external_id=m['match_id'],
                utc_date=m['utc_date'],
                status=m['status'],
                home_team_id=m['home_team']['id'],
                away_team_id=m['away_team']['id'],
                score=m['score_json']
            ).on_conflict_do_update(
                index_elements=['external_id'],
                set_={'status': m['status'], 'score': m['score_json']}
            )
            db.execute(match_stmt)

        except Exception as e:
            print(f"Sync Error for match {m['match_id']}: {e}")
            continue

    db.commit()
    db.close()
    print("Database sync complete!")

if __name__ == "__main__":
    sync_data()