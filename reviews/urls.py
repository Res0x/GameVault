from django.urls import path

from .views import *


app_name = 'reviews'

urlpatterns = [
    path(
        '<slug:game_slug>/',
        ReviewCreateView.as_view(),
        name='review_create'
    ),
    path(
        '<int:pk>/edit',
        ReviewUpdateView.as_view(),
        name='review_edit'
    ),
    path(
        '<int:pk>/delete',
        ReviewDeleteView.as_view(),
        name='review_delete'
    ),
]