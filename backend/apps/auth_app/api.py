from django.conf import settings
from django.contrib.auth import authenticate
from ninja import Router
from ninja.errors import HttpError

from .schemas import LoginSchema, LoginResponseSchema, UserInfoSchema
from .auth import JWTAuth, generate_token

router = Router(tags=['认证'])


@router.post('/login', response=LoginResponseSchema)
def login(request, data: LoginSchema):
    user = authenticate(username=data.username, password=data.password)
    if not user:
        raise HttpError(401, '用户名或密码错误')
    if not user.is_active:
        raise HttpError(403, '账户已被禁用')
    token = generate_token(user)
    expires_in = settings.JWT_EXPIRATION_HOURS * 3600
    return {
        'token': token,
        'token_type': 'Bearer',
        'expires_in': expires_in,
    }


@router.get('/me', response=UserInfoSchema, auth=JWTAuth())
def get_current_user(request):
    user = request.auth
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'first_name': user.first_name,
        'last_name': user.last_name,
    }
