1. Enter virtual environment using `source venv/bin/activate` from root folder
2. Test test-fetch endpoint
	1. From the backend folder, run the server using `uvicorn app.main:app --reload`
	2. Go to http://localhost:8000/api/test-fetch
		- Check the terminal output for match details
	- Go to http://127.0.0.1:8000/docs to see all endpoints and such and test their execution
3. To run pytest suite, enter `pytest` from root folder
	- To run a specific test, run the below from backend directory:
		- `python -m pytest tests/test_user_interactions.py -v`
4. Test sync_db.py
	1. From backend directory, run `python -m app.scripts.sync_db`
	2. Check results in Supabase and terminal output.
		1. Or if code is pointing to local testing DB, view data in TablePlus or by entering the below in terminal
	```
			psql matches_db 
			# Inside the prompt, run: SELECT * FROM matches LIMIT 5; 
			# To exit: \q
	```
