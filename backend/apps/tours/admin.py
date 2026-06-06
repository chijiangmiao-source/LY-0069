from django.contrib import admin
from .models import TourTask, TourTaskVehicle, TourTaskProp, TourCostItem, TourSettlement


class TourTaskVehicleInline(admin.TabularInline):
    model = TourTaskVehicle
    extra = 0


class TourTaskPropInline(admin.TabularInline):
    model = TourTaskProp
    extra = 0


class TourCostItemInline(admin.TabularInline):
    model = TourCostItem
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TourTask)
class TourTaskAdmin(admin.ModelAdmin):
    list_display = [
        'program', 'performance_date', 'city', 'venue',
        'person_in_charge', 'status', 'execution_status', 'start_date', 'end_date'
    ]
    list_filter = ['status', 'execution_status', 'city']
    search_fields = ['program__name', 'city', 'venue', 'person_in_charge']
    inlines = [TourTaskVehicleInline, TourTaskPropInline, TourCostItemInline]


@admin.register(TourTaskVehicle)
class TourTaskVehicleAdmin(admin.ModelAdmin):
    list_display = ['tour_task', 'vehicle']
    list_filter = ['tour_task__city']
    search_fields = ['tour_task__program__name', 'vehicle__code']


@admin.register(TourTaskProp)
class TourTaskPropAdmin(admin.ModelAdmin):
    list_display = ['tour_task', 'prop', 'quantity']
    list_filter = ['tour_task__city']
    search_fields = ['tour_task__program__name', 'prop__code', 'prop__name']


@admin.register(TourCostItem)
class TourCostItemAdmin(admin.ModelAdmin):
    list_display = [
        'tour_task', 'cost_type', 'amount', 'expense_date',
        'operator', 'is_abnormal_cost'
    ]
    list_filter = ['cost_type', 'is_abnormal_cost', 'tour_task__city']
    search_fields = [
        'tour_task__program__name', 'description', 'operator', 'receipt_no'
    ]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TourSettlement)
class TourSettlementAdmin(admin.ModelAdmin):
    list_display = [
        'settlement_no', 'tour_task', 'total_cost',
        'settlement_status', 'settler', 'settlement_date'
    ]
    list_filter = ['settlement_status', 'tour_task__city']
    search_fields = [
        'settlement_no', 'tour_task__program__name', 'settler'
    ]
    readonly_fields = ['created_at', 'updated_at']
