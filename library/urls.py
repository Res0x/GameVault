from django.urls import path

from . import views

app_name = 'library'

urlpatterns = [
    path('',
         views.LibraryEntryListView.as_view(),
         name='library_list'
         ),
]