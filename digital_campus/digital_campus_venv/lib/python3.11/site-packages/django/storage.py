from django.conf import settings
print("🌍 STATICFILES_STORAGE:", getattr(settings, "STATICFILES_STORAGE", "<not set>"))

