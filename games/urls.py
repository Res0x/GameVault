from django.urls import path

from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('games/', views.game_list, name='game_list'),
    path('ratings/', views.ratings, name='ratings'),
    path('games/add/', views.game_create, name='game_create'),
    path(
        'games/<slug:game_slug>/',
        views.game_detail,
        name='game_detail',
    ),
]