# PlayLog

PlayLog is a FastAPI project backed by SQLite, SQLAlchemy/SQLModel, and Alembic.

## Project setup from scratch

### 1. Create a virtual environment

Use Python's built-in `venv` module. Some older guides refer to this as `pyvenv`, but `python3 -m venv` is the current command.

```bash
python3 -m venv .venv
```

### 2. Activate the virtual environment

On macOS or Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

Upgrade `pip` first, then install the project requirements.

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Database setup with Alembic

Apply the latest migrations to create the SQLite database and all tables:

```bash
alembic upgrade head
```

This creates or updates the local database file at `playlog.db` in the project root.

To check the currently applied revision:

```bash
alembic current
```

## Run the application

This project runs with FastAPI and Uvicorn.

```bash
uvicorn app.main:app --reload
```

By default, the API will be available at:

```text
http://127.0.0.1:8000
```

## Swagger API docs

Once the server is running, open the Swagger UI at:

```text
http://127.0.0.1:8000/docs
```

FastAPI also exposes the ReDoc page at:

```text
http://127.0.0.1:8000/redoc
```

## Main API flow for the frontend

### Log a game for a user

```http
POST /api/v1/users/{username}/games/log
```

Example request body:

```json
{
	"title": "Expedition 33",
	"hours_played": 70,
	"finished_at": "2026-03-24",
	"genre": {
		"name": "JRPG",
		"description": "Japanese role-playing game"
	}
}
```

### List a user's logged games

```http
GET /api/v1/users/{username}/games
```

### Get one logged game

```http
GET /api/v1/users/{username}/games/{title}
```

### Update a logged game

```http
PUT /api/v1/users/{username}/games/{title}
```

Example request body:

```json
{
	"hours_played": 78,
	"finished_at": "2026-03-24"
}
```

### Delete a logged game

```http
DELETE /api/v1/users/{username}/games/{title}
```

### Get total hours played for a user

```http
GET /api/v1/users/{username}/stats/total-hours
```

Example response:

```json
{
	"username": "daniel",
	"total_hours_played": 148
}
```

### Get top played games for a user

```http
GET /api/v1/users/{username}/stats/top-games?limit=5
```

Example response:

```json
{
	"username": "daniel",
	"games": [
		{
			"title": "Expedition 33",
			"hours_played": 70,
			"finished_at": "2026-03-24"
		},
		{
			"title": "Metaphor ReFantazio",
			"hours_played": 55,
			"finished_at": null
		}
	]
}
```

## Run the tests

This project uses `pytest` with async test support enabled through [pytest.ini](pytest.ini).

Run the full test suite:

```bash
pytest tests/ -v
```

Run only the service-layer tests:

```bash
pytest tests/test_services/ -v
```

Run only the integration tests:

```bash
pytest tests/integration/ -v
```

Run the game-related tests only:

```bash
pytest tests/test_services/test_game_service.py tests/integration/test_game.py -v
```

There is also a more detailed game testing note in [GAME_TESTS_README.md](GAME_TESTS_README.md).

## Full setup summary

If you want the full setup flow in one sequence:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

