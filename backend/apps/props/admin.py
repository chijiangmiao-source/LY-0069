from django.contrib import admin
from .models import Prop


@admin.register(Prop)
class PropAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'program_id', 'status', 'location', 'created_at')
    list_filter = ('status', 'program_id')
    search_fields = ('code', 'name', 'material', 'location')
    readonly_fields = ('created_at', 'updated_at')
