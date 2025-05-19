from django.urls import path
from .views import search, autocomplete


app_name = "search"

urlpatterns = [
    # ——— Search ———
    path("search/", search, name="search"),
    path("autocomplete/", autocomplete, name="autocomplete"),
]
