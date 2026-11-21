import os

# Gunicorn configuration file for Render / Linux production
port = os.environ.get("PORT", "8000")
bind = f"0.0.0.0:{port}"
workers = int(os.environ.get("WEB_CONCURRENCY", "1"))
worker_class = "uvicorn.workers.UvicornWorker"
wsgi_app = "app:app"
