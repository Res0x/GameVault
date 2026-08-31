from django.urls import path

from .views import ReviewCreateView


app_name = 'reviews'

urlpatterns = [
    path(
        '<slug:game_slug>/',
        ReviewCreateView.as_view(),
        name='review_create'
    )
]