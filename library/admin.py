from django.contrib import admin

from .models import LibraryEntry

@admin.register(LibraryEntry)
class LibraryEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'status', 'rating', 'is_favourite')
    list_filter = ('status', 'is_favourite')
    search_fields = ('user__username', 'game__title')
    readonly_fields = ('created_at', 'updated_at')