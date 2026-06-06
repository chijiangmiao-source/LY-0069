from django.contrib import admin
from .models import Program


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)
