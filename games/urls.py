from django.urls import path

from . import views

app_name = 'games'

urlpatterns = [
    path('', views.home, name='home'),
    path('games/', views.GameListView.as_view(), name='game_list'),
    path('ratings/', views.ratings, name='ratings'),
    path('games/add/', views.GameCreateView.as_view(), name='game_create'),
    path('games/latest/', views.latest_game, name='latest_game'),
    path('games/year/<int:release_year>/', views.games_by_year, name='games_by_year'),
    path(
        'games/<slug:game_slug>/',
        views.GameDetailView.as_view(),
        name='game_detail',
    ),
    path(
        'games/<slug:game_slug>/edit/',
        views.GameUpdateView.as_view(),
        name='game_edit',
    ),
    path(
        'games/<slug:game_slug>/delete/',
        views.GameDeleteView.as_view(),
        name='game_delete',
    ),

]