import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from ninja.security import HttpBearer
from ninja.errors import HttpError

User = get_user_model()


def generate_token(user):
    payload = {
        'user_id': user.id,
        'username': user.username,
        'exp': datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRATION_HOURS),
        'iat': datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


def verify_token(token):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get('user_id')
        if not user_id:
            return None
        try:
            user = User.objects.get(id=user_id, is_active=True)
            return user
        except User.DoesNotExist:
            return None
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        user = verify_token(token)
        if not user:
            raise HttpError(401, '无效或已过期的认证令牌')
        request.auth = user
        return token
