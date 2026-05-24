
### Database Setup on Supabase
1. Sign up at supabase.com and create Soccer Matches project
2. Chose "Only Connection String" when asked what type of connections you plan to use, as it is more efficient to connect in Python using the connection string than Supabase's "Data API"
3. Add `SUPABASE_URL`, `SUPABASE_KEY`, and `DATABASE_URL` variables to .env. These can be found in Supabase as the project URL, public API key, and database connection string, respectively.
4. Create models.py file
5. Set up Alembic ([Alembic Setup](#Alembic%20Setup))
### Alembic Setup
1. In Terminal, from project root, run `alembic init alembic`. A folder named `alembic` and a file named `alembic.ini` should be created at the project root.
2. In `alembic.ini`, find the line that starts with `sqlalchemy.url` and replace it with the following so that alembic gets the` DATABASE_URL` property from the .env file: `sqlalchemy.url = %(DATABASE_URL)s`
3. Update `alembic/env.py` file to tell Alembic where to find the Table Blueprints (Models)
	1. Add the very top (right under `from logging.config import fileConfig` add the below lines so that Alembic can see the backend folder):
		```python
			import sys 
			from os.path import abspath, dirname 
			sys.path.insert(0, abspath(dirname(dirname(__file__))))
			sys.path.insert(0, abspath(dirname(dirname(__file__)) + "/backend"))
		```
	2. Add the below import statements
	```python
			from app.database import Base 
			from app.models import Team, Match, Competition
	```
	3. Set the `target_metadata` variable to equal `Base.metadata`
4. Run this command in project root to tell Alembic to make the Supabase database match the Models defined in the code: `alembic revision --autogenerate -m "create initial tables"`. Should see a new file under `alembic/versions` with create table scripts.
	- I had to make more changes to `alembic/env.py` to get it working, see that file for reference. I also had change Supabase to use Transaction Poller instead of Direct Connection.
5. Tell Supabase to actually create the tables by running `alembic upgrade head`. This runs the latest file in the `alembic/versions` folder and runs that scrip to create the tables. Can see the tables created in Alembic under the "Table Editor" section.

### Creating Local Test Database
1. Check if PostgreSQL is installed on computer using `psql --version` (I ran all these commands from root of project)
2. If not, install it
	1. `brew install postgresql@14`
	2. `brew services start postgresql@14`
3. `brew services list` should show 'started' in green
4. Create local db using `createdb matches_db`
5. In .env file, add this line: `DATABASE_URL=postgresql://localhost/football_db`
6. Follow instructions below for [Updating DB Using Alembic](#Updating%20DB%20Using%20Alembic)
7. Install TablePlus to view test database on Mac
	1. Go to [tableplus.com](https://tableplus.com/) and download and install the Mac version.
	2. Navigate to Create Connection, select PostgreSQL, enter the following details:
		1. Name: `Matches DB` (or whatever you want)
		2. Host: `127.0.0.1` (or `localhost`)
		3. Port: `5432`
		4. User: Your Mac username (leave blank if unsure)
		5. Password: (Leave blank if you didn't set one during `brew` install)
		6. Database: `matches_db`
		7. Click Connect, and you should see the tables / data
### Updating DB Using Alembic
1. Update `models.py`
2. From root of project, run `alembic revision --autogenerate -m "your_message"`
3. Run `alembic upgrade head`

## Resetting Alembic History and Rebuilding Database
### Step 1: Clear out the old version files

Delete everything inside your local `alembic/versions/` directory so Alembic completely forgets your broken migration history:

Bash

```
rm alembic/versions/*.py
```

### Step 2: Clear out the Supabase Database

Run the schema reset script in your **Supabase SQL Editor** to ensure there are zero tables, ghost indexes, or old tracking data left:

SQL

```
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO anon;
GRANT ALL ON SCHEMA public TO authenticated;
```

### Step 3: Generate the New Baseline Migration

Because your Supabase database is now completely empty, running the autogenerate command while pointing to it will force Alembic to look at your current Python models and write a single, clean file to build everything from scratch.

Run this in your Mac terminal **and ensure .env is pointed to Supabase DB**:

Bash

```
alembic revision --autogenerate -m "initial_schema_baseline"
```

Open this newly generated file inside `alembic/versions/`. You will see it contains a single `upgrade()` function that sequentially builds all your tables (`competitions`, `teams`, `matches`, `users`, `user_matches`) and sets up their constraints correctly in one shot.

### Step 4: Run the Migration

Execute the upgrade command to apply your clean baseline schema to Supabase:

Bash

```
alembic upgrade head
```


### Step 5. Wipe the local SQLite file

Since you are nuking the migration history files anyway, delete your local SQLite database file so it doesn't contain old tracking metadata:

Bash

```
rm test_db.sqlite
```

### Step 6. Sync your Local SQLite

Now, switch your `.env` file's `DATABASE_URL` back to your local SQLite path (`sqlite:///./test_db.sqlite`). Then, run the exact same upgrade command:

Bash

```
alembic upgrade head
```