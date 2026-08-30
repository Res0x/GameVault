from django.contrib import admin

from reviews.models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'game', 'title', 'contains_spoilers', 'created_at')
    list_filter = ('contains_spoilers', 'created_at')
    search_fields = ('author__username', 'game__title', 'title')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)