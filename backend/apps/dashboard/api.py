from ninja import Router
from django.db.models import Count, Sum, Q
from datetime import date, timedelta

from .schemas import (
    DashboardData, VehicleLoadRate, ProgramPropDist, TourFlowStats,
    MaintenanceStats, HighLossProgram, TourTaskStats, ProgramScheduleRank
)
from apps.auth_app.auth import JWTAuth
from apps.vehicles.models import Vehicle
from apps.props.models import Prop

router = Router(tags=['数据看板'], auth=JWTAuth())


try:
    from apps.loading.models import LoadingRecord, UnloadingRecord, DamageRecord
except ImportError:
    LoadingRecord = None
    UnloadingRecord = None
    DamageRecord = None

try:
    from apps.tours.models import TourTask
except ImportError:
    TourTask = None


@router.get('', response=DashboardData)
def get_dashboard_data(request):
    vehicle_load_rates = []
    vehicles = Vehicle.objects.all()
    for vehicle in vehicles:
        load_rate = 0.0
        if vehicle.capacity > 0:
            load_rate = round(vehicle.current_load / vehicle.capacity * 100, 2)
        vehicle_load_rates.append(VehicleLoadRate(
            vehicle_code=vehicle.code,
            model=vehicle.model,
            capacity=vehicle.capacity,
            current_load=vehicle.current_load,
            load_rate=load_rate,
        ))

    program_prop_dist = []
    prop_counts = Prop.objects.values('program_id__name').annotate(count=Count('id')).order_by('-count')
    for item in prop_counts:
        program_prop_dist.append(ProgramPropDist(
            program_name=item['program_id__name'] or '未分类',
            prop_count=item['count'],
        ))

    total_loading_count = 0
    total_unloading_count = 0
    total_tour_count = 0

    if LoadingRecord is not None:
        try:
            total_loading_count = LoadingRecord.objects.count()
        except Exception:
            pass

    if UnloadingRecord is not None:
        try:
            total_unloading_count = UnloadingRecord.objects.count()
        except Exception:
            pass

    if LoadingRecord is not None:
        try:
            total_tour_count = LoadingRecord.objects.count()
        except Exception:
            pass

    tour_flow_stats = TourFlowStats(
        total_loading_count=total_loading_count,
        total_unloading_count=total_unloading_count,
        total_tour_count=total_tour_count,
    )

    today = date.today()
    seven_days_later = today + timedelta(days=7)
    maintenance_due_count = Prop.objects.filter(
        next_maintenance_date__isnull=False,
        next_maintenance_date__lte=seven_days_later,
        next_maintenance_date__gte=today,
        scrap_status__in=['active', 'pending']
    ).count()
    maintenance_overdue_count = Prop.objects.filter(
        next_maintenance_date__isnull=False,
        next_maintenance_date__lt=today,
        scrap_status__in=['active', 'pending']
    ).count()
    total_props = Prop.objects.count()
    scrapped_count = Prop.objects.filter(scrap_status__in=['scrapped', 'approved']).count()
    scrap_proportion = round(scrapped_count / total_props * 100, 2) if total_props > 0 else 0.0

    maintenance_stats = MaintenanceStats(
        maintenance_due_count=maintenance_due_count,
        maintenance_overdue_count=maintenance_overdue_count,
        scrap_proportion=scrap_proportion,
    )

    high_loss_programs = []
    if DamageRecord is not None:
        try:
            loss_stats = DamageRecord.objects.values(
                'prop__program_id__name'
            ).annotate(
                total_damage_quantity=Sum('damage_quantity'),
                damage_count=Count('id')
            ).order_by('-total_damage_quantity')[:10]

            for item in loss_stats:
                program_name = item['prop__program_id__name'] or '未分类'
                prop_count = Prop.objects.filter(program_id__name=program_name).count()
                high_loss_programs.append(HighLossProgram(
                    program_name=program_name,
                    total_damage_quantity=item['total_damage_quantity'] or 0,
                    prop_count=prop_count,
                ))
        except Exception:
            pass

    future_tasks_count = 0
    in_progress_tasks_count = 0
    abnormal_tasks_count = 0
    program_schedule_rank = []

    if TourTask is not None:
        try:
            future_tasks_count = TourTask.objects.filter(
                status__in=['pending', 'in_progress'],
                start_date__gte=today
            ).count()
            in_progress_tasks_count = TourTask.objects.filter(status='in_progress').count()
            abnormal_tasks_count = TourTask.objects.filter(status='abnormal').count()

            rank_stats = TourTask.objects.values('program__name').annotate(
                task_count=Count('id'),
            ).order_by('-task_count')[:10]

            for item in rank_stats:
                p_name = item['program__name'] or '未分类'
                upcoming_count = TourTask.objects.filter(
                    program__name=p_name,
                    status__in=['pending', 'in_progress'],
                    start_date__gte=today
                ).count()
                program_schedule_rank.append(ProgramScheduleRank(
                    program_name=p_name,
                    task_count=item['task_count'],
                    upcoming_count=upcoming_count,
                ))
        except Exception:
            pass

    tour_task_stats = TourTaskStats(
        future_tasks_count=future_tasks_count,
        in_progress_tasks_count=in_progress_tasks_count,
        abnormal_tasks_count=abnormal_tasks_count,
    )

    return DashboardData(
        vehicle_load_rates=vehicle_load_rates,
        program_prop_dist=program_prop_dist,
        tour_flow_stats=tour_flow_stats,
        maintenance_stats=maintenance_stats,
        high_loss_programs=high_loss_programs,
        tour_task_stats=tour_task_stats,
        program_schedule_rank=program_schedule_rank,
    )
