"""
apps/search/apps.py

AppConfig for the `search` app.
Initializes the global search engine singleton on app startup.

Author: Vikram Bhojanala
Last updated: 2025-05-09
"""

import sys
from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError
import logging

logger = logging.getLogger(__name__)

class SearchConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.search"

    def ready(self):
        if 'manage.py' in sys.argv and 'runserver' not in sys.argv:
            return

        try:
            from .engine import initialize_engine
            from apps.posts.models import Post
            from django.contrib.auth import get_user_model

            initialize_engine(Post.objects.all(),
                              get_user_model().objects.all())
            logger.info("[SearchEngine] Index built successfully.")
        except (OperationalError, ProgrammingError) as e:
            logger.warning(f"[SearchEngine] Skipped init: {e}")
