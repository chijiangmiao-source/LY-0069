from django.contrib import admin
from .models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('code', 'model', 'capacity', 'current_load', 'status', 'driver', 'created_at')
    list_filter = ('status',)
    search_fields = ('code', 'model', 'driver')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('code', 'model', 'capacity', 'current_load')}),
        ('状态信息', {'fields': ('status', 'driver')}),
        ('时间信息', {'fields': ('created_at', 'updated_at')}),
    )
