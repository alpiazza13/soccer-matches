1. Download Obsidian
2. Create soccer-matches folder on local desktop, navigate into it and enter `git init` command
3. Download Cursor and open soccer-matches project.
4. Tell Cursor to create `.gitignore`. Prompt used:
	> "Create a professional .gitignore file for a Python FastAPI and Next.js project. Also include a rule to ignore the .obsidian/ folder."
5. Create `docs` folder and `project_outline.md` file.
6. Setup Github CLI:
	1. Install Github CLI by entering `brew install gh` in terminal
	2. Run ` gh auth login`. Choose HTTPS for authentication.
7. Run `gh repo create soccer-matches --public --source=. --remote=origin --push` to create remote repo and push to it.