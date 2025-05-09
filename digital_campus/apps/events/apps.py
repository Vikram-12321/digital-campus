"""
apps/events/apps.py

Configuration for the Events app. Registers app metadata with Django's app registry.

Author: Your Name or Team
Last updated: 2025-05-02
"""

from django.apps import AppConfig


class EventsConfig(AppConfig):
    """
    Django AppConfig for the Events app.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.events"
