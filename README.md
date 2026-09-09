# Calisfy

A calisthenics training, skill-progression, athlete-profile, ranking, and
community platform. Built with **Django** because it gets you a working,
deployable MVP fastest in Python — auth, ORM, migrations, and a full **admin
panel** all come for free, which covers a large chunk of this spec without
writing custom code for it.

## Stack

- Django 6.1 (backend + templated frontend)
- SQLite for local development, PostgreSQL for production (via `DATABASE_URL`)
- Tailwind CSS (via CDN, no build step)
- WhiteNoise for static file serving
- Gunicorn as the production WSGI server

## What's implemented (MVP scope)

- **Auth**: signup, login (remember-me), logout, password reset, short onboarding
- **Athlete profiles**: public profile (rank, XP, verified skills, achievements,
  followers), private account settings, edit profile
- **Skill tree**: categories, skills with prerequisites/progressions and
  admin-configurable difficulty — nothing hard-coded in application logic
- **Skill verification**: status lifecycle (not started → learning →
  self-recorded → pending → verified), video upload, admin review workbench.
  A skill is **never** auto-verified by selecting it.
- **Training**: programs, workouts, workout player, session tracking, XP on
  completion
- **Rank Engine** (`ranking/services.py`): recalculates rank from XP + verified
  skill count + skill difficulty score. Rank is never stored as ground truth —
  it's recomputed from raw signals, so you can change the formula/thresholds
  (in the admin, via the `Rank` model) without a migration.
- **Community**: posts, likes, comments, reporting/moderation queue
- **Leaderboard**: ranked by cached XP/skill score, not followers
- **Admin panel**: `/admin/` — manage skills, review verification videos,
  configure rank thresholds and XP rules, moderate reports

## Stubbed for a later version (per the product spec itself)

AI video verification, challenges, in-app notification delivery UI (the
`Notification` model exists), advanced analytics, social login (Google/Apple/
GitHub), country-based leaderboards.

## Local setup

```bash
python3 -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_calisfy   # loads skill tree, ranks, a sample program & achievements
python manage.py createsuperuser

python manage.py runserver
```

Visit `http://127.0.0.1:8000/` for the app and `/admin/` for the admin panel.

A demo superuser is pre-created in this build:
- username: `admin`
- password: `Calisfy@2026`
**Change this password immediately if you deploy this as-is.**

## Project layout

```
calisfy/
├── accounts/     # User + AthleteProfile, auth views, profile pages, follow
├── skills/       # Skill tree, verification requirements & workflow
├── training/     # Programs, workouts, sessions, exercise logs
├── ranking/      # XP ledger, Rank Engine, Achievements
├── community/    # Posts, likes, comments, reports, notifications
├── core/         # Landing page + personalized dashboard
└── templates/    # Dark-athletic Tailwind UI, one folder per app
```

## Going live (free/cheap options)

### Option A — Render.com (recommended, has a free web service tier)

1. Push this project to a GitHub repo.
2. On Render: **New → Web Service**, connect the repo.
3. Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
4. Start command: `gunicorn calisfy_project.wsgi`
5. Add a **PostgreSQL** instance (Render → New → PostgreSQL, free tier) and copy
   its internal `DATABASE_URL` into your web service's environment variables.
6. Set these environment variables on the web service:
   - `DJANGO_SECRET_KEY` — generate one (e.g. `python -c "import secrets; print(secrets.token_urlsafe(50))"`)
   - `DJANGO_DEBUG=False`
   - `DJANGO_ALLOWED_HOSTS=your-app.onrender.com`
   - `DJANGO_CSRF_TRUSTED_ORIGINS=https://your-app.onrender.com`
   - `DATABASE_URL` — from step 5
7. After first deploy, open the Render shell and run:
   ```bash
   python manage.py migrate
   python manage.py seed_calisfy
   python manage.py createsuperuser
   ```
8. Your app is now live at `https://your-app.onrender.com`.

### Option B — Railway.app

Same idea: deploy from GitHub, attach a Postgres plugin (Railway sets
`DATABASE_URL` automatically), set the same environment variables as above,
and use `gunicorn calisfy_project.wsgi` as the start command.

### Media/video storage note

Verification videos and post media currently save to local disk
(`MEDIA_ROOT`). Most hosts (Render, Railway) use **ephemeral filesystems** —
uploaded files disappear on redeploy. For a real production launch, swap
`MEDIA` storage for an S3-compatible bucket (e.g. via `django-storages` +
Cloudflare R2/AWS S3) before you rely on video verification at scale. This is
a small, contained change (one settings block + one pip install) and doesn't
touch any of the app logic above it.

## Extending the skill tree / ranks / programs

Everything content-related (skills, categories, prerequisites, difficulty
scores, verification instructions, rank thresholds, programs, workouts,
exercises, achievements) is managed through `/admin/` — no code changes
needed to add a new skill or rebalance ranks. `skills/management/commands/seed_calisfy.py`
shows the shape of that data if you want to bulk-load more via a script instead.
