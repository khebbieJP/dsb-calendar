in this project we use beads for task management run `bd quickstart` to understand how it works.

We use mise en place to run tasks and for dependency management.

Always ensure tests are green and kept up to date.
We do not test details of the implementation but the outer interfaces.
If the application was once in a state and you change it, we do not need to know how it was before, or the changes you made - they are in git.
We only document the current state.

ensure you use python virtual environments to maintain a stable environment.

## Key Learnings

### Testing Web Applications
- Always verify HTTP status codes, not just output
- Create automated tests for manual operations (curl commands → test cases)
- Run `mise run test` after changes to verify nothing broke

### Mise Task Dependencies
- Use `depends = ["install"]` for tasks that require dependencies
- This prevents "module not found" errors
- Dependencies run automatically before the task

### Flask Application Structure
- Templates go in `templates/` at root level (next to app.py)
- Static files go in `static/` at root level
- Flask looks for these directories relative to the Flask app instance

### Temporary File Management
- Use dedicated temp directories (not project root)
- Use `tempfile.NamedTemporaryFile` for unique names
- Clean up in `finally` blocks with error handling
- Use `BytesIO` for in-memory responses when possible

### Port Management on macOS
- Port 5000 often used by AirPlay Receiver
- Port 8000 commonly in use
- Use `FLASK_PORT=3000` or similar to specify alternative ports

### Beads Task Management
- Use `bd` commands, not TodoWrite tool
- `.beads/` directory is local and should be in .gitignore
- Run `bd list` to see current issues
- Run `bd ready` to see unblocked work

### Test Coverage
- Test both API endpoints (Flask) and core functionality (business logic)
- Separate test files for different concerns (test_api.py vs test_dsb_to_ics.py)
- Use Flask test client for API tests (no need to run server)
