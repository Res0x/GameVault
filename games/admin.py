from django.contrib import admin

from .models import Game


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'genre',
        'platform',
        'developer',
        'release_year',
        'rating',
    )

    search_fields = (
        'title',
        'genre',
        'developer',
    )

    ordering = ('-release_year', 'title')

    list_filter = (
        'platform',
        'release_year',
    )

    prepopulated_fields = {'slug': ('title',)}
    empty_value_display = 'Не указано'