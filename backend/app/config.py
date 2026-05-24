import os

# sync_db settings
DEFAULT_SYNC_START_DATE = "2025-12-30"
LOOKBACK_DAYS = 7

# Lambda settings (for async sync processing in production)
USE_LAMBDA_FOR_SYNC = os.getenv("ENV", "local").lower() == "production"
LAMBDA_FUNCTION_NAME = os.getenv("LAMBDA_FUNCTION_NAME", "soccer-match-tracker-sync-worker")

