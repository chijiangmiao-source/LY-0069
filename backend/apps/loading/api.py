from ninja import Router
from typing import List
from django.db import transaction

from .models import LoadingRecord, UnloadingRecord, DamageRecord
from .schemas import (
    LoadingIn, LoadingOut,
    UnloadingIn, UnloadingOut,
    DamageIn, DamageOut
)
from apps.auth_app.auth import JWTAuth
from apps.common.services import (
    LoadingService,
    UnloadingService,
    DamageService,
)
from apps.common.validators import (
    get_loading_or_404,
)

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
    loading = LoadingService.create_loading(data)
    return serialize_loading(loading)


@loading_router.get('/{id}', response=LoadingOut)
def get_loading(request, id: int):
    r = LoadingRecord.objects.select_related('vehicle', 'prop').get(id=id)
    return serialize_loading(r)


@loading_router.put('/{id}', response=LoadingOut)
@transaction.atomic
def update_loading(request, id: int, data: LoadingIn):
    loading = LoadingService.update_loading(id, data)
    return serialize_loading(loading)


@loading_router.delete('/{id}')
@transaction.atomic
def delete_loading(request, id: int):
    LoadingService.delete_loading(id)
    return {'success': True}


@unloading_router.get('/list', response=List[UnloadingOut])
def list_unloading(request):
    records = UnloadingRecord.objects.select_related('vehicle', 'prop', 'loading').all()
    return [serialize_unloading(r) for r in records]


@unloading_router.post('/list', response=UnloadingOut)
@transaction.atomic
def create_unloading(request, data: UnloadingIn):
    unloading = UnloadingService.create_unloading(data)
    return serialize_unloading(unloading)


@unloading_router.get('/{id}', response=UnloadingOut)
def get_unloading(request, id: int):
    r = UnloadingRecord.objects.select_related('vehicle', 'prop', 'loading').get(id=id)
    return serialize_unloading(r)


@unloading_router.put('/{id}', response=UnloadingOut)
@transaction.atomic
def update_unloading(request, id: int, data: UnloadingIn):
    unloading = UnloadingService.update_unloading(id, data)
    return serialize_unloading(unloading)


@unloading_router.delete('/{id}')
@transaction.atomic
def delete_unloading(request, id: int):
    UnloadingService.delete_unloading(id)
    return {'success': True}


@damage_router.get('/list', response=List[DamageOut])
def list_damage(request):
    records = DamageRecord.objects.select_related('prop').all()
    return [serialize_damage(r) for r in records]


@damage_router.post('/list', response=DamageOut)
@transaction.atomic
def create_damage(request, data: DamageIn):
    damage = DamageService.create_damage(data)
    return serialize_damage(damage)


@damage_router.get('/{id}', response=DamageOut)
def get_damage(request, id: int):
    r = DamageRecord.objects.select_related('prop').get(id=id)
    return serialize_damage(r)


@damage_router.put('/{id}', response=DamageOut)
@transaction.atomic
def update_damage(request, id: int, data: DamageIn):
    damage = DamageService.update_damage(id, data)
    return serialize_damage(damage)


@damage_router.delete('/{id}')
@transaction.atomic
def delete_damage(request, id: int):
    DamageService.delete_damage(id)
    return {'success': True}
