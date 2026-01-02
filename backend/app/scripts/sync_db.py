import os
import sys
from datetime import timedelta
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from app.config import DEFAULT_SYNC_START_DATE, LOOKBACK_DAYS


# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models import Team, Match, Competition
from app.schemas import TeamSchema, MatchSchema, CompetitionSchema
from app.services.football_api import FootballAPIClient


def get_sync_start_date(db: Session) -> str:
    """Logic for determining the start date."""
    last_match = db.query(Match).order_by(Match.utc_date.desc()).first()
    if last_match:
        return (last_match.utc_date - timedelta(days=LOOKBACK_DAYS)).strftime("%Y-%m-%d")
    return DEFAULT_SYNC_START_DATE


def upsert_competition(db: Session, competition: CompetitionSchema):
    """Handles Competition table logic."""
    stmt = insert(Competition).values(
        id=competition.id,
        external_id=competition.id,
        name=competition.name,
        code=competition.code
    ).on_conflict_do_update(
        index_elements=[Competition.external_id.name],
        set_={
            Competition.name.name: competition.name,
            Competition.code.name: competition.code
        }
    )
    db.execute(stmt)

def upsert_team(db: Session, team: TeamSchema):
    """Handles Team table logic."""
    stmt = insert(Team).values(
        id=team.id,
        external_id=team.id,
        name=team.name,
        short_name=team.short_name,
        tla=team.tla
    ).on_conflict_do_update(
        index_elements=[Team.external_id.name],
        set_={
            Team.name.name: team.name,
            Team.short_name.name: team.short_name,
            Team.tla.name: team.tla
        }
    )
    db.execute(stmt)


def upsert_match(db: Session, m: MatchSchema):
    """Handles Match table logic."""
    # Convert the score object to a dict to ensure JSON serialization
    score_dict = m.score.model_dump()
    stmt = insert(Match).values(
        external_id=m.match_id,
        utc_date=m.utc_date,
        status=m.status,
        home_team_id=m.home_team.id,
        away_team_id=m.away_team.id,
        competition_id=m.competition.id,
        score=score_dict
    ).on_conflict_do_update(
        index_elements=[Match.external_id.name],
        set_={
            Match.competition_id.name: m.competition.id,
            Match.status.name: m.status,
            Match.utc_date.name: m.utc_date,
            Match.home_team_id.name: m.home_team.id,
            Match.away_team_id.name: m.away_team.id,
            Match.score.name: score_dict
        }
    )
    db.execute(stmt)

def sync_data():
    print("Starting sync DB...")
    db = SessionLocal()
    client = FootballAPIClient()
    
    start_date = get_sync_start_date(db)
    print("Got start date = ", start_date)
    processed_matches, _ = client.fetch_all_matches(date_from=start_date)
    
    for m in processed_matches:
        try:
            upsert_competition(db, m.competition)
            upsert_team(db, m.home_team)
            upsert_team(db, m.away_team)
            upsert_match(db, m)
        except Exception as e:
            print(f"Sync Error for match {m.match_id}: {e}")
            continue

    db.commit()
    db.close()
    print("Finished syncing db.")

if __name__ == "__main__":
    sync_data()