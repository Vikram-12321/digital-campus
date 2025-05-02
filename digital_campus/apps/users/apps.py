from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'

    def ready(self):
        # Import signals to register them
        import apps.users.signals  # Noqa (flake8 ignore)
