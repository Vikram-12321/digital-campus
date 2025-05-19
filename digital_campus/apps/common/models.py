"""
apps/common/models.py

Defines shared models used across the platform:
- Course: for academic tagging and autocomplete

Author: Vikram Bhojanala
Last updated: 2025-05-02
"""

## Models Imports
from django.db import models

# ————————————————————————————————————
# Course Model (e.g., for user-tagged courses or filtering)
# ————————————————————————————————————
class Course(models.Model):
    name = models.CharField(max_length=255)
    session = models.CharField(max_length=255)

    def __str__(self):
        return self.name
