from ninja import Router, Query
from ninja.errors import HttpError
from typing import List, Optional
from django.db import transaction
from django.db.models import Q, Count
from datetime import date

from .models import TourTask, TourTaskVehicle, TourTaskProp
from .schemas import (
    TourTaskIn, TourTaskUpdateIn, TourTaskOut,
    TourTaskStatusUpdate, TourTaskStats, ProgramScheduleRank,
    TourTaskVehicleOut, TourTaskPropOut
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
