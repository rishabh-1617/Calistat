# Calisfy

Calisfy is a calisthenics platform for skill progression, workout programming,
athlete rankings, and community activity. It combines Django's data and
administration features with a FastAPI ASGI application for the deployed web
pages and JSON API.

**Live app:** https://calisfy.onrender.com

**API health:** https://calisfy.onrender.com/api/health

**Interactive API documentation:** https://calisfy.onrender.com/docs

**Alternative API documentation:** https://calisfy.onrender.com/redoc

## Technology

- **Python 3.13** — deployment runtime configured in `render.yaml`.
- **Django 6.1** — ORM, models, migrations, authentication components, admin,
  management commands, and Django template rendering.
- **FastAPI 0.165** — ASGI application, JSON endpoints, health check, and the
  deployed HTML page routes.
- **Uvicorn 0.54** — ASGI server used by the local FastAPI command and Render.
- **Pydantic 2** — response and request schemas for the API.
- **asgiref** — `sync_to_async` bridge for Django ORM access from async routes.
- **SQLite** — default database for local development. PostgreSQL can be
  selected by setting `DATABASE_URL`; `dj-database-url` parses the URL.
- **Django templates, HTML, CSS, and JavaScript** — server-rendered interface.
- **Tailwind CSS via CDN** — utility styling; no frontend build step.
- **WhiteNoise** — static file middleware and compressed manifest storage.
- **Pillow** — image handling for uploaded media.
- **Render** — current deployment platform; deployment settings are in
  `render.yaml`.

The exact pinned Python dependencies are listed in `requirements.txt`.

## Features

- Account signup, login, onboarding, profile editing, and password reset in
  the Django application.
- Athlete profiles with bios, avatars, followers, and training/ranking data.
- Admin-managed skill categories, prerequisites, progressions, difficulty,
  technique instructions, and verification workflow.
- Workout programs, workouts, exercises, workout history, and session logging.
- XP, configurable rank tiers, achievements, leaderboard, and analytics pages.
- Community posts, likes, comments, notifications, and moderation/reporting.
- Django admin for managing application data when running the Django URL
  configuration.

## Application entry points

There are two server entry points in this repository:

1. **FastAPI (`main:app`)** is the Render deployment. It exposes the API and
   the FastAPI web routes listed below. On startup, it runs Django migrations
   and seeds the skill data if the database has no skills.
2. **Django (`manage.py runserver`)** serves the Django URL configuration,
   including Django admin and the Django account/workflow routes, for local
   development.

The current Render command runs `main:app`; it does not mount Django's full
URL configuration. Consequently, Django-only routes such as `/admin/` and
`/accounts/` are not exposed by the deployed FastAPI app.

## Web pages

The FastAPI application serves these page routes:

| Route | Page |
|---|---|
| `/` | Dashboard |
| `/skills/` | Skill list |
| `/skills/{slug}/` | Skill detail |
| `/training/` | Program list |
| `/training/programs/` | Program list |
| `/training/programs/{id}/` | Program detail |
| `/training/workouts/{id}/player/` | Workout player |
| `/ranking/` | Leaderboard |
| `/community/` | Community feed |

The Django URL configuration includes `/admin/`, `/accounts/`, `/skills/`,
`/training/`, `/community/`, and `/leaderboard/`.

## JSON API

FastAPI's interactive schema is available at `/docs` and `/redoc`.

| Method | Route | Description |
|---|---|---|
| `GET` | `/api/health` | Service health and version |
| `GET` | `/api/skills/categories` | Skill categories |
| `GET` | `/api/skills` | Skills; optional `category`, `difficulty`, and `search` filters |
| `GET` | `/api/skills/{slug}` | Skill instructions and progression data |
| `GET` | `/api/exercises` | Exercises; optional `search` and `muscle` filters |
| `GET` | `/api/exercises/{exercise_id}` | Exercise details |
| `GET` | `/api/training/programs` | Programs, workouts, and exercises |
| `GET` | `/api/training/workouts/{workout_id}` | Workout details |
| `POST` | `/api/training/workouts/{workout_id}/log` | Record a workout session |
| `GET` | `/api/ranking/ranks` | Rank tiers |
| `GET` | `/api/ranking/leaderboard` | Leaderboard |
| `GET` | `/api/community/posts` | Recent visible community posts |

## Local development

Use Python 3.13 to match the Render configuration.

### Windows PowerShell

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_calisfy
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/` for the Django application and
`http://127.0.0.1:8000/admin/` for Django admin.

To run the FastAPI app instead, stop the Django server and run:

```powershell
python -m uvicorn main:app --reload
```

Then open `http://127.0.0.1:8000/docs` for the API explorer or visit
`http://127.0.0.1:8000/api/health`.

### macOS/Linux

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_calisfy
python manage.py createsuperuser
python manage.py runserver
```

## Configuration

| Variable | Purpose | Default / local behavior |
|---|---|---|
| `DJANGO_SECRET_KEY` | Django cryptographic signing key | Development fallback only; set a unique secret in production |
| `DJANGO_DEBUG` | Enables Django debug mode only when the value is `True` | `True` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated Django host names | `localhost,127.0.0.1,testserver` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Comma-separated trusted origins for Django CSRF | Empty |
| `DATABASE_URL` | Optional database URL; parsed by `dj-database-url` | SQLite at `db.sqlite3` |
| `PORT` | HTTP port supplied by the deployment platform | `8000` locally |

Generate a production Django secret locally with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Set the generated value as `DJANGO_SECRET_KEY` in the hosting provider's secret
environment-variable settings. Do not commit the value to the repository.

## Deploying to Render

The repository includes a Render Blueprint in `render.yaml`:

- Runtime: Python
- Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
- Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Python version: `3.13.0`
- Debug: disabled

To deploy:

1. In Render, create a Blueprint or Web Service from this GitHub repository
   and select the `main` branch.
2. For a manual Web Service, use the build and start commands above and leave
   the root directory blank.
3. Set `DJANGO_SECRET_KEY` to a newly generated secret in Render's environment
   settings. Configure `DJANGO_ALLOWED_HOSTS` to the service hostname when
   possible.
4. Choose an instance plan, then deploy. Render auto-deploys later commits
   when auto-deploy is enabled.
5. Verify the service at `/api/health`.

The current configuration uses SQLite unless `DATABASE_URL` is set. Render's
local service filesystem is not a substitute for a persistent database; use a
managed PostgreSQL database for data that must survive service restarts and
redeploys, and set its connection URL as `DATABASE_URL`. Uploaded media is
also stored locally under `MEDIA_ROOT` and needs persistent or object storage
for production use.

## Project layout

```text
accounts/          Django users, profiles, and account views
calisfy_project/   Django settings, URLs, and WSGI/ASGI configuration
community/         Posts, comments, likes, notifications, and moderation
core/              Landing page, dashboard, and shared context
fastapi_app/       FastAPI app, Pydantic schemas, API and web routers
ranking/           Rank models, XP services, leaderboard, and analytics
skills/            Skill tree, verification, and seed command
templates/         Django HTML templates
training/          Programs, workouts, exercises, sessions, and challenges
static/            CSS, JavaScript, and source image assets
render.yaml        Render deployment Blueprint
requirements.txt   Pinned Python dependencies
main.py            FastAPI ASGI entry point (`main:app`)
manage.py          Django management entry point
```

## Data seeding and administration

`python manage.py seed_calisfy` loads the initial skill tree, exercises,
programs, ranks, and achievements. The FastAPI startup lifecycle also runs
migrations and invokes this command when the database contains no skills.

For local Django development, create an administrator with
`python manage.py createsuperuser` and manage application data at `/admin/`.
No demo username or password is provided in this README.
