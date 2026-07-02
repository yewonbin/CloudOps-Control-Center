# backend — FastAPI service (Phase 1)

Task management API with JWT auth, backed by PostgreSQL.

## Layout

```
app/
├─ main.py            app factory, /health, router wiring, table creation
├─ core/
│  ├─ config.py       settings (env / .env)
│  ├─ db.py           engine, session, Base, get_db
│  └─ security.py     password hashing + JWT
├─ models/            SQLAlchemy: User, Task
├─ schemas/           Pydantic: user, task, token
└─ api/
   ├─ deps.py         get_current_user (OAuth2 bearer)
   ├─ auth.py         POST /register, POST /login
   └─ tasks.py        Task CRUD + /complete
```

## Endpoints

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET  | `/health` | – | liveness probe |
| POST | `/api/v1/auth/register` | – | create user |
| POST | `/api/v1/auth/login` | – | get JWT (form: `username`=email, `password`) |
| GET  | `/api/v1/me` | ✅ | current user |
| GET  | `/api/v1/tasks` | ✅ | list (optional `?status=`) |
| POST | `/api/v1/tasks` | ✅ | create |
| GET  | `/api/v1/tasks/{id}` | ✅ | read |
| PATCH| `/api/v1/tasks/{id}` | ✅ | partial update |
| POST | `/api/v1/tasks/{id}/complete` | ✅ | mark done |
| DELETE | `/api/v1/tasks/{id}` | ✅ | delete |

## Run

From the repo root:

```bash
docker compose up --build
```

Then open http://localhost:8000/docs.

## Smoke test (curl)

```bash
BASE=http://localhost:8000/api/v1

# register
curl -sX POST $BASE/auth/register -H 'Content-Type: application/json' \
  -d '{"email":"ops@example.com","password":"supersecret"}'

# login -> token
TOKEN=$(curl -sX POST $BASE/auth/login \
  -d 'username=ops@example.com&password=supersecret' | python -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')

# create a task
curl -sX POST $BASE/tasks -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"title":"Set up Nginx reverse proxy"}'

# list
curl -s $BASE/tasks -H "Authorization: Bearer $TOKEN"
```

## Notes / next phases

- Tables are created on startup via `Base.metadata.create_all`. **Alembic** migrations
  come with a later phase.
- A `/metrics` endpoint for **Prometheus** is added in Phase 7.
- CORS is currently wide open for dev; tightened once the React frontend exists.
