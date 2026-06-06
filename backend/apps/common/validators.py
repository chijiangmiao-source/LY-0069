from datetime import date
from typing import List, Optional, Any

from apps.vehicles.models import Vehicle
from apps.props.models import Prop
from apps.programs.models import Program
from apps.tours.models import TourTaskVehicle, TourTaskProp
from apps.loading.models import LoadingRecord, UnloadingRecord

from .exceptions import (
    NotFoundException,
    ValidationException,
    StatusValidationException,
    ConflictException,
    ERR_MSG_VEHICLE_NOT_EXIST,
    ERR_MSG_PROP_NOT_EXIST,
    ERR_MSG_PROGRAM_NOT_EXIST,
    ERR_MSG_LOADING_NOT_EXIST,
    ERR_MSG_UNLOADING_NOT_EXIST,
    ERR_MSG_QUANTITY_MUST_BE_POSITIVE,
    ERR_MSG_AMOUNT_NON_NEGATIVE,
    ERR_MSG_VEHICLE_INACTIVE,
    ERR_MSG_VEHICLE_INACTIVE_FOR_TOUR,
    ERR_MSG_VEHICLE_OVERLOAD,
    ERR_MSG_VEHICLE_OVERLOAD_ADJUSTED,
    ERR_MSG_VEHICLE_NEGATIVE_LOAD,
    ERR_MSG_VEHICLE_NEGATIVE_LOAD_ADJUSTED,
    ERR_MSG_PROP_SCRAPPED_FOR_LOADING,
    ERR_MSG_PROP_SCRAPPED_FOR_TOUR,
    ERR_MSG_PROP_MAINTENANCE_OVERDUE_FOR_LOADING,
    ERR_MSG_PROP_MAINTENANCE_OVERDUE_FOR_TOUR,
    ERR_MSG_SCRAP_STATUS_SCRAPPED,
    ERR_MSG_SCRAP_STATUS_PENDING,
    ERR_MSG_UNLOADING_DATE_EARLIER,
    ERR_MSG_UNLOADING_RECORD_EXISTS,
    ERR_MSG_LOADING_HAS_UNLOADING,
    ERR_MSG_DAMAGE_REASON_REQUIRED,
    ERR_MSG_TASK_DATE_RANGE_INVALID,
    ERR_MSG_PERFORMANCE_DATE_OUT_OF_RANGE,
    ERR_MSG_TASK_COMPLETED_OR_CANCELLED,
    ERR_MSG_TASK_IN_PROGRESS_CANNOT_DELETE,
    ERR_MSG_TASK_INVALID_STATUS,
    ERR_MSG_TASK_INVALID_EXEC_STATUS,
    ERR_MSG_TASK_ABNORMAL_REQUIRES_DESC,
    ERR_MSG_VEHICLE_TIME_CONFLICT,
    ERR_MSG_PROP_TIME_CONFLICT,
    ERR_MSG_COST_TYPE_INVALID,
    ERR_MSG_COST_DATE_OUT_OF_RANGE,
    ERR_MSG_TASK_CANCELLED_NO_COST,
    ERR_MSG_TASK_CANCELLED_COST_CANNOT_EDIT,
    ERR_MSG_ABNORMAL_COST_REQUIRES_REMARK,
    ERR_MSG_SETTLEMENT_SUBMITTED_CANNOT_EDIT_COST,
    ERR_MSG_SETTLEMENT_SUBMITTED_CANNOT_DELETE_COST,
    ERR_MSG_TASK_CANCELLED_NO_SETTLEMENT,
    ERR_MSG_SETTLEMENT_ALREADY_EXISTS,
    ERR_MSG_SETTLEMENT_SUBMITTED_OR_CONFIRMED_CANNOT_REFRESH,
    ERR_MSG_TASK_NOT_COMPLETED_CANNOT_SUBMIT_SETTLEMENT,
    ERR_MSG_ABNORMAL_TASK_REQUIRES_COST_NOTE,
    ERR_MSG_SETTLEMENT_ALREADY_CONFIRMED,
    ERR_MSG_SETTLEMENT_ONLY_SUBMITTED_CAN_CONFIRM,
    ERR_MSG_SETTLEMENT_CONFIRMED_CANNOT_DELETE,
    ERR_MSG_PROP_ALREADY_SCRAPPED,
    ERR_MSG_SCRAP_APPLICATION_PENDING_EXISTS,
    ERR_MSG_SCRAP_ONLY_PENDING_CAN_APPROVE,
    VALID_COST_TYPES,
    TOUR_TASK_STATUSES,
    TOUR_EXECUTION_STATUSES,
    TOUR_TASK_STATUSES_FOR_CONFLICT,
    PROP_SCRAP_STATUSES_BLOCKING,
    PROP_SCRAP_STATUSES_BLOCKING_FOR_TOUR,
    SETTLEMENT_STATUSES_LOCKED,
    PROPS_MAINTENANCE_WARNING_DAYS,
)


def validate_positive_quantity(quantity: int, field_name: str = '数量'):
    if quantity <= 0:
        raise ValidationException(f'{field_name}必须大于0')


def validate_non_negative_amount(amount: float):
    if amount < 0:
        raise ValidationException(ERR_MSG_AMOUNT_NON_NEGATIVE)


def validate_non_empty_text(text: str, field_name: str):
    if not text or text.strip() == '':
        raise ValidationException(f'{field_name}必须填写')


def get_vehicle_or_404(vehicle_id: int) -> Vehicle:
    try:
        return Vehicle.objects.get(id=vehicle_id)
    except Vehicle.DoesNotExist:
        raise NotFoundException(ERR_MSG_VEHICLE_NOT_EXIST)


def get_prop_or_404(prop_id: int) -> Prop:
    try:
        return Prop.objects.get(id=prop_id)
    except Prop.DoesNotExist:
        raise NotFoundException(ERR_MSG_PROP_NOT_EXIST)


def get_program_or_404(program_id: int) -> Program:
    try:
        return Program.objects.get(id=program_id)
    except Program.DoesNotExist:
        raise NotFoundException(ERR_MSG_PROGRAM_NOT_EXIST)


def get_loading_or_404(loading_id: int) -> LoadingRecord:
    try:
        return LoadingRecord.objects.get(id=loading_id)
    except LoadingRecord.DoesNotExist:
        raise NotFoundException(ERR_MSG_LOADING_NOT_EXIST)


def get_unloading_or_404(unloading_id: int) -> UnloadingRecord:
    try:
        return UnloadingRecord.objects.get(id=unloading_id)
    except UnloadingRecord.DoesNotExist:
        raise NotFoundException(ERR_MSG_UNLOADING_NOT_EXIST)


def validate_vehicle_active(vehicle: Vehicle):
    if vehicle.status == 'inactive':
        raise StatusValidationException(ERR_MSG_VEHICLE_INACTIVE)


def validate_vehicle_active_for_tour(vehicle: Vehicle):
    if vehicle.status == 'inactive':
        raise StatusValidationException(
            ERR_MSG_VEHICLE_INACTIVE_FOR_TOUR.format(code=vehicle.code)
        )


def validate_vehicle_load_capacity(
    vehicle: Vehicle,
    quantity_to_add: int,
    quantity_to_remove: int = 0
):
    new_load = vehicle.current_load - quantity_to_remove + quantity_to_add
    if new_load > vehicle.capacity:
        if quantity_to_remove == 0:
            raise ValidationException(
                ERR_MSG_VEHICLE_OVERLOAD.format(
                    current=vehicle.current_load,
                    capacity=vehicle.capacity
                )
            )
        else:
            raise ValidationException(
                ERR_MSG_VEHICLE_OVERLOAD_ADJUSTED.format(
                    adjusted=new_load,
                    capacity=vehicle.capacity
                )
            )


def validate_vehicle_unload_quantity(
    vehicle: Vehicle,
    quantity_to_remove: int,
    quantity_to_add_back: int = 0
):
    new_load = vehicle.current_load + quantity_to_add_back - quantity_to_remove
    if new_load < 0:
        if quantity_to_add_back == 0:
            raise ValidationException(
                ERR_MSG_VEHICLE_NEGATIVE_LOAD.format(current=vehicle.current_load)
            )
        else:
            raise ValidationException(
                ERR_MSG_VEHICLE_NEGATIVE_LOAD_ADJUSTED.format(adjusted=new_load)
            )


def _get_prop_scrap_status_msg(scrap_status: str) -> str:
    if scrap_status in ('scrapped', 'approved'):
        return ERR_MSG_SCRAP_STATUS_SCRAPPED
    if scrap_status == 'pending':
        return ERR_MSG_SCRAP_STATUS_PENDING
    return ''


def validate_prop_available_for_loading(prop: Prop, check_date: Optional[date] = None):
    today = check_date or date.today()

    if prop.scrap_status in PROP_SCRAP_STATUSES_BLOCKING:
        status_msg = _get_prop_scrap_status_msg(prop.scrap_status)
        raise StatusValidationException(
            ERR_MSG_PROP_SCRAPPED_FOR_LOADING.format(
                code=prop.code,
                name=prop.name,
                status_msg=status_msg
            )
        )

    if prop.next_maintenance_date and prop.next_maintenance_date < today:
        raise StatusValidationException(
            ERR_MSG_PROP_MAINTENANCE_OVERDUE_FOR_LOADING.format(
                code=prop.code,
                name=prop.name,
                date=prop.next_maintenance_date
            )
        )


def validate_prop_available_for_tour(prop: Prop, check_date: Optional[date] = None):
    today = check_date or date.today()

    if prop.scrap_status in PROP_SCRAP_STATUSES_BLOCKING_FOR_TOUR:
        raise StatusValidationException(
            ERR_MSG_PROP_SCRAPPED_FOR_TOUR.format(
                code=prop.code,
                name=prop.name
            )
        )

    if prop.next_maintenance_date and prop.next_maintenance_date < today:
        raise StatusValidationException(
            ERR_MSG_PROP_MAINTENANCE_OVERDUE_FOR_TOUR.format(
                code=prop.code,
                name=prop.name,
                date=prop.next_maintenance_date
            )
        )


def validate_props_available_for_tour(prop_items: List[Any]):
    for item in prop_items:
        prop = get_prop_or_404(item.prop_id)
        validate_prop_available_for_tour(prop)


def validate_vehicles_active_for_tour(vehicle_ids: List[int]):
    for vehicle_id in vehicle_ids:
        vehicle = get_vehicle_or_404(vehicle_id)
        validate_vehicle_active_for_tour(vehicle)


def validate_unloading_date(loading_date: date, unloading_date: date):
    if unloading_date < loading_date:
        raise ValidationException(ERR_MSG_UNLOADING_DATE_EARLIER)


def validate_no_existing_unloading(loading_id: int):
    if UnloadingRecord.objects.filter(loading_id=loading_id).exists():
        raise ConflictException(ERR_MSG_UNLOADING_RECORD_EXISTS)


def validate_no_existing_unloading_except(loading_id: int, exclude_unloading_id: int):
    if UnloadingRecord.objects.filter(loading_id=loading_id).exclude(id=exclude_unloading_id).exists():
        raise ConflictException(ERR_MSG_UNLOADING_RECORD_EXISTS)


def validate_loading_has_no_unloading(loading: LoadingRecord):
    if hasattr(loading, 'unloading_record'):
        raise ConflictException(ERR_MSG_LOADING_HAS_UNLOADING)


def validate_damage_reason(reason: str):
    validate_non_empty_text(reason, ERR_MSG_DAMAGE_REASON_REQUIRED)


def validate_task_date_range(start_date: date, end_date: date):
    if start_date > end_date:
        raise ValidationException(ERR_MSG_TASK_DATE_RANGE_INVALID)


def validate_performance_date_in_range(
    performance_date: date,
    start_date: date,
    end_date: date
):
    if performance_date < start_date or performance_date > end_date:
        raise ValidationException(ERR_MSG_PERFORMANCE_DATE_OUT_OF_RANGE)


def validate_task_editable(task_status: str):
    if task_status in ('completed', 'cancelled'):
        raise StatusValidationException(ERR_MSG_TASK_COMPLETED_OR_CANCELLED)


def validate_task_deletable(task_status: str):
    if task_status == 'in_progress':
        raise StatusValidationException(ERR_MSG_TASK_IN_PROGRESS_CANNOT_DELETE)


def validate_task_status(status: str):
    if status not in TOUR_TASK_STATUSES:
        raise ValidationException(ERR_MSG_TASK_INVALID_STATUS.format(status=status))


def validate_task_execution_status(execution_status: str):
    if execution_status not in TOUR_EXECUTION_STATUSES:
        raise ValidationException(
            ERR_MSG_TASK_INVALID_EXEC_STATUS.format(status=execution_status)
        )


def validate_task_abnormal_has_description(
    status: str,
    abnormal_situation: Optional[str]
):
    if status == 'abnormal' and not abnormal_situation:
        raise ValidationException(ERR_MSG_TASK_ABNORMAL_REQUIRES_DESC)


def _find_vehicle_time_conflicts(
    vehicle_id: int,
    start_date: date,
    end_date: date,
    exclude_task_id: Optional[int] = None
):
    conflicts = TourTaskVehicle.objects.filter(
        vehicle_id=vehicle_id,
        tour_task__start_date__lte=end_date,
        tour_task__end_date__gte=start_date,
        tour_task__status__in=TOUR_TASK_STATUSES_FOR_CONFLICT
    ).select_related('tour_task')
    if exclude_task_id:
        conflicts = conflicts.exclude(tour_task_id=exclude_task_id)
    return conflicts


def _find_prop_time_conflicts(
    prop_id: int,
    start_date: date,
    end_date: date,
    exclude_task_id: Optional[int] = None
):
    conflicts = TourTaskProp.objects.filter(
        prop_id=prop_id,
        tour_task__start_date__lte=end_date,
        tour_task__end_date__gte=start_date,
        tour_task__status__in=TOUR_TASK_STATUSES_FOR_CONFLICT
    ).select_related('tour_task')
    if exclude_task_id:
        conflicts = conflicts.exclude(tour_task_id=exclude_task_id)
    return conflicts


def _format_conflict_tasks(conflicts) -> List[str]:
    return [
        f"{c.tour_task.program.name}({c.tour_task.start_date}~{c.tour_task.end_date})"
        for c in conflicts
    ]


def validate_vehicle_no_time_conflict(
    vehicle_id: int,
    start_date: date,
    end_date: date,
    exclude_task_id: Optional[int] = None
):
    conflicts = _find_vehicle_time_conflicts(vehicle_id, start_date, end_date, exclude_task_id)
    if conflicts.exists():
        conflict_tasks = _format_conflict_tasks(conflicts)
        vehicle = Vehicle.objects.get(id=vehicle_id)
        raise ConflictException(
            ERR_MSG_VEHICLE_TIME_CONFLICT.format(
                code=vehicle.code,
                start=start_date,
                end=end_date,
                tasks=', '.join(conflict_tasks)
            )
        )


def validate_prop_no_time_conflict(
    prop_id: int,
    start_date: date,
    end_date: date,
    exclude_task_id: Optional[int] = None
):
    conflicts = _find_prop_time_conflicts(prop_id, start_date, end_date, exclude_task_id)
    if conflicts.exists():
        conflict_tasks = _format_conflict_tasks(conflicts)
        prop = Prop.objects.get(id=prop_id)
        raise ConflictException(
            ERR_MSG_PROP_TIME_CONFLICT.format(
                code=prop.code,
                name=prop.name,
                start=start_date,
                end=end_date,
                tasks=', '.join(conflict_tasks)
            )
        )


def validate_vehicles_no_time_conflict(
    vehicle_ids: List[int],
    start_date: date,
    end_date: date,
    exclude_task_id: Optional[int] = None
):
    for vehicle_id in vehicle_ids:
        validate_vehicle_no_time_conflict(vehicle_id, start_date, end_date, exclude_task_id)


def validate_props_no_time_conflict(
    prop_items: List[Any],
    start_date: date,
    end_date: date,
    exclude_task_id: Optional[int] = None
):
    prop_ids = [item.prop_id for item in prop_items]
    for prop_id in prop_ids:
        validate_prop_no_time_conflict(prop_id, start_date, end_date, exclude_task_id)


def validate_cost_type(cost_type: str):
    if cost_type not in VALID_COST_TYPES:
        raise ValidationException(ERR_MSG_COST_TYPE_INVALID.format(cost_type=cost_type))


def validate_cost_date_in_task_range(
    expense_date: date,
    task_start_date: date,
    task_end_date: date
):
    if expense_date < task_start_date or expense_date > task_end_date:
        raise ValidationException(ERR_MSG_COST_DATE_OUT_OF_RANGE)


def validate_task_allows_cost(task_status: str):
    if task_status == 'cancelled':
        raise StatusValidationException(ERR_MSG_TASK_CANCELLED_NO_COST)


def validate_task_cost_editable(task_status: str):
    if task_status == 'cancelled':
        raise StatusValidationException(ERR_MSG_TASK_CANCELLED_COST_CANNOT_EDIT)


def validate_cost_item_not_locked_by_settlement(task: Any):
    if hasattr(task, 'settlement') and task.settlement.settlement_status in SETTLEMENT_STATUSES_LOCKED:
        raise StatusValidationException(ERR_MSG_SETTLEMENT_SUBMITTED_CANNOT_EDIT_COST)


def validate_cost_item_deletable(task: Any):
    if hasattr(task, 'settlement') and task.settlement.settlement_status in SETTLEMENT_STATUSES_LOCKED:
        raise StatusValidationException(ERR_MSG_SETTLEMENT_SUBMITTED_CANNOT_DELETE_COST)


def validate_abnormal_cost_has_remark(is_abnormal: bool, abnormal_remark: Optional[str]):
    if is_abnormal and not abnormal_remark:
        raise ValidationException(ERR_MSG_ABNORMAL_COST_REQUIRES_REMARK)


def validate_task_allows_settlement(task_status: str):
    if task_status == 'cancelled':
        raise StatusValidationException(ERR_MSG_TASK_CANCELLED_NO_SETTLEMENT)


def validate_no_existing_settlement(task: Any):
    if hasattr(task, 'settlement'):
        raise ConflictException(ERR_MSG_SETTLEMENT_ALREADY_EXISTS)


def validate_settlement_refreshable(settlement_status: str):
    if settlement_status in SETTLEMENT_STATUSES_LOCKED:
        raise StatusValidationException(ERR_MSG_SETTLEMENT_SUBMITTED_OR_CONFIRMED_CANNOT_REFRESH)


def validate_task_ready_for_settlement(task_status: str):
    if task_status in ('pending', 'in_progress'):
        raise StatusValidationException(ERR_MSG_TASK_NOT_COMPLETED_CANNOT_SUBMIT_SETTLEMENT)


def validate_abnormal_task_has_cost_note(
    task_status: str,
    abnormal_cost_note: Optional[str],
    existing_note: Optional[str]
):
    if task_status == 'abnormal' and not abnormal_cost_note and not existing_note:
        raise ValidationException(ERR_MSG_ABNORMAL_TASK_REQUIRES_COST_NOTE)


def validate_settlement_not_confirmed(settlement_status: str):
    if settlement_status == 'confirmed':
        raise StatusValidationException(ERR_MSG_SETTLEMENT_ALREADY_CONFIRMED)


def validate_settlement_confirmable(settlement_status: str):
    if settlement_status != 'submitted':
        raise StatusValidationException(ERR_MSG_SETTLEMENT_ONLY_SUBMITTED_CAN_CONFIRM)


def validate_settlement_deletable(settlement_status: str):
    if settlement_status == 'confirmed':
        raise StatusValidationException(ERR_MSG_SETTLEMENT_CONFIRMED_CANNOT_DELETE)


def validate_prop_not_scrapped(prop: Prop):
    if prop.scrap_status == 'scrapped':
        raise StatusValidationException(ERR_MSG_PROP_ALREADY_SCRAPPED)


def validate_no_pending_scrap_application(prop_id: int):
    from apps.props.models import ScrapApplication
    if ScrapApplication.objects.filter(prop_id=prop_id, status='pending').exists():
        raise ConflictException(ERR_MSG_SCRAP_APPLICATION_PENDING_EXISTS)


def validate_scrap_application_approvable(status: str):
    if status != 'pending':
        raise StatusValidationException(ERR_MSG_SCRAP_ONLY_PENDING_CAN_APPROVE)


def compute_prop_maintenance_status(prop: Prop, today: Optional[date] = None) -> str:
    today = today or date.today()
    if prop.maintenance_status == 'in_maintenance':
        return prop.maintenance_status
    if prop.next_maintenance_date:
        if prop.next_maintenance_date < today:
            return 'overdue'
        elif (prop.next_maintenance_date - today).days <= PROPS_MAINTENANCE_WARNING_DAYS:
            return 'pending'
    return prop.maintenance_status
