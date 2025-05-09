"""
apps/common/apps.py

AppConfig for the `common` app.
Initializes the global search engine singleton on app startup.

Author: Your Name or Team
Last updated: 2025-05-02
"""

import sys
from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError
from django.core.exceptions import AppRegistryNotReady # type: ignore


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.common"

    def ready(self):
        """
        Runs when Django starts. Initializes a global search engine
        instance by indexing all posts and users if data is available.

        Skips indexing during migrations and setup steps.
        """
        if 'manage.py' in sys.argv and 'runserver' not in sys.argv:
            return  # Skip during migration commands

        try:
            from .search_engine import SearchEngine
            from apps.posts.models import Post
            from django.contrib.auth import get_user_model

            engine = SearchEngine()

            posts = Post.objects.all()
            users = get_user_model().objects.all()

            if posts.exists() and users.exists():
                try:
                    engine.build_index(posts, users)
                except ValueError as e:
                    if "empty vocabulary" in str(e).lower():
                        print("[SearchEngine] Skipped: empty vocabulary (stop words only)")
                    else:
                        raise

            # Set global singleton access (optional pattern)
            sys.modules["apps.common.search_engine_instance"] = engine

        except (OperationalError, ProgrammingError, AppRegistryNotReady, ImportError):
            # Skip indexing if DB tables aren't ready or models are unavailable
            pass
