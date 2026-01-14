1. Install node using `brew install node`
2. Initialize project by running, from root of project, command `npx create-next-app@latest frontend`. Select Use recommended defaults when prompted. Options to select:
3. Add code to main.py in backend so backend can receive requests from frontend
	```python
	
	from fastapi.middleware.cors import CORSMiddleware
	
	#right under app = FastAPI() line
	app.add_middleware(

		CORSMiddleware,
		
		allow_origins=["http://localhost:3000"],
		
		allow_credentials=True,
		
		allow_methods=["*"],
		
		allow_headers=["*"],

)
	```
	
4. Create `.env.local` file in root of `frontend` folder, add `NEXT_PUBLIC_API_URL=http://localhost:8000`
5. Start writing typescript code
6. In frontend folder, run `npm install lucide-react`
7. Packages installed through `npm` are added to `package.json` file. Run `npm install` to install all of them if starting dev work on a new machine.