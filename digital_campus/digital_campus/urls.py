"""
URL configuration for digital_campus project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include(('apps.common.urls', 'common'), namespace='common')),
    path('', include('apps.chat.urls')),
    path('', include('apps.users.urls')), 
    path('', include(('apps.events.urls', 'events'), namespace='events')),
    path('', include(('apps.clubs.urls', 'clubs'), namespace='clubs')),
    path('', include(('apps.posts.urls', 'posts'), namespace='posts')),
    path('', include(("apps.search.urls", 'search'), namespace = 'search')),
    path('', include(("apps.connections.urls", 'connections'), namespace = 'connections')),
    path('', include(("apps.notifications.urls", 'notifications'), namespace = 'notifications')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
