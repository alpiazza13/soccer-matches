1. Enter virtual environment using `source venv/bin/activate` from root folder
2. From the backend folder, run the server using `uvicorn app.main:app --reload`
3. Go to http://localhost:8000/api/test-fetch
4. Check the terminal output for match details
5. To run pytest suite, enter `pytest` from root folder