from datetime import date, datetime
from typing import List, Optional, Any, Tuple

from django.db import transaction
from django.db.models import QuerySet

from apps.vehicles.models import Vehicle
from apps.props.models import Prop, MaintenanceRecord, ScrapApplication
from apps.loading.models import LoadingRecord, UnloadingRecord, DamageRecord
from apps.tours.models import (
    TourTask, TourTaskVehicle, TourTaskProp,
    TourCostItem, TourSettlement
)

from .validators import (
    validate_positive_quantity,
    validate_vehicle_active,
    validate_vehicle_load_capacity,
    validate_vehicle_unload_quantity,
    validate_prop_available_for_loading,
    validate_unloading_date,
    validate_no_existing_unloading,
    validate_loading_has_no_unloading,
    validate_damage_reason,
    validate_task_date_range,
    validate_performance_date_in_range,
    validate_task_editable,
    validate_task_deletable,
    validate_task_status,
    validate_task_execution_status,
    validate_task_abnormal_has_description,
    validate_vehicles_active_for_tour,
    validate_props_available_for_tour,
    validate_vehicles_no_time_conflict,
    validate_props_no_time_conflict,
    validate_cost_type,
    validate_cost_date_in_task_range,
    validate_task_allows_cost,
    validate_task_cost_editable,
    validate_cost_item_not_locked_by_settlement,
    validate_cost_item_deletable,
    validate_abnormal_cost_has_remark,
    validate_task_allows_settlement,
    validate_no_existing_settlement,
    validate_settlement_refreshable,
    validate_task_ready_for_settlement,
    validate_abnormal_task_has_cost_note,
    validate_settlement_not_confirmed,
    validate_settlement_confirmable,
    validate_settlement_deletable,
    validate_prop_not_scrapped,
    validate_no_pending_scrap_application,
    validate_scrap_application_approvable,
    get_vehicle_or_404,
    get_prop_or_404,
    get_program_or_404,
    get_loading_or_404,
)
from .exceptions import (
    ERR_MSG_VEHICLE_OVERLOAD_ON_DELETE,
    ValidationException,
    COST_TYPE_DISPLAY,
)


class VehicleService:

    @staticmethod
    def add_load(vehicle: Vehicle, quantity: int):
        vehicle.current_load += quantity
        vehicle.save()

    @staticmethod
    def remove_load(vehicle: Vehicle, quantity: int):
        vehicle.current_load -= quantity
        vehicle.save()

    @staticmethod
    def adjust_load(vehicle: Vehicle, delta: int):
        vehicle.current_load += delta
        vehicle.save()

    @staticmethod
    @transaction.atomic
    def transfer_load(
        old_vehicle: Vehicle,
        new_vehicle: Vehicle,
        quantity: int,
        new_vehicle_extra_quantity: int = 0
    ):
        old_vehicle.current_load -= quantity
        old_vehicle.save()
        new_vehicle.current_load += (quantity + new_vehicle_extra_quantity)
        new_vehicle.save()


class PropStatusService:

    @staticmethod
    def set_status(prop: Prop, status: str):
        prop.status = status
        prop.save()

    @staticmethod
    def set_loaded(prop: Prop):
        PropStatusService.set_status(prop, 'loaded')

    @staticmethod
    def set_in_store(prop: Prop):
        PropStatusService.set_status(prop, 'in_store')

    @staticmethod
    def set_damaged(prop: Prop):
        PropStatusService.set_status(prop, 'damaged')

    @staticmethod
    def set_scrapped(prop: Prop):
        prop.status = 'scrapped'
        prop.scrap_status = 'approved'
        prop.save()

    @staticmethod
    def update_maintenance_pass(prop: Prop, maintenance_date: date):
        prop.last_maintenance_date = maintenance_date
        prop.maintenance_status = 'normal'
        prop.save()

    @staticmethod
    def set_scrap_status(prop: Prop, scrap_status: str):
        prop.scrap_status = scrap_status
        prop.save()


class LoadingService:

    @staticmethod
    @transaction.atomic
    def create_loading(data: Any) -> LoadingRecord:
        validate_positive_quantity(data.loading_quantity, '装车数量')

        vehicle = get_vehicle_or_404(data.vehicle_id)
        validate_vehicle_active(vehicle)
        validate_vehicle_load_capacity(vehicle, data.loading_quantity)

        prop = get_prop_or_404(data.prop_id)
        validate_prop_available_for_loading(prop)

        loading = LoadingRecord.objects.create(**data.dict())
        loading.vehicle = vehicle
        loading.prop = prop

        VehicleService.add_load(vehicle, data.loading_quantity)
        PropStatusService.set_loaded(prop)

        return loading

    @staticmethod
    @transaction.atomic
    def update_loading(loading_id: int, data: Any) -> LoadingRecord:
        validate_positive_quantity(data.loading_quantity, '装车数量')

        loading = get_loading_or_404(loading_id)

        vehicle = get_vehicle_or_404(data.vehicle_id)
        validate_vehicle_active(vehicle)

        prop = get_prop_or_404(data.prop_id)
        validate_prop_available_for_loading(prop)

        old_vehicle_id = loading.vehicle_id
        old_prop_id = loading.prop_id
        old_quantity = loading.loading_quantity

        if old_vehicle_id != data.vehicle_id:
            validate_vehicle_load_capacity(vehicle, data.loading_quantity)
        else:
            validate_vehicle_load_capacity(
                vehicle,
                data.loading_quantity,
                old_quantity
            )

        for attr, value in data.dict().items():
            setattr(loading, attr, value)
        loading.save()
        loading.vehicle = vehicle
        loading.prop = prop

        if old_vehicle_id != data.vehicle_id:
            old_vehicle = get_vehicle_or_404(old_vehicle_id)
            VehicleService.transfer_load(old_vehicle, vehicle, old_quantity, data.loading_quantity - old_quantity)
        elif old_quantity != data.loading_quantity:
            VehicleService.adjust_load(vehicle, data.loading_quantity - old_quantity)

        if old_prop_id != data.prop_id:
            old_prop = get_prop_or_404(old_prop_id)
            PropStatusService.set_in_store(old_prop)
            PropStatusService.set_loaded(prop)

        return loading

    @staticmethod
    @transaction.atomic
    def delete_loading(loading_id: int):
        loading = get_loading_or_404(loading_id)
        validate_loading_has_no_unloading(loading)

        vehicle = loading.vehicle
        VehicleService.remove_load(vehicle, loading.loading_quantity)

        prop = loading.prop
        PropStatusService.set_in_store(prop)

        loading.delete()


class UnloadingService:

    @staticmethod
    @transaction.atomic
    def create_unloading(data: Any) -> UnloadingRecord:
        validate_positive_quantity(data.unloading_quantity, '卸车数量')

        loading = get_loading_or_404(data.loading_id)
        validate_no_existing_unloading(data.loading_id)
        validate_unloading_date(loading.loading_date, data.unloading_date)

        vehicle = get_vehicle_or_404(data.vehicle_id)
        validate_vehicle_unload_quantity(vehicle, data.unloading_quantity)

        prop = get_prop_or_404(data.prop_id)

        unloading = UnloadingRecord.objects.create(**data.dict())
        unloading.vehicle = vehicle
        unloading.prop = prop
        unloading.loading = loading

        VehicleService.remove_load(vehicle, data.unloading_quantity)
        PropStatusService.set_in_store(prop)

        return unloading

    @staticmethod
    @transaction.atomic
    def update_unloading(unloading_id: int, data: Any) -> UnloadingRecord:
        validate_positive_quantity(data.unloading_quantity, '卸车数量')

        try:
            unloading = UnloadingRecord.objects.get(id=unloading_id)
        except UnloadingRecord.DoesNotExist:
            from .exceptions import NotFoundException, ERR_MSG_UNLOADING_NOT_EXIST
            raise NotFoundException(ERR_MSG_UNLOADING_NOT_EXIST)

        loading = get_loading_or_404(data.loading_id)
        validate_unloading_date(loading.loading_date, data.unloading_date)

        if data.loading_id != unloading.loading_id:
            validate_no_existing_unloading(data.loading_id)

        vehicle = get_vehicle_or_404(data.vehicle_id)
        prop = get_prop_or_404(data.prop_id)

        old_vehicle_id = unloading.vehicle_id
        old_prop_id = unloading.prop_id
        old_quantity = unloading.unloading_quantity

        if old_vehicle_id != data.vehicle_id:
            validate_vehicle_unload_quantity(vehicle, data.unloading_quantity)
        else:
            validate_vehicle_unload_quantity(
                vehicle,
                data.unloading_quantity,
                old_quantity
            )

        for attr, value in data.dict().items():
            setattr(unloading, attr, value)
        unloading.save()
        unloading.vehicle = vehicle
        unloading.prop = prop
        unloading.loading = loading

        if old_vehicle_id != data.vehicle_id:
            old_vehicle = get_vehicle_or_404(old_vehicle_id)
            old_vehicle.current_load += old_quantity
            old_vehicle.save()
            vehicle.current_load -= data.unloading_quantity
            vehicle.save()
        elif old_quantity != data.unloading_quantity:
            vehicle.current_load -= (data.unloading_quantity - old_quantity)
            vehicle.save()

        if old_prop_id != data.prop_id:
            old_prop = get_prop_or_404(old_prop_id)
            PropStatusService.set_loaded(old_prop)
            PropStatusService.set_in_store(prop)

        return unloading

    @staticmethod
    @transaction.atomic
    def delete_unloading(unloading_id: int):
        try:
            unloading = UnloadingRecord.objects.get(id=unloading_id)
        except UnloadingRecord.DoesNotExist:
            from .exceptions import NotFoundException, ERR_MSG_UNLOADING_NOT_EXIST
            raise NotFoundException(ERR_MSG_UNLOADING_NOT_EXIST)

        vehicle = unloading.vehicle
        if vehicle.current_load + unloading.unloading_quantity > vehicle.capacity:
            raise ValidationException(
                ERR_MSG_VEHICLE_OVERLOAD_ON_DELETE.format(
                    current=vehicle.current_load,
                    capacity=vehicle.capacity
                )
            )
        VehicleService.add_load(vehicle, unloading.unloading_quantity)

        prop = unloading.prop
        PropStatusService.set_loaded(prop)

        unloading.delete()


class DamageService:

    @staticmethod
    @transaction.atomic
    def create_damage(data: Any) -> DamageRecord:
        validate_positive_quantity(data.damage_quantity, '损耗数量')
        validate_damage_reason(data.damage_reason)

        prop = get_prop_or_404(data.prop_id)

        damage = DamageRecord.objects.create(**data.dict())
        damage.prop = prop

        PropStatusService.set_damaged(prop)

        return damage

    @staticmethod
    @transaction.atomic
    def update_damage(damage_id: int, data: Any) -> DamageRecord:
        validate_positive_quantity(data.damage_quantity, '损耗数量')
        validate_damage_reason(data.damage_reason)

        try:
            damage = DamageRecord.objects.get(id=damage_id)
        except DamageRecord.DoesNotExist:
            from .exceptions import NotFoundException, ERR_MSG_DAMAGE_NOT_EXIST
            raise NotFoundException(ERR_MSG_DAMAGE_NOT_EXIST)

        prop = get_prop_or_404(data.prop_id)

        old_prop_id = damage.prop_id

        for attr, value in data.dict().items():
            setattr(damage, attr, value)
        damage.save()
        damage.prop = prop

        if old_prop_id != data.prop_id:
            old_prop = get_prop_or_404(old_prop_id)
            PropStatusService.set_in_store(old_prop)
            PropStatusService.set_damaged(prop)

        return damage

    @staticmethod
    @transaction.atomic
    def delete_damage(damage_id: int):
        try:
            damage = DamageRecord.objects.get(id=damage_id)
        except DamageRecord.DoesNotExist:
            from .exceptions import NotFoundException, ERR_MSG_DAMAGE_NOT_EXIST
            raise NotFoundException(ERR_MSG_DAMAGE_NOT_EXIST)

        prop = damage.prop
        PropStatusService.set_in_store(prop)

        damage.delete()


class MaintenanceService:

    @staticmethod
    @transaction.atomic
    def create_maintenance(data: Any) -> MaintenanceRecord:
        prop = get_prop_or_404(data.prop_id)
        record = MaintenanceRecord.objects.create(**data.dict())
        record.prop = prop
        if data.result == 'pass':
            PropStatusService.update_maintenance_pass(prop, data.maintenance_date)
        return record

    @staticmethod
    @transaction.atomic
    def update_maintenance(record_id: int, data: Any) -> MaintenanceRecord:
        try:
            record = MaintenanceRecord.objects.get(id=record_id)
        except MaintenanceRecord.DoesNotExist:
            from .exceptions import NotFoundException, ERR_MSG_MAINTENANCE_NOT_EXIST
            raise NotFoundException(ERR_MSG_MAINTENANCE_NOT_EXIST)

        prop = get_prop_or_404(data.prop_id)
        for attr, value in data.dict().items():
            setattr(record, attr, value)
        record.save()
        record.prop = prop
        if data.result == 'pass' and record.prop_id == data.prop_id:
            PropStatusService.update_maintenance_pass(prop, data.maintenance_date)
        return record

    @staticmethod
    def delete_maintenance(record_id: int):
        try:
            record = MaintenanceRecord.objects.get(id=record_id)
        except MaintenanceRecord.DoesNotExist:
            from .exceptions import NotFoundException, ERR_MSG_MAINTENANCE_NOT_EXIST
            raise NotFoundException(ERR_MSG_MAINTENANCE_NOT_EXIST)
        record.delete()


class ScrapService:

    @staticmethod
    @transaction.atomic
    def create_application(data: Any) -> ScrapApplication:
        prop = get_prop_or_404(data.prop_id)
        validate_prop_not_scrapped(prop)
        validate_no_pending_scrap_application(data.prop_id)

        record = ScrapApplication.objects.create(**data.dict())
        record.prop = prop
        PropStatusService.set_scrap_status(prop, 'pending')
        return record

    @staticmethod
    @transaction.atomic
    def approve_application(application_id: int, data: Any) -> ScrapApplication:
        try:
            record = ScrapApplication.objects.get(id=application_id)
        except ScrapApplication.DoesNotExist:
            from .exceptions import NotFoundException, ERR_MSG_SCRAP_NOT_EXIST
            raise NotFoundException(ERR_MSG_SCRAP_NOT_EXIST)

        validate_scrap_application_approvable(record.status)
        record.status = 'approved'
        record.approver = data.approver
        record.approve_date = data.approve_date
        record.approve_remark = data.approve_remark
        record.save()

        prop = record.prop
        PropStatusService.set_scrapped(prop)

        return record

    @staticmethod
    @transaction.atomic
    def reject_application(application_id: int, data: Any) -> ScrapApplication:
        try:
            record = ScrapApplication.objects.get(id=application_id)
        except ScrapApplication.DoesNotExist:
            from .exceptions import NotFoundException, ERR_MSG_SCRAP_NOT_EXIST
            raise NotFoundException(ERR_MSG_SCRAP_NOT_EXIST)

        validate_scrap_application_approvable(record.status)
        record.status = 'rejected'
        record.approver = data.approver
        record.approve_date = data.approve_date
        record.approve_remark = data.approve_remark
        record.save()

        prop = record.prop
        PropStatusService.set_scrap_status(prop, 'active')

        return record

    @staticmethod
    @transaction.atomic
    def delete_application(application_id: int):
        try:
            record = ScrapApplication.objects.get(id=application_id)
        except ScrapApplication.DoesNotExist:
            from .exceptions import NotFoundException, ERR_MSG_SCRAP_NOT_EXIST
            raise NotFoundException(ERR_MSG_SCRAP_NOT_EXIST)

        if record.status == 'pending':
            prop = record.prop
            PropStatusService.set_scrap_status(prop, 'active')

        record.delete()


class TourTaskService:

    @staticmethod
    def _assign_vehicles(task: TourTask, vehicle_ids: List[int]):
        TourTaskVehicle.objects.filter(tour_task=task).delete()
        for vehicle_id in vehicle_ids:
            TourTaskVehicle.objects.create(tour_task=task, vehicle_id=vehicle_id)

    @staticmethod
    def _assign_props(task: TourTask, prop_items: List[Any]):
        TourTaskProp.objects.filter(tour_task=task).delete()
        for prop_item in prop_items:
            TourTaskProp.objects.create(
                tour_task=task,
                prop_id=prop_item.prop_id,
                quantity=prop_item.quantity,
            )

    @staticmethod
    @transaction.atomic
    def create_task(data: Any) -> TourTask:
        validate_task_date_range(data.start_date, data.end_date)
        validate_performance_date_in_range(data.performance_date, data.start_date, data.end_date)

        program = get_program_or_404(data.program_id)

        validate_vehicles_active_for_tour(data.vehicle_ids)
        validate_props_available_for_tour(data.props)
        validate_vehicles_no_time_conflict(data.vehicle_ids, data.start_date, data.end_date)
        validate_props_no_time_conflict(data.props, data.start_date, data.end_date)

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

        TourTaskService._assign_vehicles(task, data.vehicle_ids)
        TourTaskService._assign_props(task, data.props)

        return task

    @staticmethod
    @transaction.atomic
    def update_task(task_id: int, data: Any) -> TourTask:
        try:
            task = TourTask.objects.select_related('program').get(id=task_id)
        except TourTask.DoesNotExist:
            from .exceptions import NotFoundException, ERR_MSG_TASK_NOT_EXIST
            raise NotFoundException(ERR_MSG_TASK_NOT_EXIST)

        validate_task_editable(task.status)
        validate_task_date_range(data.start_date, data.end_date)
        validate_performance_date_in_range(data.performance_date, data.start_date, data.end_date)

        program = get_program_or_404(data.program_id)

        validate_vehicles_active_for_tour(data.vehicle_ids)
        validate_props_available_for_tour(data.props)
        validate_vehicles_no_time_conflict(data.vehicle_ids, data.start_date, data.end_date, task_id)
        validate_props_no_time_conflict(data.props, data.start_date, data.end_date, task_id)

        task.program = program
        task.performance_date = data.performance_date
        task.city = data.city
        task.venue = data.venue
        task.person_in_charge = data.person_in_charge
        task.start_date = data.start_date
        task.end_date = data.end_date
        task.remark = data.remark
        task.save()

        TourTaskService._assign_vehicles(task, data.vehicle_ids)
        TourTaskService._assign_props(task, data.props)

        return task

    @staticmethod
    @transaction.atomic
    def update_task_status(task_id: int, data: Any) -> TourTask:
        try:
            task = TourTask.objects.select_related('program').get(id=task_id)
        except TourTask.DoesNotExist:
            from .exceptions import NotFoundException, ERR_MSG_TASK_NOT_EXIST
            raise NotFoundException(ERR_MSG_TASK_NOT_EXIST)

        validate_task_status(data.status)

        if data.status == 'in_progress':
            if data.execution_status:
                validate_task_execution_status(data.execution_status)

        validate_task_abnormal_has_description(data.status, data.abnormal_situation)

        task.status = data.status
        if data.execution_status:
            task.execution_status = data.execution_status
        if data.abnormal_situation is not None:
            task.abnormal_situation = data.abnormal_situation
        if data.completion_result is not None:
            task.completion_result = data.completion_result

        if data.status == 'completed' and not task.completion_result:
            task.completion_result = '任务已顺利完成'

        task.save()
        return task

    @staticmethod
    @transaction.atomic
    def delete_task(task_id: int):
        try:
            task = TourTask.objects.get(id=task_id)
        except TourTask.DoesNotExist:
            from .exceptions import NotFoundException, ERR_MSG_TASK_NOT_EXIST
            raise NotFoundException(ERR_MSG_TASK_NOT_EXIST)

        validate_task_deletable(task.status)

        TourTaskVehicle.objects.filter(tour_task=task).delete()
        TourTaskProp.objects.filter(tour_task=task).delete()
        task.delete()


class CostItemService:

    @staticmethod
    def _is_abnormal_cost(cost_type: str, is_abnormal_cost: bool) -> bool:
        return is_abnormal_cost or cost_type == 'abnormal_handling'

    @staticmethod
    @transaction.atomic
    def create_cost_item(data: Any) -> TourCostItem:
        try:
            task = TourTask.objects.get(id=data.tour_task_id)
        except TourTask.DoesNotExist:
            from .exceptions import NotFoundException, ERR_MSG_TASK_NOT_EXIST
            raise NotFoundException(ERR_MSG_TASK_NOT_EXIST)

        validate_task_allows_cost(task.status)
        validate_cost_type(data.cost_type)
        from .validators import validate_non_negative_amount
        validate_non_negative_amount(data.amount)
        validate_cost_date_in_task_range(data.expense_date, task.start_date, task.end_date)

        is_abnormal = CostItemService._is_abnormal_cost(data.cost_type, data.is_abnormal_cost)
        validate_abnormal_cost_has_remark(is_abnormal, data.abnormal_remark)

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
        return item

    @staticmethod
    @transaction.atomic
    def update_cost_item(item_id: int, data: Any) -> TourCostItem:
        try:
            item = TourCostItem.objects.select_related('tour_task').get(id=item_id)
        except TourCostItem.DoesNotExist:
            from .exceptions import NotFoundException, ERR_MSG_COST_ITEM_NOT_EXIST
            raise NotFoundException(ERR_MSG_COST_ITEM_NOT_EXIST)

        task = item.tour_task
        validate_task_cost_editable(task.status)
        validate_cost_item_not_locked_by_settlement(task)
        validate_cost_type(data.cost_type)
        from .validators import validate_non_negative_amount
        validate_non_negative_amount(data.amount)
        validate_cost_date_in_task_range(data.expense_date, task.start_date, task.end_date)

        is_abnormal = CostItemService._is_abnormal_cost(data.cost_type, data.is_abnormal_cost)
        validate_abnormal_cost_has_remark(is_abnormal, data.abnormal_remark)

        item.cost_type = data.cost_type
        item.amount = data.amount
        item.description = data.description
        item.expense_date = data.expense_date
        item.operator = data.operator
        item.receipt_no = data.receipt_no
        item.is_abnormal_cost = is_abnormal
        item.abnormal_remark = data.abnormal_remark
        item.save()
        return item

    @staticmethod
    @transaction.atomic
    def delete_cost_item(item_id: int):
        try:
            item = TourCostItem.objects.select_related('tour_task').get(id=item_id)
        except TourCostItem.DoesNotExist:
            from .exceptions import NotFoundException, ERR_MSG_COST_ITEM_NOT_EXIST
            raise NotFoundException(ERR_MSG_COST_ITEM_NOT_EXIST)

        task = item.tour_task
        validate_cost_item_deletable(task)

        item.delete()


class SettlementService:

    @staticmethod
    def _generate_settlement_no() -> str:
        today = datetime.now()
        prefix = f'JS{today.strftime("%Y%m%d")}'
        count = TourSettlement.objects.filter(settlement_no__startswith=prefix).count() + 1
        return f'{prefix}{count:04d}'

    @staticmethod
    @transaction.atomic
    def create_settlement(data: Any) -> TourSettlement:
        try:
            task = TourTask.objects.select_related('program').get(id=data.tour_task_id)
        except TourTask.DoesNotExist:
            from .exceptions import NotFoundException, ERR_MSG_TASK_NOT_EXIST
            raise NotFoundException(ERR_MSG_TASK_NOT_EXIST)

        validate_task_allows_settlement(task.status)
        validate_no_existing_settlement(task)

        settlement_no = SettlementService._generate_settlement_no()
        s = TourSettlement.objects.create(
            tour_task=task,
            settlement_no=settlement_no,
            remark=data.remark,
        )
        s.aggregate_from_cost_items()
        s.save()
        return s

    @staticmethod
    @transaction.atomic
    def refresh_settlement(settlement_id: int) -> TourSettlement:
        try:
            s = TourSettlement.objects.select_related('tour_task').get(id=settlement_id)
        except TourSettlement.DoesNotExist:
            from .exceptions import NotFoundException, ERR_MSG_SETTLEMENT_NOT_EXIST
            raise NotFoundException(ERR_MSG_SETTLEMENT_NOT_EXIST)

        validate_settlement_refreshable(s.settlement_status)

        s.aggregate_from_cost_items()
        s.save()
        return s

    @staticmethod
    @transaction.atomic
    def submit_settlement(settlement_id: int, data: Any, username: Optional[str] = None) -> TourSettlement:
        try:
            s = TourSettlement.objects.select_related('tour_task').get(id=settlement_id)
        except TourSettlement.DoesNotExist:
            from .exceptions import NotFoundException, ERR_MSG_SETTLEMENT_NOT_EXIST
            raise NotFoundException(ERR_MSG_SETTLEMENT_NOT_EXIST)

        task = s.tour_task
        validate_task_ready_for_settlement(task.status)
        validate_abnormal_task_has_cost_note(
            task.status,
            data.abnormal_cost_note,
            s.abnormal_cost_note
        )
        validate_settlement_not_confirmed(s.settlement_status)

        s.aggregate_from_cost_items()
        if data.abnormal_cost_note:
            s.abnormal_cost_note = data.abnormal_cost_note
        if data.remark:
            s.remark = data.remark
        s.settlement_status = 'submitted'
        s.settlement_date = date.today()
        s.settler = username
        s.save()
        return s

    @staticmethod
    @transaction.atomic
    def confirm_settlement(settlement_id: int) -> TourSettlement:
        try:
            s = TourSettlement.objects.select_related('tour_task').get(id=settlement_id)
        except TourSettlement.DoesNotExist:
            from .exceptions import NotFoundException, ERR_MSG_SETTLEMENT_NOT_EXIST
            raise NotFoundException(ERR_MSG_SETTLEMENT_NOT_EXIST)

        validate_settlement_confirmable(s.settlement_status)

        s.settlement_status = 'confirmed'
        s.save()
        return s

    @staticmethod
    @transaction.atomic
    def delete_settlement(settlement_id: int):
        try:
            s = TourSettlement.objects.get(id=settlement_id)
        except TourSettlement.DoesNotExist:
            from .exceptions import NotFoundException, ERR_MSG_SETTLEMENT_NOT_EXIST
            raise NotFoundException(ERR_MSG_SETTLEMENT_NOT_EXIST)

        validate_settlement_deletable(s.settlement_status)

        s.delete()
