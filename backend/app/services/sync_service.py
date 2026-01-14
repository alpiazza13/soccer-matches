from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models import SyncMetadata

# Helper to check if a sync is actually needed
def get_sync_freshness(db: Session, sync_key: str, threshold_seconds: int = 300) -> bool:
    sync_meta = db.query(SyncMetadata).filter_by(sync_key=sync_key).first()
    if not sync_meta:
        return False
    
    # Ensure we compare timezone-aware datetimes
    last_run = sync_meta.last_run_at.replace(tzinfo=timezone.utc)
    time_diff = datetime.now(timezone.utc) - last_run
    return time_diff.total_seconds() < threshold_seconds

# Helper to update metadata records
def update_sync_metadata(db: Session, sync_key: str, status: str, error: str | None = None):
    sync_meta = db.query(SyncMetadata).filter_by(sync_key=sync_key).first()
    if not sync_meta:
        sync_meta = SyncMetadata(sync_key=sync_key)
        db.add(sync_meta)
    
    sync_meta.last_run_at = datetime.now(timezone.utc)
    sync_meta.status = status
    sync_meta.last_error = error
    db.commit()

def get_last_sync_time(db: Session, sync_key: str) -> datetime | None:
    sync_meta = db.query(SyncMetadata).filter_by(sync_key=sync_key).first()
    return sync_meta.last_run_at if sync_meta else None

