from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('library/', include('library.urls')),
    path('', include('games.urls')),
    path('reviews/', include('reviews.urls')),
]

handler404 = 'gamevault_project.errors.page_not_found'