from typing import List
from ninja import Router, Query
from ninja.errors import HttpError
from django.db.models import Q

from apps.auth_app.auth import JWTAuth
from .models import Prop
from .schemas import PropIn, PropOut, PropFilter

router = Router(tags=['道具档案'], auth=JWTAuth())


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
    result = []
    for prop in qs:
        result.append({
            'id': prop.id,
            'code': prop.code,
            'name': prop.name,
            'program_id': prop.program_id_id,
            'program_name': prop.program_id.name if prop.program_id else '',
            'material': prop.material,
            'status': prop.status,
            'location': prop.location,
            'created_at': prop.created_at,
            'updated_at': prop.updated_at,
        })
    return result


@router.get('/{prop_id}', response=PropOut)
def get_prop(request, prop_id: int):
    try:
        prop = Prop.objects.select_related('program_id').get(id=prop_id)
    except Prop.DoesNotExist:
        raise HttpError(404, '道具不存在')
    return {
        'id': prop.id,
        'code': prop.code,
        'name': prop.name,
        'program_id': prop.program_id_id,
        'program_name': prop.program_id.name if prop.program_id else '',
        'material': prop.material,
        'status': prop.status,
        'location': prop.location,
        'created_at': prop.created_at,
        'updated_at': prop.updated_at,
    }


@router.post('', response=PropOut)
def create_prop(request, data: PropIn):
    if Prop.objects.filter(code=data.code).exists():
        raise HttpError(400, '道具编号已存在')
    prop = Prop.objects.create(**data.dict())
    prop = Prop.objects.select_related('program_id').get(id=prop.id)
    return {
        'id': prop.id,
        'code': prop.code,
        'name': prop.name,
        'program_id': prop.program_id_id,
        'program_name': prop.program_id.name if prop.program_id else '',
        'material': prop.material,
        'status': prop.status,
        'location': prop.location,
        'created_at': prop.created_at,
        'updated_at': prop.updated_at,
    }


@router.put('/{prop_id}', response=PropOut)
def update_prop(request, prop_id: int, data: PropIn):
    try:
        prop = Prop.objects.get(id=prop_id)
    except Prop.DoesNotExist:
        raise HttpError(404, '道具不存在')
    if data.code != prop.code and Prop.objects.filter(code=data.code).exists():
        raise HttpError(400, '道具编号已存在')
    for attr, value in data.dict().items():
        setattr(prop, attr, value)
    prop.save()
    prop = Prop.objects.select_related('program_id').get(id=prop.id)
    return {
        'id': prop.id,
        'code': prop.code,
        'name': prop.name,
        'program_id': prop.program_id_id,
        'program_name': prop.program_id.name if prop.program_id else '',
        'material': prop.material,
        'status': prop.status,
        'location': prop.location,
        'created_at': prop.created_at,
        'updated_at': prop.updated_at,
    }


@router.delete('/{prop_id}')
def delete_prop(request, prop_id: int):
    try:
        prop = Prop.objects.get(id=prop_id)
    except Prop.DoesNotExist:
        raise HttpError(404, '道具不存在')
    prop.delete()
    return {'success': True}
