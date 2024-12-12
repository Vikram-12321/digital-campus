from django.urls import path
from .import views

urlpatterns = [
    path("", views.home, name='uoft-social-app-home'),
    path("about/", views.about, name='uoft-social-app-about'),
    path("account/", views.account, name='uoft-social-app-account'),
]