"""
apps/common/apps.py

AppConfig for the `common` app.
Initializes the global search engine singleton on app startup.

Author: Vikram Bhojanala
Last updated: 2025-05-09
"""

import sys
import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)

class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.common"

    def ready(self):
        """
        Called on Django app startup.
        Initializes the global SearchEngine instance if database is ready.

        - Skips during migration/setup commands
        - Safely handles missing tables or empty data
        """
        # Avoid during migrate/makemigrations/shell/etc
        if 'manage.py' in sys.argv and 'runserver' not in sys.argv:
            return
