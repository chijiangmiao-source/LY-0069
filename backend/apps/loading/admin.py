from django.contrib import admin
from .models import LoadingRecord, UnloadingRecord, DamageRecord


@admin.register(LoadingRecord)
class LoadingRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehicle', 'prop', 'loading_date', 'loading_quantity', 'operator', 'created_at')
    list_filter = ('loading_date',)
    search_fields = ('vehicle__code', 'prop__code', 'prop__name', 'operator')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {'fields': ('vehicle', 'prop', 'loading_date', 'loading_quantity')}),
        ('操作信息', {'fields': ('operator', 'remark')}),
        ('时间信息', {'fields': ('created_at',)}),
    )


@admin.register(UnloadingRecord)
class UnloadingRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'loading', 'vehicle', 'prop', 'unloading_date', 'unloading_quantity', 'operator', 'created_at')
    list_filter = ('unloading_date',)
    search_fields = ('vehicle__code', 'prop__code', 'prop__name', 'operator')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {'fields': ('loading', 'vehicle', 'prop', 'unloading_date', 'unloading_quantity')}),
        ('操作信息', {'fields': ('operator', 'remark')}),
        ('时间信息', {'fields': ('created_at',)}),
    )


@admin.register(DamageRecord)
class DamageRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'prop', 'damage_date', 'damage_quantity', 'damage_reason', 'handler', 'created_at')
    list_filter = ('damage_date',)
    search_fields = ('prop__code', 'prop__name', 'damage_reason', 'handler')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {'fields': ('prop', 'damage_date', 'damage_quantity', 'damage_reason')}),
        ('操作信息', {'fields': ('handler', 'remark')}),
        ('时间信息', {'fields': ('created_at',)}),
    )
