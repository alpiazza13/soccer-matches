# Soccer Match Tracker Web App Implementation Plan

## Architecture Overview

The application will consist of:

- **Backend**: FastAPI (Python) with endpoints for match CRUD operations and scheduled fetching
- **Frontend**: Next.js (React) with a table-based UI for viewing and updating matches
- **Database**: Supabase (PostgreSQL) for persistent storage
- **API Integration**: Football Data API v4 for match data

## Database Schema

### `matches` table

- `id` (BIGINT PRIMARY KEY) - Match ID from Football Data API
- `home_team` (VARCHAR) - Home team short name
- `away_team` (VARCHAR) - Away team short name
- `home_score` (INTEGER, nullable) - Home team score
- `away_score` (INTEGER, nullable) - Away team score
- `match_date` (TIMESTAMP) - Match date/time in UTC
- `date_display` (VARCHAR) - Formatted date (MM/DD/YYYY)
- `time_display` (VARCHAR) - Formatted time (HH:MM AM/PM Eastern)
- `competition` (VARCHAR) - Competition name
- `done_with` (BOOLEAN DEFAULT FALSE) - Whether highlights have been watched
- `created_at` (TIMESTAMP) - Record creation timestamp
- `updated_at` (TIMESTAMP) - Last update timestamp

### `raw_match_data` table (optional, for storing full API responses)

- `id` (BIGINT PRIMARY KEY) - Match ID
- `match_data` (JSONB) - Full match data from API
- `created_at` (TIMESTAMP)

## Project Structure

```javascript
soccer-matches/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── models.py            # SQLAlchemy/Pydantic models
│   │   ├── database.py          # Database connection (Supabase)
│   │   ├── schemas.py           # Pydantic schemas for API
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes/
│   │   │       ├── matches.py   # Match CRUD endpoints
│   │   │       └── fetch.py     # Endpoint to trigger match fetching
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── football_api.py  # Football Data API client
│   │   │   └── match_service.py # Business logic for matches
│   │   └── utils/
│   │       └── date_utils.py    # Date formatting utilities
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/                     # Next.js app directory
│   │   ├── layout.tsx
│   │   ├── page.tsx             # Main matches table page
│   │   └── api/                 # API route handlers (if needed)
│   ├── components/
│   │   ├── MatchesTable.tsx     # Main table component
│   │   ├── MatchRow.tsx         # Individual match row
│   │   └── StatusToggle.tsx     # Done/Not Done toggle
│   ├── lib/
│   │   └── api.ts               # API client functions
│   ├── package.json
│   └── .env.local.example
├── docs/
├── get_matches.py              # Original script (kept for reference)
└── README.md
```



## Implementation Steps

### Phase 1: Backend Setup

1. **Initialize FastAPI project structure**

- Create `backend/` directory with FastAPI app
- Set up dependency management (`requirements.txt`)
- Configure environment variables for API keys and database

2. **Database setup**

- Create Supabase project and database
- Define SQLAlchemy models in `models.py`
- Set up database connection using Supabase client or SQLAlchemy
- Create migration scripts or direct SQL for table creation

3. **Football Data API service**

- Create `football_api.py` service to handle API calls
- Implement rate limiting (10 calls/minute)
- Extract match data transformation logic from `get_matches.py`
- Handle date range queries (fetch matches since last date)

4. **Match service layer**

- Create `match_service.py` with business logic:
    - Fetch new matches from API
    - Merge with existing matches (avoid duplicates)
    - Update "done_with" status
    - Format dates/times for display

5. **API endpoints**

- `GET /api/matches` - List all matches (with filtering, sorting, pagination)
- `GET /api/matches/{match_id}` - Get single match
- `PATCH /api/matches/{match_id}/done` - Toggle done_with status
- `POST /api/matches/fetch` - Trigger manual match fetching
- `GET /api/matches/stats` - Get statistics (total, done, pending)

### Phase 2: Frontend Setup

1. **Initialize Next.js project**

- Create `frontend/` directory with Next.js app
- Set up TypeScript configuration
- Configure API client to communicate with FastAPI backend

2. **Matches table component**

- Create `MatchesTable.tsx` with:
    - Table layout matching Excel structure
    - Columns: Done with?, Date, Time, Home, Home Score, Away Score, Away, Match ID
    - Sortable columns (default: date descending)
    - Filtering by competition, done status
    - Responsive design

3. **Status toggle functionality**

- Create toggle component for "Done with?" column
- Implement optimistic UI updates
- Handle API errors gracefully

4. **UI enhancements**

- Loading states
- Error handling
- Empty states
- Basic styling (modern, clean design)

### Phase 3: Integration & Testing

1. **Connect frontend to backend**

- Configure CORS in FastAPI
- Set up API client with proper error handling
- Test end-to-end workflows

2. **Data fetching automation**

- Create scheduled job function (for future EventBridge integration)
- Test manual trigger endpoint
- Verify duplicate prevention logic

3. **Testing**

- Test match fetching from API
- Test CRUD operations
- Test date formatting and timezone conversion
- Verify incremental updates work correctly

## Key Features to Implement

1. **Match Fetching Logic** (from `get_matches.py`):

- Fetch matches since last match date
- Support all competitions: Serie A, Premier League, Champions League, Ligue 1, Bundesliga, Spanish League, World Cup, Euros
- Handle rate limiting (10 calls/minute)
- Convert UTC to Eastern time for display

2. **Match Management**:

- Display matches in reverse chronological order (newest first)
- Toggle "done_with" status with single click
- Prevent duplicate matches (by Match ID)
- Preserve "done_with" status when updating matches

3. **UI/UX**:

- Table view similar to Excel
- Clear visual indication of watched/unwatched matches
- Filter by competition
- Sort by date, competition, teams
- Responsive design for mobile/desktop

## Environment Variables

**Backend (.env)**:

- `FOOTBALL_DATA_API_TOKEN` - API token for Football Data API
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase service role key
- `DATABASE_URL` - PostgreSQL connection string
- `CORS_ORIGINS` - Allowed frontend origins

**Frontend (.env.local)**:

- `NEXT_PUBLIC_API_URL` - FastAPI backend URL

## Notes

- Team reminders feature will be removed (per user preference)
- No authentication needed (single-user app)
- Raw match data storage is optional but can be useful for debugging