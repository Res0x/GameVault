from django.contrib import admin

from .models import Game, GameHighlight, Feature


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
        'added_by',
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
        'added_by',
    )

    filter_horizontal = (
        'features',
    )

    prepopulated_fields = {'slug': ('title',)}
    empty_value_display = 'Не указано'

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug'
    )

    search_fields = (
        'name',
    )

    prepopulated_fields = {'slug': ('name',)}
