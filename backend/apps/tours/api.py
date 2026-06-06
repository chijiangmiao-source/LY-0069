from ninja import Router, Query
from ninja.errors import HttpError
from typing import List, Optional
from django.db import transaction
from django.db.models import Q, Count, Sum
from datetime import date, datetime

from .models import TourTask, TourTaskVehicle, TourTaskProp, TourCostItem, TourSettlement
from .schemas import (
    TourTaskIn, TourTaskUpdateIn, TourTaskOut,
    TourTaskStatusUpdate, TourTaskStats, ProgramScheduleRank,
    TourTaskVehicleOut, TourTaskPropOut,
    TourCostItemIn, TourCostItemUpdate, TourCostItemOut,
    TourSettlementIn, TourSettlementSubmit, TourSettlementOut,
    TourCostStats, ProgramCostRank, CityCostStat
)
from apps.programs.models import Program
from apps.vehicles.models import Vehicle
from apps.props.models import Prop
from apps.auth_app.auth import JWTAuth

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


def check_vehicle_conflict(vehicle_ids: List[int], start_date: date, end_date: date, exclude_task_id: Optional[int] = None):
    for vehicle_id in vehicle_ids:
        conflicts = TourTaskVehicle.objects.filter(
            vehicle_id=vehicle_id,
            tour_task__start_date__lte=end_date,
            tour_task__end_date__gte=start_date,
            tour_task__status__in=['pending', 'in_progress']
        ).select_related('tour_task')
        if exclude_task_id:
            conflicts = conflicts.exclude(tour_task_id=exclude_task_id)
        if conflicts.exists():
            conflict_tasks = [f"{c.tour_task.program.name}({c.tour_task.start_date}~{c.tour_task.end_date})" for c in conflicts]
            vehicle = Vehicle.objects.get(id=vehicle_id)
            raise HttpError(400, f'车辆「{vehicle.code}」在时间段 {start_date}~{end_date} 已被安排到其他任务: {", ".join(conflict_tasks)}')


def check_prop_conflict(prop_items: List, start_date: date, end_date: date, exclude_task_id: Optional[int] = None):
    prop_ids = [item.prop_id for item in prop_items]
    for prop_id in prop_ids:
        conflicts = TourTaskProp.objects.filter(
            prop_id=prop_id,
            tour_task__start_date__lte=end_date,
            tour_task__end_date__gte=start_date,
            tour_task__status__in=['pending', 'in_progress']
        ).select_related('tour_task')
        if exclude_task_id:
            conflicts = conflicts.exclude(tour_task_id=exclude_task_id)
        if conflicts.exists():
            conflict_tasks = [f"{c.tour_task.program.name}({c.tour_task.start_date}~{c.tour_task.end_date})" for c in conflicts]
            prop = Prop.objects.get(id=prop_id)
            raise HttpError(400, f'道具「{prop.code} {prop.name}」在时间段 {start_date}~{end_date} 已被安排到其他任务: {", ".join(conflict_tasks)}')


def validate_props_available(prop_items: List):
    today = date.today()
    for item in prop_items:
        try:
            prop = Prop.objects.get(id=item.prop_id)
        except Prop.DoesNotExist:
            raise HttpError(400, f'道具ID {item.prop_id} 不存在')

        if prop.scrap_status in ('scrapped', 'approved'):
            raise HttpError(400, f'道具「{prop.code} {prop.name}」已报废，不可加入巡演任务')

        if prop.next_maintenance_date and prop.next_maintenance_date < today:
            raise HttpError(400, f'道具「{prop.code} {prop.name}」维保已超期（下次维保日期: {prop.next_maintenance_date}），不可加入巡演任务')


def validate_vehicles_available(vehicle_ids: List[int]):
    for vehicle_id in vehicle_ids:
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
        except Vehicle.DoesNotExist:
            raise HttpError(400, f'车辆ID {vehicle_id} 不存在')

        if vehicle.status == 'inactive':
            raise HttpError(400, f'车辆「{vehicle.code}」已停用，不可加入巡演任务')


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
        raise HttpError(404, '巡演任务不存在')
    return serialize_task(task)


@router.post('/list', response=TourTaskOut)
@transaction.atomic
def create_task(request, data: TourTaskIn):
    if data.start_date > data.end_date:
        raise HttpError(400, '任务开始日期不能晚于结束日期')
    if data.performance_date < data.start_date or data.performance_date > data.end_date:
        raise HttpError(400, '演出日期必须在任务开始和结束日期之间')

    try:
        program = Program.objects.get(id=data.program_id)
    except Program.DoesNotExist:
        raise HttpError(400, '剧目不存在')

    validate_vehicles_available(data.vehicle_ids)
    validate_props_available(data.props)
    check_vehicle_conflict(data.vehicle_ids, data.start_date, data.end_date)
    check_prop_conflict(data.props, data.start_date, data.end_date)

    task = TourTask.objects.create(
        program=program,
        performance_date=data.performance_date,
        city=data.city,
        venue=data.venue,
        person_in_charge=data.person_in_charge,
        start_date=data.start_date,
        end_date=data.end_date,
        remark=data.remark,
    )

    for vehicle_id in data.vehicle_ids:
        TourTaskVehicle.objects.create(tour_task=task, vehicle_id=vehicle_id)

    for prop_item in data.props:
        TourTaskProp.objects.create(
            tour_task=task,
            prop_id=prop_item.prop_id,
            quantity=prop_item.quantity,
        )

    return serialize_task(task)


@router.put('/{task_id}', response=TourTaskOut)
@transaction.atomic
def update_task(request, task_id: int, data: TourTaskUpdateIn):
    try:
        task = TourTask.objects.select_related('program').get(id=task_id)
    except TourTask.DoesNotExist:
        raise HttpError(404, '巡演任务不存在')

    if task.status in ('completed', 'cancelled'):
        raise HttpError(400, '已完成或已取消的任务不可修改')

    if data.start_date > data.end_date:
        raise HttpError(400, '任务开始日期不能晚于结束日期')
    if data.performance_date < data.start_date or data.performance_date > data.end_date:
        raise HttpError(400, '演出日期必须在任务开始和结束日期之间')

    try:
        program = Program.objects.get(id=data.program_id)
    except Program.DoesNotExist:
        raise HttpError(400, '剧目不存在')

    validate_vehicles_available(data.vehicle_ids)
    validate_props_available(data.props)
    check_vehicle_conflict(data.vehicle_ids, data.start_date, data.end_date, exclude_task_id=task_id)
    check_prop_conflict(data.props, data.start_date, data.end_date, exclude_task_id=task_id)

    task.program = program
    task.performance_date = data.performance_date
    task.city = data.city
    task.venue = data.venue
    task.person_in_charge = data.person_in_charge
    task.start_date = data.start_date
    task.end_date = data.end_date
    task.remark = data.remark
    task.save()

    TourTaskVehicle.objects.filter(tour_task=task).delete()
    for vehicle_id in data.vehicle_ids:
        TourTaskVehicle.objects.create(tour_task=task, vehicle_id=vehicle_id)

    TourTaskProp.objects.filter(tour_task=task).delete()
    for prop_item in data.props:
        TourTaskProp.objects.create(
            tour_task=task,
            prop_id=prop_item.prop_id,
            quantity=prop_item.quantity,
        )

    return serialize_task(task)


@router.post('/{task_id}/status', response=TourTaskOut)
@transaction.atomic
def update_task_status(request, task_id: int, data: TourTaskStatusUpdate):
    try:
        task = TourTask.objects.select_related('program').get(id=task_id)
    except TourTask.DoesNotExist:
        raise HttpError(404, '巡演任务不存在')

    valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled', 'abnormal']
    if data.status not in valid_statuses:
        raise HttpError(400, f'无效的任务状态: {data.status}')

    if data.status == 'in_progress':
        valid_exec = ['not_started', 'preparing', 'transporting', 'performing', 'returning', 'finished']
        if data.execution_status and data.execution_status not in valid_exec:
            raise HttpError(400, f'无效的执行状态: {data.execution_status}')

    task.status = data.status
    if data.execution_status:
        task.execution_status = data.execution_status
    if data.abnormal_situation is not None:
        task.abnormal_situation = data.abnormal_situation
    if data.completion_result is not None:
        task.completion_result = data.completion_result

    if data.status == 'completed' and not task.completion_result:
        task.completion_result = '任务已顺利完成'
    if data.status == 'abnormal' and not task.abnormal_situation:
        raise HttpError(400, '标记为异常任务时必须填写异常情况')

    task.save()
    return serialize_task(task)


@router.delete('/{task_id}')
@transaction.atomic
def delete_task(request, task_id: int):
    try:
        task = TourTask.objects.get(id=task_id)
    except TourTask.DoesNotExist:
        raise HttpError(404, '巡演任务不存在')

    if task.status == 'in_progress':
        raise HttpError(400, '执行中的任务不可删除，请先取消或完成任务')

    TourTaskVehicle.objects.filter(tour_task=task).delete()
    TourTaskProp.objects.filter(tour_task=task).delete()
    task.delete()
    return {'success': True}


COST_TYPE_DISPLAY = {
    'transport': '运输费',
    'labor': '人工费',
    'venue': '场地费',
    'maintenance': '维保费',
    'temporary_purchase': '临时采购费',
    'abnormal_handling': '异常处理费',
}

VALID_COST_TYPES = list(COST_TYPE_DISPLAY.keys())


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


def generate_settlement_no() -> str:
    today = datetime.now()
    prefix = f'JS{today.strftime("%Y%m%d")}'
    count = TourSettlement.objects.filter(settlement_no__startswith=prefix).count() + 1
    return f'{prefix}{count:04d}'


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
        raise HttpError(404, '成本项不存在')
    return serialize_cost_item(item)


@router.post('/cost-items', response=TourCostItemOut)
@transaction.atomic
def create_cost_item(request, data: TourCostItemIn):
    try:
        task = TourTask.objects.get(id=data.tour_task_id)
    except TourTask.DoesNotExist:
        raise HttpError(404, '巡演任务不存在')

    if task.status == 'cancelled':
        raise HttpError(400, '已取消的任务不可登记成本')

    if data.cost_type not in VALID_COST_TYPES:
        raise HttpError(400, f'无效的费用类型: {data.cost_type}')

    if data.amount < 0:
        raise HttpError(400, '金额不能为负数')

    if data.expense_date < task.start_date or data.expense_date > task.end_date:
        raise HttpError(400, '费用发生日期必须在任务开始和结束日期之间')

    if data.is_abnormal_cost and not data.abnormal_remark:
        raise HttpError(400, '标记为异常费用时必须填写异常费用说明')

    is_abnormal = data.is_abnormal_cost or data.cost_type == 'abnormal_handling'

    item = TourCostItem.objects.create(
        tour_task=task,
        cost_type=data.cost_type,
        amount=data.amount,
        description=data.description,
        expense_date=data.expense_date,
        operator=data.operator,
        receipt_no=data.receipt_no,
        is_abnormal_cost=is_abnormal,
        abnormal_remark=data.abnormal_remark,
    )
    return serialize_cost_item(item)


@router.put('/cost-items/{item_id}', response=TourCostItemOut)
@transaction.atomic
def update_cost_item(request, item_id: int, data: TourCostItemUpdate):
    try:
        item = TourCostItem.objects.select_related('tour_task').get(id=item_id)
    except TourCostItem.DoesNotExist:
        raise HttpError(404, '成本项不存在')

    task = item.tour_task
    if task.status == 'cancelled':
        raise HttpError(400, '已取消任务的成本项不可修改')

    if hasattr(task, 'settlement') and task.settlement.settlement_status in ('submitted', 'confirmed'):
        raise HttpError(400, '该任务已提交结算，成本项不可修改')

    if data.cost_type not in VALID_COST_TYPES:
        raise HttpError(400, f'无效的费用类型: {data.cost_type}')

    if data.amount < 0:
        raise HttpError(400, '金额不能为负数')

    if data.expense_date < task.start_date or data.expense_date > task.end_date:
        raise HttpError(400, '费用发生日期必须在任务开始和结束日期之间')

    is_abnormal = data.is_abnormal_cost or data.cost_type == 'abnormal_handling'
    if is_abnormal and not data.abnormal_remark:
        raise HttpError(400, '标记为异常费用时必须填写异常费用说明')

    item.cost_type = data.cost_type
    item.amount = data.amount
    item.description = data.description
    item.expense_date = data.expense_date
    item.operator = data.operator
    item.receipt_no = data.receipt_no
    item.is_abnormal_cost = is_abnormal
    item.abnormal_remark = data.abnormal_remark
    item.save()
    return serialize_cost_item(item)


@router.delete('/cost-items/{item_id}')
@transaction.atomic
def delete_cost_item(request, item_id: int):
    try:
        item = TourCostItem.objects.select_related('tour_task').get(id=item_id)
    except TourCostItem.DoesNotExist:
        raise HttpError(404, '成本项不存在')

    task = item.tour_task
    if hasattr(task, 'settlement') and task.settlement.settlement_status in ('submitted', 'confirmed'):
        raise HttpError(400, '该任务已提交结算，成本项不可删除')

    item.delete()
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
        raise HttpError(404, '结算单不存在')
    return serialize_settlement(s)


@router.post('/settlements', response=TourSettlementOut)
@transaction.atomic
def create_settlement(request, data: TourSettlementIn):
    try:
        task = TourTask.objects.select_related('program').get(id=data.tour_task_id)
    except TourTask.DoesNotExist:
        raise HttpError(404, '巡演任务不存在')

    if task.status == 'cancelled':
        raise HttpError(400, '已取消的任务不可生成结算记录')

    if hasattr(task, 'settlement'):
        raise HttpError(400, '该任务已存在结算单')

    settlement_no = generate_settlement_no()
    s = TourSettlement.objects.create(
        tour_task=task,
        settlement_no=settlement_no,
        remark=data.remark,
    )
    s.aggregate_from_cost_items()
    s.save()
    return serialize_settlement(s)


@router.post('/settlements/{settlement_id}/refresh')
@transaction.atomic
def refresh_settlement(request, settlement_id: int):
    try:
        s = TourSettlement.objects.select_related('tour_task').get(id=settlement_id)
    except TourSettlement.DoesNotExist:
        raise HttpError(404, '结算单不存在')

    if s.settlement_status in ('submitted', 'confirmed'):
        raise HttpError(400, '已提交或已确认的结算单不可刷新')

    s.aggregate_from_cost_items()
    s.save()
    return serialize_settlement(s)


@router.post('/settlements/{settlement_id}/submit', response=TourSettlementOut)
@transaction.atomic
def submit_settlement(request, settlement_id: int, data: TourSettlementSubmit):
    try:
        s = TourSettlement.objects.select_related('tour_task').get(id=settlement_id)
    except TourSettlement.DoesNotExist:
        raise HttpError(404, '结算单不存在')

    task = s.tour_task
    if task.status in ('pending', 'in_progress'):
        raise HttpError(400, '未完成的任务不能提交最终结算')

    if task.status == 'abnormal':
        if not data.abnormal_cost_note and not s.abnormal_cost_note:
            raise HttpError(400, '异常任务必须补充额外费用说明')

    if s.settlement_status == 'confirmed':
        raise HttpError(400, '已确认的结算单不可重复提交')

    s.aggregate_from_cost_items()
    if data.abnormal_cost_note:
        s.abnormal_cost_note = data.abnormal_cost_note
    if data.remark:
        s.remark = data.remark
    s.settlement_status = 'submitted'
    s.settlement_date = date.today()
    s.settler = request.auth.get('username') if hasattr(request, 'auth') and isinstance(request.auth, dict) else None
    s.save()
    return serialize_settlement(s)


@router.post('/settlements/{settlement_id}/confirm', response=TourSettlementOut)
@transaction.atomic
def confirm_settlement(request, settlement_id: int):
    try:
        s = TourSettlement.objects.select_related('tour_task').get(id=settlement_id)
    except TourSettlement.DoesNotExist:
        raise HttpError(404, '结算单不存在')

    if s.settlement_status != 'submitted':
        raise HttpError(400, '只有已提交的结算单可以确认')

    s.settlement_status = 'confirmed'
    s.save()
    return serialize_settlement(s)


@router.delete('/settlements/{settlement_id}')
@transaction.atomic
def delete_settlement(request, settlement_id: int):
    try:
        s = TourSettlement.objects.get(id=settlement_id)
    except TourSettlement.DoesNotExist:
        raise HttpError(404, '结算单不存在')

    if s.settlement_status == 'confirmed':
        raise HttpError(400, '已确认的结算单不可删除')

    s.delete()
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
