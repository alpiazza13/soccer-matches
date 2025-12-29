# Soccer Highlight Tracker: Project Map

## Goal
A web app to track which soccer matches I've watched.

## Architecture
- **Backend:** FastAPI (Python)
- **Frontend:** Next.js (React)
- **Database:** Supabase (Postgres)
- **Infrastructure:**
    - **Frontend:** AWS Amplify (manages S3 + CloudFront for Next.js)
    - **Backend:** AWS Lambda + API Gateway (FastAPI)
    - **Automation:** AWS EventBridge (fetch soccer matches daily at 3:00 AM)


