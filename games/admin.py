from django.contrib import admin

from .models import Game, GameHighlight


class GameHighlightInline(admin.TabularInline):
    model = GameHighlight
    fields = (
        'text',
        'position'
    )
    extra = 1

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    inlines = (
        GameHighlightInline,
    )
    list_display = (
        'id',
        'title',
        'genre',
        'platform',
        'developer',
        'release_year',
        'rating',
        'status',
    )

    search_fields = (
        'title',
        'genre',
        'developer',
    )

    list_filter = (
        'platform',
        'release_year',
        'status',
    )

    prepopulated_fields = {'slug': ('title',)}
    empty_value_display = 'Не указано'
