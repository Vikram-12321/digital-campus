from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError
from django.core.exceptions import AppRegistryNotReady

class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.common"
    
    def ready(self):
        # Skip if running management commands that don't need this
        import sys
        if 'manage.py' in sys.argv and 'runserver' not in sys.argv:
            return
            
        try:
            from .search_engine import SearchEngine
            from apps.posts.models import Post
            from django.contrib.auth import get_user_model
            
            engine = SearchEngine()
            
            # Only build index if there's actual content
            posts = Post.objects.all()
            users = get_user_model().objects.all()
            
            if posts.exists() and users.exists():
                try:
                    engine.build_index(posts, users)
                except ValueError as e:
                    if "empty vocabulary" in str(e):
                        print("Warning: Not building search index - empty content or only stop words")
                    else:
                        raise
                
            # Store global instance
            import sys
            sys.modules["apps.common.search_engine_instance"] = engine
            
        except (OperationalError, ProgrammingError, AppRegistryNotReady, ImportError):
            # Skip during setup or if models aren't ready
            pass