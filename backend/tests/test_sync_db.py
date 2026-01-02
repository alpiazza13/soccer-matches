import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects import postgresql
from unittest.mock import MagicMock
from datetime import datetime, timedelta
from app.scripts.sync_db import get_sync_start_date, upsert_competition, upsert_team, upsert_match
from app.models import Match
from app.config import DEFAULT_SYNC_START_DATE, LOOKBACK_DAYS
from app.scripts import sync_db

def test_get_sync_start_date_empty_db():
    mock_db = MagicMock()
    mock_db.query.return_value.order_by.return_value.first.return_value = None
    result = get_sync_start_date(mock_db)
    assert result == DEFAULT_SYNC_START_DATE

def test_get_sync_start_date_with_existing_match(mock_db):
    latest_match_date = datetime(2026, 1, 15)
    mock_match = MagicMock(spec=Match)
    mock_match.utc_date = latest_match_date
    mock_db.query.return_value.order_by.return_value.first.return_value = mock_match
    result = get_sync_start_date(mock_db)
    
    expected_date = (latest_match_date - timedelta(days=LOOKBACK_DAYS)).strftime("%Y-%m-%d")
    assert result == expected_date

def test_upsert_competition_success(mock_db, sample_competition):
    upsert_competition(mock_db, sample_competition)
    assert mock_db.execute.call_count == 1
    
    call_args = mock_db.execute.call_args[0][0]
    inserted_values = call_args.compile().params
    assert inserted_values['id'] == sample_competition.id
    assert inserted_values['name'] == sample_competition.name
    assert inserted_values['code'] == sample_competition.code


def test_upsert_competition_fail(mock_db, sample_competition):
    mock_db.execute.side_effect = SQLAlchemyError("Database connection lost")
    with pytest.raises(SQLAlchemyError) as excinfo:
        upsert_competition(mock_db, sample_competition)
    
    assert "Database connection lost" in str(excinfo.value)
    assert mock_db.execute.call_count == 1

'''
def test_upsert_competition_statement_structure(mock_db, sample_competition):
    upsert_competition(mock_db, sample_competition)
    stmt = mock_db.execute.call_args[0][0]
    assert stmt.is_insert
    assert str(stmt).find("ON CONFLICT") != -1
'''

def test_upsert_competition_statement_structure(mock_db, sample_competition):
    upsert_competition(mock_db, sample_competition)
    stmt = mock_db.execute.call_args[0][0]
    compiled_stmt = str(stmt.compile(dialect=postgresql.dialect()))
    
    assert "INSERT INTO competitions" in compiled_stmt
    assert "ON CONFLICT (external_id) DO UPDATE SET" in compiled_stmt
    assert "name =" in compiled_stmt
    assert "code =" in compiled_stmt

def test_upsert_team_success(mock_db, sample_team):
    upsert_team(mock_db, sample_team)
    assert mock_db.execute.call_count == 1
    
    call_args = mock_db.execute.call_args[0][0]
    inserted_values = call_args.compile().params
    
    assert inserted_values['id'] == sample_team.id
    assert inserted_values['name'] == sample_team.name
    assert inserted_values['short_name'] == sample_team.short_name
    assert inserted_values['tla'] == sample_team.tla

def test_upsert_team_fail(mock_db, sample_team):
    mock_db.execute.side_effect = SQLAlchemyError("Connection Timeout")
    
    with pytest.raises(SQLAlchemyError) as excinfo:
        upsert_team(mock_db, sample_team)
    
    assert "Connection Timeout" in str(excinfo.value)
    assert mock_db.execute.call_count == 1

def test_upsert_team_statement_structure(mock_db, sample_team):
    upsert_team(mock_db, sample_team)
    stmt = mock_db.execute.call_args[0][0]
    compiled_stmt = str(stmt.compile(dialect=postgresql.dialect()))
    
    assert "INSERT INTO teams" in compiled_stmt
    assert "ON CONFLICT (external_id) DO UPDATE SET" in compiled_stmt
    assert "short_name =" in compiled_stmt
    assert "tla =" in compiled_stmt


def test_upsert_match_success(mock_db, sample_match):
    m = sample_match
    upsert_match(mock_db, m)
    assert mock_db.execute.call_count == 1

    call_args = mock_db.execute.call_args[0][0]
    inserted_values = call_args.compile().params

    assert inserted_values['external_id'] == m.match_id
    assert inserted_values['status'] == m.status
    assert inserted_values['home_team_id'] == m.home_team.id
    assert inserted_values['away_team_id'] == m.away_team.id
    assert inserted_values['competition_id'] == m.competition.id
    assert inserted_values['score'] == m.score.model_dump()


def test_upsert_match_fail(mock_db, sample_match):
    m = sample_match
    mock_db.execute.side_effect = SQLAlchemyError("Insert failed")
    with pytest.raises(SQLAlchemyError) as excinfo:
        upsert_match(mock_db, m)

    assert "Insert failed" in str(excinfo.value)
    assert mock_db.execute.call_count == 1


def test_upsert_match_statement_structure(mock_db, sample_match):
    m = sample_match
    upsert_match(mock_db, m)
    stmt = mock_db.execute.call_args[0][0]
    compiled_stmt = str(stmt.compile(dialect=postgresql.dialect()))

    assert "INSERT INTO matches" in compiled_stmt
    assert "ON CONFLICT (external_id) DO UPDATE SET" in compiled_stmt
    assert "utc_date =" in compiled_stmt
    assert "score =" in compiled_stmt


def test_sync_data_success(monkeypatch, sample_match):
    mock_db = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.close = MagicMock()

    monkeypatch.setenv("ENV", "production")
    monkeypatch.setattr(sync_db, "SessionLocal", lambda: mock_db)

    client = MagicMock()
    client.fetch_all_matches.return_value = ([sample_match], 1)
    monkeypatch.setattr(sync_db, "FootballAPIClient", lambda: client)

    upsert_comp = MagicMock()
    upsert_team = MagicMock()
    upsert_match = MagicMock()
    monkeypatch.setattr(sync_db, "upsert_competition", upsert_comp)
    monkeypatch.setattr(sync_db, "upsert_team", upsert_team)
    monkeypatch.setattr(sync_db, "upsert_match", upsert_match)

    sync_db.sync_data()

    upsert_comp.assert_called_once_with(mock_db, sample_match.competition)
    assert upsert_team.call_count == 2
    upsert_match.assert_called_once_with(mock_db, sample_match)
    mock_db.commit.assert_called_once()
    mock_db.close.assert_called_once()


def test_sync_data_continues_on_upsert_error(monkeypatch, sample_match):
    mock_db = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.close = MagicMock()

    monkeypatch.setenv("ENV", "production")
    monkeypatch.setattr(sync_db, "SessionLocal", lambda: mock_db)

    client = MagicMock()
    m1 = sample_match
    m2 = sample_match.model_copy(deep=True)
    m2.match_id = 999999
    client.fetch_all_matches.return_value = ([m1, m2], 2)
    monkeypatch.setattr(sync_db, "FootballAPIClient", lambda: client)

    upsert_comp = MagicMock(side_effect=[Exception("boom"), None])
    upsert_team = MagicMock()
    upsert_match = MagicMock()
    monkeypatch.setattr(sync_db, "upsert_competition", upsert_comp)
    monkeypatch.setattr(sync_db, "upsert_team", upsert_team)
    monkeypatch.setattr(sync_db, "upsert_match", upsert_match)

    # Should not raise despite first upsert raising
    sync_db.sync_data()

    assert mock_db.commit.called
    assert mock_db.close.called
    assert upsert_comp.call_count == 2
    upsert_match.assert_called_with(mock_db, m2)