from typing import List
from ninja import Router, Query
from ninja.errors import HttpError
from django.db.models import Q
from django.db import transaction
from datetime import date

from apps.auth_app.auth import JWTAuth
from .models import Prop, MaintenanceRecord, ScrapApplication
from .schemas import (
    PropIn, PropOut, PropFilter,
    MaintenanceRecordIn, MaintenanceRecordOut,
    ScrapApplicationIn, ScrapApplicationApprove, ScrapApplicationOut
)
from apps.common.services import (
    MaintenanceService,
    ScrapService,
)
from apps.common.validators import (
    get_prop_or_404,
    compute_prop_maintenance_status,
)
from apps.common.exceptions import (
    ERR_MSG_PROP_CODE_ALREADY_EXISTS,
)

router = Router(tags=['道具档案'], auth=JWTAuth())
maintenance_router = Router(tags=['维保记录'], auth=JWTAuth())
scrap_router = Router(tags=['报废管理'], auth=JWTAuth())


def serialize_prop(prop: Prop) -> dict:
    return {
        'id': prop.id,
        'code': prop.code,
        'name': prop.name,
        'program_id': prop.program_id_id,
        'program_name': prop.program_id.name if prop.program_id else '',
        'material': prop.material,
        'status': prop.status,
        'location': prop.location,
        'maintenance_cycle_days': prop.maintenance_cycle_days,
        'last_maintenance_date': prop.last_maintenance_date,
        'next_maintenance_date': prop.next_maintenance_date,
        'maintenance_status': prop.maintenance_status,
        'scrap_status': prop.scrap_status,
        'created_at': prop.created_at,
        'updated_at': prop.updated_at,
    }


def serialize_maintenance(r: MaintenanceRecord) -> dict:
    return {
        'id': r.id,
        'prop_id': r.prop_id,
        'prop_code': r.prop.code,
        'prop_name': r.prop.name,
        'type': r.type,
        'maintenance_date': r.maintenance_date,
        'description': r.description,
        'operator': r.operator,
        'result': r.result,
        'cost': r.cost,
        'remark': r.remark,
        'created_at': r.created_at,
    }


def serialize_scrap(r: ScrapApplication) -> dict:
    return {
        'id': r.id,
        'prop_id': r.prop_id,
        'prop_code': r.prop.code,
        'prop_name': r.prop.name,
        'applicant': r.applicant,
        'apply_date': r.apply_date,
        'reason': r.reason,
        'status': r.status,
        'approver': r.approver,
        'approve_date': r.approve_date,
        'approve_remark': r.approve_remark,
        'created_at': r.created_at,
    }


@router.get('', response=List[PropOut])
def list_props(request, filters: PropFilter = Query(...)):
    qs = Prop.objects.select_related('program_id').all()
    if filters.keyword:
        qs = qs.filter(
            Q(code__icontains=filters.keyword) |
            Q(name__icontains=filters.keyword) |
            Q(material__icontains=filters.keyword)
        )
    if filters.program_id:
        qs = qs.filter(program_id=filters.program_id)
    if filters.status:
        qs = qs.filter(status=filters.status)
    if filters.maintenance_status:
        qs = qs.filter(maintenance_status=filters.maintenance_status)
    if filters.scrap_status:
        qs = qs.filter(scrap_status=filters.scrap_status)
    today = date.today()
    result = []
    for prop in qs:
        prop.maintenance_status = compute_prop_maintenance_status(prop, today)
        result.append(serialize_prop(prop))
    return result


@router.get('/{prop_id}', response=PropOut)
def get_prop(request, prop_id: int):
    prop = Prop.objects.select_related('program_id').get(id=prop_id)
    return serialize_prop(prop)


@router.post('', response=PropOut)
def create_prop(request, data: PropIn):
    if Prop.objects.filter(code=data.code).exists():
        raise HttpError(400, ERR_MSG_PROP_CODE_ALREADY_EXISTS)
    prop = Prop.objects.create(**data.dict())
    prop = Prop.objects.select_related('program_id').get(id=prop.id)
    return serialize_prop(prop)


@router.put('/{prop_id}', response=PropOut)
def update_prop(request, prop_id: int, data: PropIn):
    prop = get_prop_or_404(prop_id)
    if data.code != prop.code and Prop.objects.filter(code=data.code).exists():
        raise HttpError(400, ERR_MSG_PROP_CODE_ALREADY_EXISTS)
    for attr, value in data.dict().items():
        setattr(prop, attr, value)
    prop.save()
    prop = Prop.objects.select_related('program_id').get(id=prop.id)
    return serialize_prop(prop)


@router.delete('/{prop_id}')
def delete_prop(request, prop_id: int):
    prop = get_prop_or_404(prop_id)
    prop.delete()
    return {'success': True}


@maintenance_router.get('/list', response=List[MaintenanceRecordOut])
def list_maintenance(request, prop_id: int = None):
    qs = MaintenanceRecord.objects.select_related('prop').all()
    if prop_id:
        qs = qs.filter(prop_id=prop_id)
    return [serialize_maintenance(r) for r in qs]


@maintenance_router.post('/list', response=MaintenanceRecordOut)
@transaction.atomic
def create_maintenance(request, data: MaintenanceRecordIn):
    record = MaintenanceService.create_maintenance(data)
    return serialize_maintenance(record)


@maintenance_router.get('/{id}', response=MaintenanceRecordOut)
def get_maintenance(request, id: int):
    try:
        r = MaintenanceRecord.objects.select_related('prop').get(id=id)
    except MaintenanceRecord.DoesNotExist:
        from apps.common.exceptions import NotFoundException, ERR_MSG_MAINTENANCE_NOT_EXIST
        raise NotFoundException(ERR_MSG_MAINTENANCE_NOT_EXIST)
    return serialize_maintenance(r)


@maintenance_router.put('/{id}', response=MaintenanceRecordOut)
@transaction.atomic
def update_maintenance(request, id: int, data: MaintenanceRecordIn):
    record = MaintenanceService.update_maintenance(id, data)
    return serialize_maintenance(record)


@maintenance_router.delete('/{id}')
def delete_maintenance(request, id: int):
    MaintenanceService.delete_maintenance(id)
    return {'success': True}


@scrap_router.get('/list', response=List[ScrapApplicationOut])
def list_scrap(request, prop_id: int = None, status: str = None):
    qs = ScrapApplication.objects.select_related('prop').all()
    if prop_id:
        qs = qs.filter(prop_id=prop_id)
    if status:
        qs = qs.filter(status=status)
    return [serialize_scrap(r) for r in qs]


@scrap_router.post('/list', response=ScrapApplicationOut)
@transaction.atomic
def create_scrap(request, data: ScrapApplicationIn):
    record = ScrapService.create_application(data)
    return serialize_scrap(record)


@scrap_router.get('/{id}', response=ScrapApplicationOut)
def get_scrap(request, id: int):
    try:
        r = ScrapApplication.objects.select_related('prop').get(id=id)
    except ScrapApplication.DoesNotExist:
        from apps.common.exceptions import NotFoundException, ERR_MSG_SCRAP_NOT_EXIST
        raise NotFoundException(ERR_MSG_SCRAP_NOT_EXIST)
    return serialize_scrap(r)


@scrap_router.post('/{id}/approve', response=ScrapApplicationOut)
@transaction.atomic
def approve_scrap(request, id: int, data: ScrapApplicationApprove):
    record = ScrapService.approve_application(id, data)
    return serialize_scrap(record)


@scrap_router.post('/{id}/reject', response=ScrapApplicationOut)
@transaction.atomic
def reject_scrap(request, id: int, data: ScrapApplicationApprove):
    record = ScrapService.reject_application(id, data)
    return serialize_scrap(record)


@scrap_router.delete('/{id}')
@transaction.atomic
def delete_scrap(request, id: int):
    ScrapService.delete_application(id)
    return {'success': True}
