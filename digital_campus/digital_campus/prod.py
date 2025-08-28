"""
Production settings for Digital Campus
Only overrides / adds differences vs. settings.py
"""

from .settings import *          # pull in EVERYTHING from the default file
import dj_database_url, os

DEBUG = False
ALLOWED_HOSTS = [
    "digitalcampustoronto.ca",
    "www.digitalcampustoronto.ca",
]

# Postgres via DATABASE_URL
DATABASES = {
    "default": dj_database_url.config(
        env="DATABASE_URL",
        conn_max_age=600,
        ssl_require=True,
    )
}

CSRF_TRUSTED_ORIGINS = ["https://*.digitalcampustoronto.ca"]

# (any other prod-only settings…)
