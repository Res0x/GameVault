from django.urls import path

from . import views

app_name = 'library'

urlpatterns = [
    path('',
         views.LibraryEntryListView.as_view(),
         name='library_list'
         ),
    path('add/<slug:game_slug/',
         views.library_entry_add,
         name='library_entry_add'
         ),
    path(
        '<int:pk>/edit/',
        views.LibraryEntryUpdateView.as_view(),
        name='library_entry_edit',
    ),
]