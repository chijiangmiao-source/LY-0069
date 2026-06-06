from django.contrib import admin
from .models import TourTask, TourTaskVehicle, TourTaskProp


class TourTaskVehicleInline(admin.TabularInline):
    model = TourTaskVehicle
    extra = 0


class TourTaskPropInline(admin.TabularInline):
    model = TourTaskProp
    extra = 0


@admin.register(TourTask)
class TourTaskAdmin(admin.ModelAdmin):
    list_display = [
        'program', 'performance_date', 'city', 'venue',
        'person_in_charge', 'status', 'execution_status', 'start_date', 'end_date'
    ]
    list_filter = ['status', 'execution_status', 'city']
    search_fields = ['program__name', 'city', 'venue', 'person_in_charge']
    inlines = [TourTaskVehicleInline, TourTaskPropInline]


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
