from ninja import Router, Query
from ninja.errors import HttpError
from typing import List, Optional

from .models import Vehicle
from .schemas import VehicleIn, VehicleOut
from apps.auth_app.auth import JWTAuth

router = Router(tags=['车辆管理'], auth=JWTAuth())


@router.get('', response=List[VehicleOut])
def list_vehicles(request, status: Optional[str] = Query(None)):
    queryset = Vehicle.objects.all()
    if status:
        queryset = queryset.filter(status=status)
    return list(queryset)


@router.get('/{vehicle_id}', response=VehicleOut)
def get_vehicle(request, vehicle_id: int):
    try:
        return Vehicle.objects.get(id=vehicle_id)
    except Vehicle.DoesNotExist:
        raise HttpError(404, '车辆不存在')


@router.post('', response=VehicleOut)
def create_vehicle(request, data: VehicleIn):
    if Vehicle.objects.filter(code=data.code).exists():
        raise HttpError(400, '车辆编号已存在')
    if data.current_load > data.capacity:
        raise HttpError(400, '当前装载量不能超过承载容量')
    vehicle = Vehicle.objects.create(**data.dict())
    return vehicle


@router.put('/{vehicle_id}', response=VehicleOut)
def update_vehicle(request, vehicle_id: int, data: VehicleIn):
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
    except Vehicle.DoesNotExist:
        raise HttpError(404, '车辆不存在')
    if data.current_load > data.capacity:
        raise HttpError(400, '当前装载量不能超过承载容量')
    if data.code != vehicle.code and Vehicle.objects.filter(code=data.code).exists():
        raise HttpError(400, '车辆编号已存在')
    for attr, value in data.dict().items():
        setattr(vehicle, attr, value)
    vehicle.save()
    return vehicle


@router.delete('/{vehicle_id}')
def delete_vehicle(request, vehicle_id: int):
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
    except Vehicle.DoesNotExist:
        raise HttpError(404, '车辆不存在')
    vehicle.delete()
    return {'success': True}
