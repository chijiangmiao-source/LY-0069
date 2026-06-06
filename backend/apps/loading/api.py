from ninja import Router
from ninja.errors import HttpError
from typing import List
from django.db import transaction

from .models import LoadingRecord, UnloadingRecord, DamageRecord
from .schemas import (
    LoadingIn, LoadingOut,
    UnloadingIn, UnloadingOut,
    DamageIn, DamageOut
)
from apps.vehicles.models import Vehicle
from apps.props.models import Prop
from apps.auth_app.auth import JWTAuth

loading_router = Router(tags=['装车登记'], auth=JWTAuth())
unloading_router = Router(tags=['卸车归库'], auth=JWTAuth())
damage_router = Router(tags=['损耗记录'], auth=JWTAuth())


def serialize_loading(r: LoadingRecord) -> dict:
    return {
        'id': r.id,
        'vehicle_id': r.vehicle_id,
        'vehicle_code': r.vehicle.code,
        'prop_id': r.prop_id,
        'prop_code': r.prop.code,
        'prop_name': r.prop.name,
        'loading_date': r.loading_date,
        'loading_quantity': r.loading_quantity,
        'operator': r.operator,
        'remark': r.remark,
        'created_at': r.created_at,
    }


def serialize_unloading(r: UnloadingRecord) -> dict:
    return {
        'id': r.id,
        'loading_id': r.loading_id,
        'vehicle_id': r.vehicle_id,
        'vehicle_code': r.vehicle.code,
        'prop_id': r.prop_id,
        'prop_code': r.prop.code,
        'prop_name': r.prop.name,
        'unloading_date': r.unloading_date,
        'unloading_quantity': r.unloading_quantity,
        'operator': r.operator,
        'remark': r.remark,
        'created_at': r.created_at,
    }


def serialize_damage(r: DamageRecord) -> dict:
    return {
        'id': r.id,
        'prop_id': r.prop_id,
        'prop_code': r.prop.code,
        'prop_name': r.prop.name,
        'damage_date': r.damage_date,
        'damage_quantity': r.damage_quantity,
        'damage_reason': r.damage_reason,
        'handler': r.handler,
        'remark': r.remark,
        'created_at': r.created_at,
    }


@loading_router.get('/list', response=List[LoadingOut])
def list_loading(request):
    records = LoadingRecord.objects.select_related('vehicle', 'prop').all()
    return [serialize_loading(r) for r in records]


@loading_router.post('/list', response=LoadingOut)
@transaction.atomic
def create_loading(request, data: LoadingIn):
    if data.loading_quantity <= 0:
        raise HttpError(400, '装车数量必须大于0')

    try:
        vehicle = Vehicle.objects.get(id=data.vehicle_id)
    except Vehicle.DoesNotExist:
        raise HttpError(400, '车辆不存在')

    if vehicle.status == 'inactive':
        raise HttpError(400, '停用车辆不能装车')

    if vehicle.current_load + data.loading_quantity > vehicle.capacity:
        raise HttpError(400, f'车辆装载量将超过承载容量（当前: {vehicle.current_load}, 承载: {vehicle.capacity}）')

    try:
        prop = Prop.objects.get(id=data.prop_id)
    except Prop.DoesNotExist:
        raise HttpError(400, '道具不存在')

    loading = LoadingRecord.objects.create(**data.dict())
    loading.vehicle = vehicle
    loading.prop = prop

    vehicle.current_load += data.loading_quantity
    vehicle.save()

    prop.status = 'loaded'
    prop.save()

    return serialize_loading(loading)


@loading_router.get('/{id}', response=LoadingOut)
def get_loading(request, id: int):
    try:
        r = LoadingRecord.objects.select_related('vehicle', 'prop').get(id=id)
    except LoadingRecord.DoesNotExist:
        raise HttpError(404, '装车记录不存在')
    return serialize_loading(r)


@loading_router.put('/{id}', response=LoadingOut)
@transaction.atomic
def update_loading(request, id: int, data: LoadingIn):
    if data.loading_quantity <= 0:
        raise HttpError(400, '装车数量必须大于0')

    try:
        loading = LoadingRecord.objects.get(id=id)
    except LoadingRecord.DoesNotExist:
        raise HttpError(404, '装车记录不存在')

    try:
        vehicle = Vehicle.objects.get(id=data.vehicle_id)
    except Vehicle.DoesNotExist:
        raise HttpError(400, '车辆不存在')

    if vehicle.status == 'inactive':
        raise HttpError(400, '停用车辆不能装车')

    try:
        prop = Prop.objects.get(id=data.prop_id)
    except Prop.DoesNotExist:
        raise HttpError(400, '道具不存在')

    old_vehicle_id = loading.vehicle_id
    old_prop_id = loading.prop_id
    old_quantity = loading.loading_quantity

    if old_vehicle_id != data.vehicle_id:
        if vehicle.current_load + data.loading_quantity > vehicle.capacity:
            raise HttpError(400, f'车辆装载量将超过承载容量（当前: {vehicle.current_load}, 承载: {vehicle.capacity}）')
    else:
        new_load = vehicle.current_load - old_quantity + data.loading_quantity
        if new_load > vehicle.capacity:
            raise HttpError(400, f'车辆装载量将超过承载容量（调整后: {new_load}, 承载: {vehicle.capacity}）')

    for attr, value in data.dict().items():
        setattr(loading, attr, value)
    loading.save()
    loading.vehicle = vehicle
    loading.prop = prop

    if old_vehicle_id != data.vehicle_id:
        old_vehicle = Vehicle.objects.get(id=old_vehicle_id)
        old_vehicle.current_load -= old_quantity
        old_vehicle.save()
        vehicle.current_load += data.loading_quantity
        vehicle.save()
    elif old_quantity != data.loading_quantity:
        vehicle.current_load += (data.loading_quantity - old_quantity)
        vehicle.save()

    if old_prop_id != data.prop_id:
        old_prop = Prop.objects.get(id=old_prop_id)
        old_prop.status = 'in_store'
        old_prop.save()
        prop.status = 'loaded'
        prop.save()

    return serialize_loading(loading)


@loading_router.delete('/{id}')
@transaction.atomic
def delete_loading(request, id: int):
    try:
        loading = LoadingRecord.objects.get(id=id)
    except LoadingRecord.DoesNotExist:
        raise HttpError(404, '装车记录不存在')

    if hasattr(loading, 'unloading_record'):
        raise HttpError(400, '该装车记录已有对应的卸车记录，无法删除')

    vehicle = loading.vehicle
    vehicle.current_load -= loading.loading_quantity
    vehicle.save()

    prop = loading.prop
    prop.status = 'in_store'
    prop.save()

    loading.delete()
    return {'success': True}


@unloading_router.get('/list', response=List[UnloadingOut])
def list_unloading(request):
    records = UnloadingRecord.objects.select_related('vehicle', 'prop', 'loading').all()
    return [serialize_unloading(r) for r in records]


@unloading_router.post('/list', response=UnloadingOut)
@transaction.atomic
def create_unloading(request, data: UnloadingIn):
    if data.unloading_quantity <= 0:
        raise HttpError(400, '卸车数量必须大于0')

    try:
        loading = LoadingRecord.objects.get(id=data.loading_id)
    except LoadingRecord.DoesNotExist:
        raise HttpError(400, '装车记录不存在')

    if UnloadingRecord.objects.filter(loading_id=data.loading_id).exists():
        raise HttpError(400, '该装车记录已存在卸车记录')

    if data.unloading_date < loading.loading_date:
        raise HttpError(400, '卸车日期不能早于装车日期')

    try:
        vehicle = Vehicle.objects.get(id=data.vehicle_id)
    except Vehicle.DoesNotExist:
        raise HttpError(400, '车辆不存在')

    if vehicle.current_load - data.unloading_quantity < 0:
        raise HttpError(400, f'卸车数量超过车辆当前装载量（当前装载: {vehicle.current_load}）')

    try:
        prop = Prop.objects.get(id=data.prop_id)
    except Prop.DoesNotExist:
        raise HttpError(400, '道具不存在')

    unloading = UnloadingRecord.objects.create(**data.dict())
    unloading.vehicle = vehicle
    unloading.prop = prop
    unloading.loading = loading

    vehicle.current_load -= data.unloading_quantity
    vehicle.save()

    prop.status = 'in_store'
    prop.save()

    return serialize_unloading(unloading)


@unloading_router.get('/{id}', response=UnloadingOut)
def get_unloading(request, id: int):
    try:
        r = UnloadingRecord.objects.select_related('vehicle', 'prop', 'loading').get(id=id)
    except UnloadingRecord.DoesNotExist:
        raise HttpError(404, '卸车记录不存在')
    return serialize_unloading(r)


@unloading_router.put('/{id}', response=UnloadingOut)
@transaction.atomic
def update_unloading(request, id: int, data: UnloadingIn):
    if data.unloading_quantity <= 0:
        raise HttpError(400, '卸车数量必须大于0')

    try:
        unloading = UnloadingRecord.objects.get(id=id)
    except UnloadingRecord.DoesNotExist:
        raise HttpError(404, '卸车记录不存在')

    try:
        loading = LoadingRecord.objects.get(id=data.loading_id)
    except LoadingRecord.DoesNotExist:
        raise HttpError(400, '装车记录不存在')

    if data.unloading_date < loading.loading_date:
        raise HttpError(400, '卸车日期不能早于装车日期')

    if data.loading_id != unloading.loading_id and UnloadingRecord.objects.filter(loading_id=data.loading_id).exists():
        raise HttpError(400, '该装车记录已存在卸车记录')

    try:
        vehicle = Vehicle.objects.get(id=data.vehicle_id)
    except Vehicle.DoesNotExist:
        raise HttpError(400, '车辆不存在')

    try:
        prop = Prop.objects.get(id=data.prop_id)
    except Prop.DoesNotExist:
        raise HttpError(400, '道具不存在')

    old_vehicle_id = unloading.vehicle_id
    old_prop_id = unloading.prop_id
    old_quantity = unloading.unloading_quantity

    if old_vehicle_id != data.vehicle_id:
        if vehicle.current_load - data.unloading_quantity < 0:
            raise HttpError(400, f'卸车数量超过车辆当前装载量（当前装载: {vehicle.current_load}）')
    else:
        new_load = vehicle.current_load + old_quantity - data.unloading_quantity
        if new_load < 0:
            raise HttpError(400, f'调整后车辆装载量将为负数（调整后: {new_load}）')

    for attr, value in data.dict().items():
        setattr(unloading, attr, value)
    unloading.save()
    unloading.vehicle = vehicle
    unloading.prop = prop
    unloading.loading = loading

    if old_vehicle_id != data.vehicle_id:
        old_vehicle = Vehicle.objects.get(id=old_vehicle_id)
        old_vehicle.current_load += old_quantity
        old_vehicle.save()
        vehicle.current_load -= data.unloading_quantity
        vehicle.save()
    elif old_quantity != data.unloading_quantity:
        vehicle.current_load -= (data.unloading_quantity - old_quantity)
        vehicle.save()

    if old_prop_id != data.prop_id:
        old_prop = Prop.objects.get(id=old_prop_id)
        old_prop.status = 'loaded'
        old_prop.save()
        prop.status = 'in_store'
        prop.save()

    return serialize_unloading(unloading)


@unloading_router.delete('/{id}')
@transaction.atomic
def delete_unloading(request, id: int):
    try:
        unloading = UnloadingRecord.objects.get(id=id)
    except UnloadingRecord.DoesNotExist:
        raise HttpError(404, '卸车记录不存在')

    vehicle = unloading.vehicle
    if vehicle.current_load + unloading.unloading_quantity > vehicle.capacity:
        raise HttpError(400, f'删除该卸车记录将导致车辆装载量超过容量（当前: {vehicle.current_load}, 容量: {vehicle.capacity}）')
    vehicle.current_load += unloading.unloading_quantity
    vehicle.save()

    prop = unloading.prop
    prop.status = 'loaded'
    prop.save()

    unloading.delete()
    return {'success': True}


@damage_router.get('/list', response=List[DamageOut])
def list_damage(request):
    records = DamageRecord.objects.select_related('prop').all()
    return [serialize_damage(r) for r in records]


@damage_router.post('/list', response=DamageOut)
@transaction.atomic
def create_damage(request, data: DamageIn):
    if data.damage_quantity <= 0:
        raise HttpError(400, '损耗数量必须大于0')

    if not data.damage_reason or data.damage_reason.strip() == '':
        raise HttpError(400, '损耗原因必须填写')

    try:
        prop = Prop.objects.get(id=data.prop_id)
    except Prop.DoesNotExist:
        raise HttpError(400, '道具不存在')

    damage = DamageRecord.objects.create(**data.dict())
    damage.prop = prop

    prop.status = 'damaged'
    prop.save()

    return serialize_damage(damage)


@damage_router.get('/{id}', response=DamageOut)
def get_damage(request, id: int):
    try:
        r = DamageRecord.objects.select_related('prop').get(id=id)
    except DamageRecord.DoesNotExist:
        raise HttpError(404, '损耗记录不存在')
    return serialize_damage(r)


@damage_router.put('/{id}', response=DamageOut)
@transaction.atomic
def update_damage(request, id: int, data: DamageIn):
    if data.damage_quantity <= 0:
        raise HttpError(400, '损耗数量必须大于0')

    try:
        damage = DamageRecord.objects.get(id=id)
    except DamageRecord.DoesNotExist:
        raise HttpError(404, '损耗记录不存在')

    if not data.damage_reason or data.damage_reason.strip() == '':
        raise HttpError(400, '损耗原因必须填写')

    try:
        prop = Prop.objects.get(id=data.prop_id)
    except Prop.DoesNotExist:
        raise HttpError(400, '道具不存在')

    old_prop_id = damage.prop_id

    for attr, value in data.dict().items():
        setattr(damage, attr, value)
    damage.save()
    damage.prop = prop

    if old_prop_id != data.prop_id:
        old_prop = Prop.objects.get(id=old_prop_id)
        old_prop.status = 'in_store'
        old_prop.save()
        prop.status = 'damaged'
        prop.save()

    return serialize_damage(damage)


@damage_router.delete('/{id}')
@transaction.atomic
def delete_damage(request, id: int):
    try:
        damage = DamageRecord.objects.get(id=id)
    except DamageRecord.DoesNotExist:
        raise HttpError(404, '损耗记录不存在')

    prop = damage.prop
    prop.status = 'in_store'
    prop.save()

    damage.delete()
    return {'success': True}
