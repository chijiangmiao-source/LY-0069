from ninja import Router, Query
from typing import List, Optional
from django.db import transaction
from django.db.models import Q, Count, Sum
from datetime import date

from .models import TourTask, TourTaskVehicle, TourTaskProp, TourCostItem, TourSettlement
from .schemas import (
    TourTaskIn, TourTaskUpdateIn, TourTaskOut,
    TourTaskStatusUpdate, TourTaskStats, ProgramScheduleRank,
    TourTaskVehicleOut, TourTaskPropOut,
    TourCostItemIn, TourCostItemUpdate, TourCostItemOut,
    TourSettlementIn, TourSettlementSubmit, TourSettlementOut,
    TourCostStats, ProgramCostRank, CityCostStat
)
from apps.auth_app.auth import JWTAuth
from apps.common.services import (
    TourTaskService,
    CostItemService,
    SettlementService,
)
from apps.common.exceptions import (
    COST_TYPE_DISPLAY,
)

router = Router(tags=['巡演任务管理'], auth=JWTAuth())


def serialize_task_vehicle(tv: TourTaskVehicle) -> dict:
    return {
        'id': tv.id,
        'vehicle_id': tv.vehicle_id,
        'vehicle_code': tv.vehicle.code,
        'vehicle_model': tv.vehicle.model,
    }


def serialize_task_prop(tp: TourTaskProp) -> dict:
    return {
        'id': tp.id,
        'prop_id': tp.prop_id,
        'prop_code': tp.prop.code,
        'prop_name': tp.prop.name,
        'quantity': tp.quantity,
    }


def serialize_task(task: TourTask) -> dict:
    vehicles = [serialize_task_vehicle(tv) for tv in task.task_vehicles.select_related('vehicle').all()]
    props = [serialize_task_prop(tp) for tp in task.task_props.select_related('prop').all()]
    return {
        'id': task.id,
        'program_id': task.program_id,
        'program_name': task.program.name,
        'performance_date': task.performance_date,
        'city': task.city,
        'venue': task.venue,
        'person_in_charge': task.person_in_charge,
        'start_date': task.start_date,
        'end_date': task.end_date,
        'status': task.status,
        'execution_status': task.execution_status,
        'abnormal_situation': task.abnormal_situation,
        'completion_result': task.completion_result,
        'remark': task.remark,
        'vehicles': vehicles,
        'props': props,
        'created_at': task.created_at,
        'updated_at': task.updated_at,
    }


@router.get('/list', response=List[TourTaskOut])
def list_tasks(
    request,
    status: Optional[str] = Query(None),
    program_id: Optional[int] = Query(None),
    city: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
):
    queryset = TourTask.objects.select_related('program').all()
    if status:
        queryset = queryset.filter(status=status)
    if program_id:
        queryset = queryset.filter(program_id=program_id)
    if city:
        queryset = queryset.filter(city__icontains=city)
    if keyword:
        queryset = queryset.filter(
            Q(program__name__icontains=keyword) |
            Q(venue__icontains=keyword) |
            Q(person_in_charge__icontains=keyword)
        )
    return [serialize_task(t) for t in queryset]


@router.get('/stats', response=TourTaskStats)
def get_task_stats(request):
    today = date.today()
    future_tasks_count = TourTask.objects.filter(
        status__in=['pending', 'in_progress'],
        start_date__gte=today
    ).count()
    in_progress_tasks_count = TourTask.objects.filter(status='in_progress').count()
    abnormal_tasks_count = TourTask.objects.filter(status='abnormal').count()
    return TourTaskStats(
        future_tasks_count=future_tasks_count,
        in_progress_tasks_count=in_progress_tasks_count,
        abnormal_tasks_count=abnormal_tasks_count,
    )


@router.get('/schedule-rank', response=List[ProgramScheduleRank])
def get_schedule_rank(request):
    today = date.today()
    stats = TourTask.objects.values('program__name').annotate(
        task_count=Count('id'),
    ).order_by('-task_count')[:10]

    result = []
    for item in stats:
        program_name = item['program__name'] or '未分类'
        upcoming_count = TourTask.objects.filter(
            program__name=program_name,
            status__in=['pending', 'in_progress'],
            start_date__gte=today
        ).count()
        result.append(ProgramScheduleRank(
            program_name=program_name,
            task_count=item['task_count'],
            upcoming_count=upcoming_count,
        ))
    return result


@router.get('/{task_id}', response=TourTaskOut)
def get_task(request, task_id: int):
    try:
        task = TourTask.objects.select_related('program').get(id=task_id)
    except TourTask.DoesNotExist:
        from apps.common.exceptions import NotFoundException, ERR_MSG_TASK_NOT_EXIST
        raise NotFoundException(ERR_MSG_TASK_NOT_EXIST)
    return serialize_task(task)


@router.post('/list', response=TourTaskOut)
@transaction.atomic
def create_task(request, data: TourTaskIn):
    task = TourTaskService.create_task(data)
    return serialize_task(task)


@router.put('/{task_id}', response=TourTaskOut)
@transaction.atomic
def update_task(request, task_id: int, data: TourTaskUpdateIn):
    task = TourTaskService.update_task(task_id, data)
    return serialize_task(task)


@router.post('/{task_id}/status', response=TourTaskOut)
@transaction.atomic
def update_task_status(request, task_id: int, data: TourTaskStatusUpdate):
    task = TourTaskService.update_task_status(task_id, data)
    return serialize_task(task)


@router.delete('/{task_id}')
@transaction.atomic
def delete_task(request, task_id: int):
    TourTaskService.delete_task(task_id)
    return {'success': True}


def serialize_cost_item(item: TourCostItem) -> dict:
    return {
        'id': item.id,
        'tour_task_id': item.tour_task_id,
        'tour_task_name': str(item.tour_task),
        'cost_type': item.cost_type,
        'cost_type_display': COST_TYPE_DISPLAY.get(item.cost_type, item.cost_type),
        'amount': float(item.amount),
        'description': item.description,
        'expense_date': item.expense_date,
        'operator': item.operator,
        'receipt_no': item.receipt_no,
        'is_abnormal_cost': item.is_abnormal_cost,
        'abnormal_remark': item.abnormal_remark,
        'created_at': item.created_at,
        'updated_at': item.updated_at,
    }


def serialize_settlement(s: TourSettlement) -> dict:
    return {
        'id': s.id,
        'tour_task_id': s.tour_task_id,
        'tour_task_name': str(s.tour_task),
        'program_name': s.tour_task.program.name,
        'city': s.tour_task.city,
        'performance_date': s.tour_task.performance_date,
        'task_status': s.tour_task.status,
        'settlement_no': s.settlement_no,
        'transport_cost': float(s.transport_cost),
        'labor_cost': float(s.labor_cost),
        'venue_cost': float(s.venue_cost),
        'maintenance_cost': float(s.maintenance_cost),
        'temporary_purchase_cost': float(s.temporary_purchase_cost),
        'abnormal_handling_cost': float(s.abnormal_handling_cost),
        'total_cost': float(s.total_cost),
        'abnormal_cost_note': s.abnormal_cost_note,
        'settlement_status': s.settlement_status,
        'settler': s.settler,
        'settlement_date': s.settlement_date,
        'remark': s.remark,
        'created_at': s.created_at,
        'updated_at': s.updated_at,
    }


@router.get('/cost-items', response=List[TourCostItemOut])
def list_cost_items(
    request,
    tour_task_id: Optional[int] = Query(None),
    cost_type: Optional[str] = Query(None),
    program_id: Optional[int] = Query(None),
    city: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
):
    queryset = TourCostItem.objects.select_related('tour_task', 'tour_task__program').all()
    if tour_task_id:
        queryset = queryset.filter(tour_task_id=tour_task_id)
    if cost_type:
        queryset = queryset.filter(cost_type=cost_type)
    if program_id:
        queryset = queryset.filter(tour_task__program_id=program_id)
    if city:
        queryset = queryset.filter(tour_task__city__icontains=city)
    if start_date:
        queryset = queryset.filter(expense_date__gte=start_date)
    if end_date:
        queryset = queryset.filter(expense_date__lte=end_date)
    return [serialize_cost_item(item) for item in queryset]


@router.get('/cost-items/{item_id}', response=TourCostItemOut)
def get_cost_item(request, item_id: int):
    try:
        item = TourCostItem.objects.select_related('tour_task').get(id=item_id)
    except TourCostItem.DoesNotExist:
        from apps.common.exceptions import NotFoundException, ERR_MSG_COST_ITEM_NOT_EXIST
        raise NotFoundException(ERR_MSG_COST_ITEM_NOT_EXIST)
    return serialize_cost_item(item)


@router.post('/cost-items', response=TourCostItemOut)
@transaction.atomic
def create_cost_item(request, data: TourCostItemIn):
    item = CostItemService.create_cost_item(data)
    return serialize_cost_item(item)


@router.put('/cost-items/{item_id}', response=TourCostItemOut)
@transaction.atomic
def update_cost_item(request, item_id: int, data: TourCostItemUpdate):
    item = CostItemService.update_cost_item(item_id, data)
    return serialize_cost_item(item)


@router.delete('/cost-items/{item_id}')
@transaction.atomic
def delete_cost_item(request, item_id: int):
    CostItemService.delete_cost_item(item_id)
    return {'success': True}


@router.get('/settlements', response=List[TourSettlementOut])
def list_settlements(
    request,
    tour_task_id: Optional[int] = Query(None),
    settlement_status: Optional[str] = Query(None),
    program_id: Optional[int] = Query(None),
    city: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
):
    queryset = TourSettlement.objects.select_related('tour_task', 'tour_task__program').all()
    if tour_task_id:
        queryset = queryset.filter(tour_task_id=tour_task_id)
    if settlement_status:
        queryset = queryset.filter(settlement_status=settlement_status)
    if program_id:
        queryset = queryset.filter(tour_task__program_id=program_id)
    if city:
        queryset = queryset.filter(tour_task__city__icontains=city)
    if start_date:
        queryset = queryset.filter(tour_task__performance_date__gte=start_date)
    if end_date:
        queryset = queryset.filter(tour_task__performance_date__lte=end_date)
    return [serialize_settlement(s) for s in queryset]


@router.get('/settlements/{settlement_id}', response=TourSettlementOut)
def get_settlement(request, settlement_id: int):
    try:
        s = TourSettlement.objects.select_related('tour_task', 'tour_task__program').get(id=settlement_id)
    except TourSettlement.DoesNotExist:
        from apps.common.exceptions import NotFoundException, ERR_MSG_SETTLEMENT_NOT_EXIST
        raise NotFoundException(ERR_MSG_SETTLEMENT_NOT_EXIST)
    return serialize_settlement(s)


@router.post('/settlements', response=TourSettlementOut)
@transaction.atomic
def create_settlement(request, data: TourSettlementIn):
    s = SettlementService.create_settlement(data)
    return serialize_settlement(s)


@router.post('/settlements/{settlement_id}/refresh')
@transaction.atomic
def refresh_settlement(request, settlement_id: int):
    s = SettlementService.refresh_settlement(settlement_id)
    return serialize_settlement(s)


@router.post('/settlements/{settlement_id}/submit', response=TourSettlementOut)
@transaction.atomic
def submit_settlement(request, settlement_id: int, data: TourSettlementSubmit):
    username = request.auth.get('username') if hasattr(request, 'auth') and isinstance(request.auth, dict) else None
    s = SettlementService.submit_settlement(settlement_id, data, username)
    return serialize_settlement(s)


@router.post('/settlements/{settlement_id}/confirm', response=TourSettlementOut)
@transaction.atomic
def confirm_settlement(request, settlement_id: int):
    s = SettlementService.confirm_settlement(settlement_id)
    return serialize_settlement(s)


@router.delete('/settlements/{settlement_id}')
@transaction.atomic
def delete_settlement(request, settlement_id: int):
    SettlementService.delete_settlement(settlement_id)
    return {'success': True}


@router.get('/cost-stats/summary', response=TourCostStats)
def get_cost_stats_summary(
    request,
    program_id: Optional[int] = Query(None),
    city: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
):
    settlement_qs = TourSettlement.objects.filter(
        settlement_status__in=['submitted', 'confirmed']
    ).select_related('tour_task')

    if program_id:
        settlement_qs = settlement_qs.filter(tour_task__program_id=program_id)
    if city:
        settlement_qs = settlement_qs.filter(tour_task__city__icontains=city)
    if start_date:
        settlement_qs = settlement_qs.filter(tour_task__performance_date__gte=start_date)
    if end_date:
        settlement_qs = settlement_qs.filter(tour_task__performance_date__lte=end_date)

    agg = settlement_qs.aggregate(
        total_cost=Sum('total_cost'),
        transport_cost=Sum('transport_cost'),
        labor_cost=Sum('labor_cost'),
        venue_cost=Sum('venue_cost'),
        maintenance_cost=Sum('maintenance_cost'),
        temporary_purchase_cost=Sum('temporary_purchase_cost'),
        abnormal_handling_cost=Sum('abnormal_handling_cost'),
        task_count=Count('id'),
    )

    total_cost = float(agg['total_cost'] or 0)
    abnormal_cost = float(agg['abnormal_handling_cost'] or 0)
    task_count = agg['task_count'] or 0

    return TourCostStats(
        total_cost=total_cost,
        transport_cost=float(agg['transport_cost'] or 0),
        labor_cost=float(agg['labor_cost'] or 0),
        venue_cost=float(agg['venue_cost'] or 0),
        maintenance_cost=float(agg['maintenance_cost'] or 0),
        temporary_purchase_cost=float(agg['temporary_purchase_cost'] or 0),
        abnormal_handling_cost=abnormal_cost,
        task_count=task_count,
        avg_cost_per_task=round(total_cost / task_count, 2) if task_count > 0 else 0,
        abnormal_cost_ratio=round(abnormal_cost / total_cost * 100, 2) if total_cost > 0 else 0,
    )


@router.get('/cost-stats/by-program', response=List[ProgramCostRank])
def get_cost_stats_by_program(
    request,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
):
    settlement_qs = TourSettlement.objects.filter(
        settlement_status__in=['submitted', 'confirmed']
    ).select_related('tour_task', 'tour_task__program')

    if start_date:
        settlement_qs = settlement_qs.filter(tour_task__performance_date__gte=start_date)
    if end_date:
        settlement_qs = settlement_qs.filter(tour_task__performance_date__lte=end_date)

    stats = settlement_qs.values('tour_task__program__name').annotate(
        total_cost=Sum('total_cost'),
        task_count=Count('id'),
    ).order_by('-total_cost')[:10]

    result = []
    for item in stats:
        total_cost = float(item['total_cost'] or 0)
        task_count = item['task_count'] or 0
        result.append(ProgramCostRank(
            program_name=item['tour_task__program__name'] or '未分类',
            total_cost=total_cost,
            task_count=task_count,
            avg_cost_per_task=round(total_cost / task_count, 2) if task_count > 0 else 0,
        ))
    return result


@router.get('/cost-stats/by-city', response=List[CityCostStat])
def get_cost_stats_by_city(
    request,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
):
    settlement_qs = TourSettlement.objects.filter(
        settlement_status__in=['submitted', 'confirmed']
    ).select_related('tour_task')

    if start_date:
        settlement_qs = settlement_qs.filter(tour_task__performance_date__gte=start_date)
    if end_date:
        settlement_qs = settlement_qs.filter(tour_task__performance_date__lte=end_date)

    stats = settlement_qs.values('tour_task__city').annotate(
        total_cost=Sum('total_cost'),
        task_count=Count('id'),
    ).order_by('-total_cost')

    result = []
    for item in stats:
        total_cost = float(item['total_cost'] or 0)
        task_count = item['task_count'] or 0
        result.append(CityCostStat(
            city=item['tour_task__city'] or '未知城市',
            total_cost=total_cost,
            task_count=task_count,
            avg_cost_per_task=round(total_cost / task_count, 2) if task_count > 0 else 0,
        ))
    return result
