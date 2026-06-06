from ninja import Router
from ninja.errors import HttpError
from django.shortcuts import get_object_or_404

from .models import Program
from .schemas import ProgramIn, ProgramOut
from apps.auth_app.auth import JWTAuth

router = Router(tags=['剧目管理'], auth=JWTAuth())


@router.get('', response=list[ProgramOut])
def list_programs(request):
    return Program.objects.all()


@router.get('/{program_id}', response=ProgramOut)
def get_program(request, program_id: int):
    return get_object_or_404(Program, id=program_id)


@router.post('', response=ProgramOut)
def create_program(request, data: ProgramIn):
    if Program.objects.filter(name=data.name).exists():
        raise HttpError(400, '剧目名称已存在')
    program = Program.objects.create(**data.dict())
    return program


@router.put('/{program_id}', response=ProgramOut)
def update_program(request, program_id: int, data: ProgramIn):
    program = get_object_or_404(Program, id=program_id)
    if data.name != program.name and Program.objects.filter(name=data.name).exists():
        raise HttpError(400, '剧目名称已存在')
    for attr, value in data.dict().items():
        setattr(program, attr, value)
    program.save()
    return program


@router.delete('/{program_id}')
def delete_program(request, program_id: int):
    program = get_object_or_404(Program, id=program_id)
    program.delete()
    return {'success': True}
