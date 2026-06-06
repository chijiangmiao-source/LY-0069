from ninja import Router
from django.db.models import Count

from .schemas import DashboardData, VehicleLoadRate, ProgramPropDist, TourFlowStats
from apps.auth_app.auth import JWTAuth
from apps.vehicles.models import Vehicle
from apps.props.models import Prop

router = Router(tags=['数据看板'], auth=JWTAuth())


try:
    from apps.loading.models import LoadingRecord, UnloadingRecord
except ImportError:
    LoadingRecord = None
    UnloadingRecord = None


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

    return DashboardData(
        vehicle_load_rates=vehicle_load_rates,
        program_prop_dist=program_prop_dist,
        tour_flow_stats=tour_flow_stats,
    )
