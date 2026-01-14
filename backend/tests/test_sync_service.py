import pytest
from datetime import datetime, timedelta, timezone
from app.models import SyncMetadata
from app.services.sync_service import get_sync_freshness, update_sync_metadata, get_last_sync_time

def test_get_sync_freshness_no_record(db_session):
    """Should return False if no sync record exists."""
    assert get_sync_freshness(db_session, "test_sync") is False

def test_get_sync_freshness_stale(db_session):
    """Should return False if the last sync was 10 minutes ago."""
    old_time = datetime.now(timezone.utc) - timedelta(minutes=10)
    meta = SyncMetadata(sync_key="test_sync", last_run_at=old_time)
    db_session.add(meta)
    db_session.commit()
    
    assert get_sync_freshness(db_session, "test_sync", threshold_seconds=300) is False

def test_get_sync_freshness_recent(db_session):
    """Should return True if the last sync was 1 minute ago."""
    recent_time = datetime.now(timezone.utc) - timedelta(minutes=1)
    meta = SyncMetadata(sync_key="test_sync", last_run_at=recent_time)
    db_session.add(meta)
    db_session.commit()
    
    assert get_sync_freshness(db_session, "test_sync", threshold_seconds=300) is True

def test_update_sync_metadata_new(db_session):
    """Should create a new record if one doesn't exist."""
    update_sync_metadata(db_session, "new_sync", status="SUCCESS")
    
    record = db_session.query(SyncMetadata).filter_by(sync_key="new_sync").first()
    assert record is not None
    assert record.status == "SUCCESS"

def test_update_sync_metadata_update_existing(db_session):
    """Should update the existing record instead of creating a duplicate."""
    meta = SyncMetadata(sync_key="test_sync", last_run_at=datetime.now(timezone.utc), status="PENDING")
    db_session.add(meta)
    db_session.commit()
    
    update_sync_metadata(db_session, "test_sync", status="FAILED", error="Timeout")
    
    record = db_session.query(SyncMetadata).filter_by(sync_key="test_sync").first()
    assert record.status == "FAILED"
    assert record.last_error == "Timeout"

def test_get_sync_freshness_exact_boundary(db_session):
    """Test the exact 300-second boundary."""
    # 299 seconds ago should be FRESH (True)
    fresh_time = datetime.now(timezone.utc) - timedelta(seconds=299)
    meta = SyncMetadata(sync_key="boundary_test", last_run_at=fresh_time)
    db_session.add(meta)
    db_session.commit()
    assert get_sync_freshness(db_session, "boundary_test", 300) is True

    # 301 seconds ago should be STALE (False)
    meta.last_run_at = datetime.now(timezone.utc) - timedelta(seconds=301)
    db_session.commit()
    assert get_sync_freshness(db_session, "boundary_test", 300) is False

def test_get_last_sync_time(db_session):
    # Case: No record exists
    assert get_last_sync_time(db_session, "matches_sync") is None
    
    # Case: Record exists
    now = datetime.now(timezone.utc)
    update_sync_metadata(db_session, "matches_sync", "SUCCESS")
    last_time = get_last_sync_time(db_session, "matches_sync")
    assert last_time is not None
    # Check that it's within a few seconds of 'now'
    assert (now - last_time.replace(tzinfo=timezone.utc)).total_seconds() < 5

