
## GitHub Action to Keep Supabase Alive - Setup Instructions
### 1. Store Your Database URL in GitHub Secrets

1. Go to your repository on **GitHub**.
    
2. Click **Settings** > **Secrets and variables** > **Actions**.
    
3. Click **New repository secret**.
    
4. **Name:** `DATABASE_URL`
    
5. **Secret:** Paste your Supabase connection string (e.g., `postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres`).
    
6. Click **Add secret**.
    

### 2. Create the Workflow File

Create a new file in your repository at `.github/workflows/weekly-query.yml`:

YAML

```
name: Weekly Supabase Query

on:
  schedule:
    # Runs every Sunday at midnight UTC
    - cron: '0 0 * * 0'
  # Allows manual runs from the GitHub Actions UI
  workflow_dispatch:

jobs:
  run-weekly-script:
    runs-on: ubuntu-latest

    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r backend/requirements.txt

      - name: Run script
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: |
          python backend/app/scripts/weekly_query.py
```

### 3. Test the Action

1. Commit and push `.github/workflows/weekly-query.yml` and `backend/app/scripts/weekly_query.py` to your `main` branch.
    
2. Go to the **Actions** tab in your GitHub repository.
    
3. Select **Weekly Supabase Query** from the left sidebar.
    
4. Click **Run workflow** -> **Run workflow**.
    
5. Click into the completed run and expand the **Run script** step to view your weekly database summary.